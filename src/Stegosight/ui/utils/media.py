from __future__ import annotations


def infer_media_type_from_suffix(suffix: str) -> str | None:
    suffix = (suffix or "").lower()
    image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    audio_exts = {".wav", ".mp3", ".flac", ".aac", ".ogg", ".wma"}
    video_exts = {
        ".avi",
        ".mp4",
        ".mkv",
        ".mov",
        ".ogv",
        ".wmv",
        ".m4v",
        ".mpeg",
        ".mpg",
    }

    if suffix in image_exts:
        return "image"
    if suffix in audio_exts:
        return "audio"
    if suffix in video_exts:
        return "video"
    return None


__all__ = ["infer_media_type_from_suffix"]
