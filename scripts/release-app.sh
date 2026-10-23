#!/usr/bin/env bash
# Forge Suite · one app's release files, from its signed tag (the per-app release recipe, docs/RELEASE-RECIPE.md).
#
#   scripts/release-app.sh <app> <X.Y.Z>             build dist/<app>-X.Y.Z/: the tarball, SHA256SUMS, both signed;
#                                                    prints the GitHub command — it never publishes by itself
#   scripts/release-app.sh <app> <X.Y.Z> --no-sign  the same, unsigned (a dry run: no password box)
#   scripts/release-app.sh <app> <X.Y.Z> --verify   rebuild a PUBLISHED release and check it against its files
#
# The tarball is `git archive` of the app's folder at its tag, gzip -n, with every file's time pinned to the
# tag's commit time (--mtime). Without the pin each build is stamped with the moment it ran, so a published
# file can never be rebuilt to check it (found 2026-10-22 on nightForge 1.1.0: same files, other times).
# Logs to logs/release-<app>-<X.Y.Z>-<time>.log.
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
app=${1:-}; ver=${2:-}; mode=${3:-build}
if [[ -z "$app" || ! "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  sed -n 2,13p "$0" | sed 's/^# \{0,1\}//'; exit 2
fi
tag="$app-v$ver"; name="$app-$ver"
mkdir -p "$REPO/logs"
log="$REPO/logs/release-$name-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$log") 2>&1

echo
echo "── Forge Suite · release files for $app $ver ──"
echo
cd "$REPO"
[ -d "$app" ] || { echo "  no folder '$app' in forge-suite"; exit 1; }
git rev-parse -q --verify "refs/tags/$tag" >/dev/null || { echo "  no tag $tag (tag it first: git tag -s $tag -m …)"; exit 1; }
if git tag -v "$tag" >/dev/null 2>&1; then echo "  tag $tag: signed, signature good"
else echo "  tag $tag: NOT signed or the signature doesn't check — stop"; exit 1; fi

when=$(git log -1 --format=%cI "$tag")
build() {   # $1 = output folder
  git archive --mtime="$when" --prefix="$name/" "$tag:$app" | gzip -n -9 > "$1/$name.tar.gz"
  (cd "$1" && sha256sum "$name.tar.gz" > "$name.SHA256SUMS")
}

case "$mode" in
  build|--no-sign)
    out="$REPO/dist/$name"; rm -rf "$out"; mkdir -p "$out"
    build "$out"
    echo "  tarball:   $out/$name.tar.gz  (files dated $when, the tag's commit)"
    echo "  checksum:  $(cut -d' ' -f1 "$out/$name.SHA256SUMS")"
    if [ "$mode" = build ]; then
      gpg --armor --detach-sign "$out/$name.tar.gz"
      gpg --armor --detach-sign "$out/$name.SHA256SUMS"
      gpg --verify "$out/$name.tar.gz.asc" "$out/$name.tar.gz" 2>&1 | grep -q 'Good signature' \
        && echo "  signed:    both files, signatures good" || { echo "  a signature does not check — stop"; exit 1; }
      echo
      echo "  Next, by hand (it publishes): the release notes in a file, then"
      echo "    gh release create $tag -R jetomev/forge-suite --title \"<App> $ver — <tagline>\" --notes-file <notes> \\"
      echo "      $out/$name.tar.gz $out/$name.tar.gz.asc $out/$name.SHA256SUMS $out/$name.SHA256SUMS.asc"
      echo "  (forgekit, the shared library: add --latest=false. An app takes Latest: the newest app release, decided 2026-10-22.)"
    else
      echo "  not signed (--no-sign): a dry run"
    fi
    ;;
  --verify)
    tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
    mkdir "$tmp/pub" "$tmp/new"
    gh release download "$tag" -R jetomev/forge-suite -D "$tmp/pub" -p "$name.*" >/dev/null
    (cd "$tmp/pub" && gpg --verify "$name.SHA256SUMS.asc" "$name.SHA256SUMS" 2>&1 | grep -q 'Good signature') \
      && echo "  published checksums: signed, signature good" || echo "  published checksums: signature MISSING or BAD"
    (cd "$tmp/pub" && sha256sum -c --quiet "$name.SHA256SUMS") && echo "  published tarball: matches its checksum"
    build "$tmp/new"
    if cmp -s "$tmp/pub/$name.tar.gz" "$tmp/new/$name.tar.gz"; then
      echo "  rebuilt from the tag: byte for byte the same — this release is reproducible"
    else
      mkdir "$tmp/a" "$tmp/b"; tar xzf "$tmp/pub/$name.tar.gz" -C "$tmp/a"; tar xzf "$tmp/new/$name.tar.gz" -C "$tmp/b"
      if diff -r "$tmp/a" "$tmp/b" >/dev/null; then
        echo "  rebuilt from the tag: the same files and contents, other file times"
        echo "    (built before the pinned-time recipe; from now on releases rebuild byte for byte)"
      else
        echo "  rebuilt from the tag: the CONTENTS DIFFER — the published file is not what the tag holds"; exit 1
      fi
    fi
    ;;
  *) echo "  unknown mode '$mode'"; exit 2 ;;
esac
echo
echo "  Log: $log"
echo "  Done."
