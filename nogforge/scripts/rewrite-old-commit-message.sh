#!/usr/bin/env bash
# nogForge · reword ONE old commit message (f16c086, 2026-07-30), which names the maintainer's book persona —
# a name that lives only in the book's own projects. The maintainer asked for it on 2026-10-03 ("remove it")
# and again on 2026-10-22 ("fix"). It rewrites history, so it is run by the maintainer, in steps:
#
#   scripts/rewrite-old-commit-message.sh --dry-run   on a throwaway copy, unsigned: proves every check
#   scripts/rewrite-old-commit-message.sh             here, locally: rewrites + re-signs; pushes nothing
#   PUSH=yes scripts/rewrite-old-commit-message.sh --push    then: force-pushes main and the 8 tags
#
# What changes: only that commit's message loses " (<name>, 2026-07-30)". Every later commit gets a new
# identity, so all of them are re-signed and every release tag is re-created on its new commit, signed,
# with its old message and date. Files never change: the script STOPS unless every commit's content and
# every tag's content are identical before and after. The release FILES on GitHub (what the AUR downloads)
# are uploads, untouched by this. The old history is kept: a bundle in backups/, the branch
# pre-rewrite-<time>, and the old tags under refs/pre-rewrite/. Logs to logs/rewrite-<time>.log.
set -euo pipefail

OLD=f16c086219aea72735947f1e2e7243c3b2083f73
REPO=$(cd "$(dirname "$0")/.." && pwd)
mode=${1:-local}
ts=$(date +%Y%m%d-%H%M%S)
mkdir -p "$REPO/logs"
log="$REPO/logs/rewrite-$ts.log"
exec > >(tee "$log") 2>&1
say() { printf '  %s\n' "$*"; }
stop() { printf '\n  STOPPED: %s\n  Nothing was pushed. Log: %s\n' "$*" "$log"; exit 1; }

echo
echo "── nogForge · reword one old commit message ──"
echo

if [ "$mode" = --push ]; then
  cd "$REPO"
  [ "${PUSH:-}" = yes ] || stop "pushing rewrites GitHub's history: run it as  PUSH=yes $0 --push"
  git log --format=%B main | grep -q "$(cat .git/rewrite-name 2>/dev/null || echo '@@none@@')" \
    && stop "main still carries the old message: run the local step first"
  old_remote=$(git rev-parse origin/main)
  git push --force-with-lease="main:$old_remote" origin main
  git push --force origin $(git tag -l 'v*')
  say "pushed: main and $(git tag -l 'v*' | wc -l) tags"
  say "GitHub's release files are untouched; check one against the AUR recipe:"
  say "  gh release download v1.5.0 -R jetomev/nogforge -p 'nogforge-1.5.0.tar.gz' -O - | sha256sum"
  echo; say "Log: $log"; say "Done."; exit 0
fi

if [ "$mode" = --dry-run ]; then
  work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
  git clone -q --no-local "$REPO" "$work/repo"
  cd "$work/repo"; git fetch -q --tags
  sign=(--no-gpg-sign); tagsign=(-a)
  say "a throwaway copy, unsigned: $work/repo"
else
  cd "$REPO"
  [ -z "$(git status --porcelain)" ] || stop "uncommitted changes here; commit or set them aside first"
  [ "$(git branch --show-current)" = main ] || stop "not on main"
  git fetch -q origin
  [ "$(git rev-parse main)" = "$(git rev-parse origin/main)" ] || stop "main differs from GitHub's; pull or push first"
  sign=(--gpg-sign); tagsign=(-s)
fi

git cat-file -e "$OLD^{commit}" 2>/dev/null || stop "commit $OLD not found (already rewritten?)"
msg=$(git log -1 --format=%B "$OLD")
name=$(sed -nE '1s/.*\(([A-Z][a-z]+), 2026-07-30\).*/\1/p' <<<"$msg")
[ -n "$name" ] || stop "the commit's first line doesn't have the (Name, 2026-07-30) mark"
new_msg=$(sed -E "1s/ \($name, 2026-07-30\)/ (2026-07-30)/" <<<"$msg")
say "the commit:  $(head -1 <<<"$msg" | sed "s/$name/<name>/")"
say "becomes:     $(head -1 <<<"$new_msg")"

