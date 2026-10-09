"""The fourteen default apps (Javier's list, D-2/D-4) and the common file types (D-2).

Each default app has the types that say what it is for (`main`: an app must declare one of them in
its desktop entry to be offered) and its usual file types (`types`, by extension), which File Types
can move between default apps. A file type's MIME name is what the system and mimeapps.list use.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Role:
    key: str
    title: str
    main: tuple[str, ...]                     # MIME types / URL schemes that define the job
    types: tuple[str, ...] = field(default_factory=tuple)   # extensions it starts with (D-4 question 5)
    category: str = ""                        # a desktop-entry category that also qualifies (terminals)


ROLES = [
    Role("web", "Web Browser", ("x-scheme-handler/http", "x-scheme-handler/https"), (".html", ".htm", ".xhtml")),
    Role("email", "Email Client", ("x-scheme-handler/mailto",), (".eml",)),
    Role("calendar", "Calendar", ("text/calendar", "x-scheme-handler/webcal"), ()),
    Role("phone", "Phone Numbers", ("x-scheme-handler/tel", "x-scheme-handler/callto"), ()),
    Role("image", "Image Viewer", ("image/png", "image/jpeg"),
         (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".tif", ".tiff")),
    Role("music", "Music Player", ("audio/mpeg", "audio/flac", "audio/ogg"),
         (".mp3", ".flac", ".ogg", ".opus", ".wav", ".m4a")),
    Role("video", "Video Player", ("video/mp4", "video/x-matroska", "video/webm"),
         (".mp4", ".mkv", ".webm", ".avi", ".mov")),
    Role("text", "Text Editor", ("text/plain",),
         (".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".conf", ".ini", ".log", ".sh", ".py", ".js", ".css", ".xml")),
    Role("pdf", "PDF Viewer", ("application/pdf",), (".pdf",)),
    Role("files", "File Manager", ("inode/directory",), ()),
    Role("terminal", "Terminal Emulator", (), (), category="TerminalEmulator"),
    Role("archive", "Archive Manager", ("application/zip", "application/x-7z-compressed", "application/x-tar"),
         (".zip", ".7z", ".tar", ".gz", ".xz", ".rar")),
    Role("map", "Map", ("x-scheme-handler/geo",), ()),
    Role("office", "Office Suite",
         ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "application/vnd.oasis.opendocument.text"),
         (".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".doc", ".xls", ".ppt")),
]
BY_KEY = {r.key: r for r in ROLES}

# The common file types (D-2: "a list of the most common file types, to keep it simple"):
# extension → (what it is, its MIME type).
FILE_TYPES = {
    ".html": ("web page", "text/html"), ".htm": ("web page", "text/html"), ".xhtml": ("web page", "application/xhtml+xml"),
    ".eml": ("email message", "message/rfc822"),
    ".ics": ("calendar event", "text/calendar"),
    ".png": ("PNG picture", "image/png"), ".jpg": ("JPEG picture", "image/jpeg"), ".jpeg": ("JPEG picture", "image/jpeg"),
    ".gif": ("GIF picture", "image/gif"), ".webp": ("WebP picture", "image/webp"), ".svg": ("SVG drawing", "image/svg+xml"),
    ".bmp": ("BMP picture", "image/bmp"), ".ico": ("icon", "image/vnd.microsoft.icon"), ".tif": ("TIFF picture", "image/tiff"),
    ".tiff": ("TIFF picture", "image/tiff"), ".heic": ("phone photo", "image/heif"), ".avif": ("AVIF picture", "image/avif"),
    ".mp3": ("MP3 song", "audio/mpeg"), ".flac": ("FLAC song", "audio/flac"), ".ogg": ("Ogg sound", "audio/ogg"),
    ".opus": ("Opus sound", "audio/x-opus+ogg"), ".wav": ("WAV sound", "audio/x-wav"), ".m4a": ("M4A song", "audio/mp4"),
    ".mp4": ("MP4 video", "video/mp4"), ".mkv": ("MKV video", "video/x-matroska"), ".webm": ("WebM video", "video/webm"),
    ".avi": ("AVI video", "video/x-msvideo"), ".mov": ("QuickTime video", "video/quicktime"),
    ".txt": ("plain text", "text/plain"), ".md": ("Markdown", "text/markdown"), ".json": ("JSON", "application/json"),
    ".yaml": ("YAML", "application/x-yaml"), ".yml": ("YAML", "application/x-yaml"), ".toml": ("TOML", "application/toml"),
    ".conf": ("settings file", "text/plain"), ".ini": ("settings file", "text/plain"), ".log": ("log", "text/x-log"),
    ".sh": ("shell script", "application/x-shellscript"), ".py": ("Python", "text/x-python"),
    ".js": ("JavaScript", "application/javascript"), ".css": ("CSS", "text/css"), ".xml": ("XML", "application/xml"),
    ".csv": ("spreadsheet text", "text/csv"), ".rtf": ("rich text", "application/rtf"),
    ".pdf": ("PDF document", "application/pdf"), ".epub": ("e-book", "application/epub+zip"),
    ".zip": ("ZIP archive", "application/zip"), ".7z": ("7-Zip archive", "application/x-7z-compressed"),
    ".tar": ("tar archive", "application/x-tar"), ".gz": ("gzip archive", "application/gzip"),
    ".xz": ("xz archive", "application/x-xz"), ".rar": ("RAR archive", "application/vnd.rar"),
    ".iso": ("disc image", "application/x-cd-image"), ".torrent": ("torrent", "application/x-bittorrent"),
    ".ttf": ("font", "font/ttf"), ".otf": ("font", "font/otf"), ".srt": ("subtitles", "application/x-subrip"),
    ".docx": ("Word document", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ".xlsx": ("Excel sheet", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ".pptx": ("PowerPoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    ".odt": ("document", "application/vnd.oasis.opendocument.text"),
    ".ods": ("spreadsheet", "application/vnd.oasis.opendocument.spreadsheet"),
    ".odp": ("presentation", "application/vnd.oasis.opendocument.presentation"),
    ".doc": ("old Word document", "application/msword"), ".xls": ("old Excel sheet", "application/vnd.ms-excel"),
    ".ppt": ("old PowerPoint", "application/vnd.ms-powerpoint"),
}


def default_pools() -> dict[str, list[str]]:
    """Each default app's usual file types, the first time (D-4, 5)."""
    return {r.key: [e for e in r.types if e in FILE_TYPES] for r in ROLES}