before=$(git rev-list --count main)
mapfile -t olds < <(git rev-list --reverse "$OLD^..main")
declare -A tagtree tagmsg tagdate tagtarget
for t in $(git tag -l 'v*'); do
  tagtree[$t]=$(git rev-parse "$t^{tree}")
  tagtarget[$t]=$(git rev-parse "$t^{commit}")
  tagmsg[$t]=$(git for-each-ref "refs/tags/$t" --format='%(contents:subject)%0a%0a%(contents:body)')
  tagdate[$t]=$(git for-each-ref "refs/tags/$t" --format='%(taggerdate:iso-strict)')
done
say "history: $before commits, ${#olds[@]} from that commit on, $(git tag -l 'v*' | wc -l) release tags"

# keep the old history (move aside, never delete)
if [ "$mode" != --dry-run ]; then
  mkdir -p "$REPO/backups"
  git bundle create -q "$REPO/backups/nogforge-before-rewrite-$ts.bundle" --all
  git bundle verify -q "$REPO/backups/nogforge-before-rewrite-$ts.bundle" >/dev/null
  say "backup:  backups/nogforge-before-rewrite-$ts.bundle (verified)"
fi
git branch "pre-rewrite-$ts" main
for t in $(git tag -l 'v*'); do git update-ref "refs/pre-rewrite/$t" "refs/tags/$t"; done
say "kept:    branch pre-rewrite-$ts, old tags under refs/pre-rewrite/"

# the reword, then the rest replayed on top (each re-signed in the real run)
git checkout -q --detach "$OLD"
GIT_COMMITTER_DATE="$(git log -1 --format=%cI "$OLD")" git commit -q --amend "${sign[@]}" -m "$new_msg"
git rebase -q "${sign[@]}" --committer-date-is-author-date --onto HEAD "$OLD" main
# the history before that commit is untouched and the count is the same, so the last N commits are the new ones
mapfile -t news < <(git rev-list --reverse main | tail -n ${#olds[@]})

# the gates: same count, same content commit by commit, the name gone
[ "$(git rev-list --count main)" = "$before" ] || stop "the commit count changed ($before → $(git rev-list --count main))"
declare -A newof
for i in "${!olds[@]}"; do
  [ "$(git rev-parse "${olds[$i]}^{tree}")" = "$(git rev-parse "${news[$i]}^{tree}")" ] \
    || stop "commit $((i+1)) of ${#olds[@]}: its content differs after the rewrite"
  newof[${olds[$i]}]=${news[$i]}
done
say "content: all ${#olds[@]} commits identical, one by one"
git log --format=%B main | grep -qw "$name" && stop "the name is still in a commit message"
say "message: the name is in no commit message on main"

# the tags, re-created on their new commits with their old message and date
for t in $(git tag -l 'v*'); do
  target=${newof[${tagtarget[$t]}]:-}
  [ -n "$target" ] || stop "tag $t pointed outside the rewritten range"
  GIT_COMMITTER_DATE="${tagdate[$t]}" git tag -f "${tagsign[@]}" "$t" "$target" -m "${tagmsg[$t]}"
  [ "$(git rev-parse "$t^{tree}")" = "${tagtree[$t]}" ] || stop "tag $t: its content differs"
done
say "tags:    $(git tag -l 'v*' | wc -l) re-created, each holding exactly what it held"

if [ "$mode" != --dry-run ]; then
  bad=$(git log --format='%G?' "$(git rev-parse "${news[0]}")^..main" | grep -vc '^G' || true)
  [ "$bad" = 0 ] || stop "$bad rewritten commit(s) without a good signature"
  for t in $(git tag -l 'v*'); do git tag -v "$t" >/dev/null 2>&1 || stop "tag $t: signature doesn't check"; done
  say "signed:  every rewritten commit and every tag, signatures good"
  echo "$name" > .git/rewrite-name
  echo
  say "Local only, nothing pushed. Look it over (git log, gitk); to undo: git reset --hard pre-rewrite-$ts"
  say "and restore the tags from refs/pre-rewrite/. When happy:  PUSH=yes $0 --push"
fi
echo; say "Log: $log"; say "Done."
