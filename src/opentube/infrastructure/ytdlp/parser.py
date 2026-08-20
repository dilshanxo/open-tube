from typing import Any

from opentube.domain.models import MediaFormat


def parse_duration(raw: Any) -> int | None:
    if isinstance(raw, (int, float)):
        return int(raw)
    try:
        if raw is not None:
            return int(float(raw))
    except (ValueError, TypeError):
        pass
    return None

def parse_formats(raw_formats: list[dict[str, Any]]) -> list[MediaFormat]:
    parsed = []
    for f in raw_formats:
        fmt_id = f.get("format_id")
        if not fmt_id:
            continue
            
        ext = f.get("ext", "")
        if ext in ("mhtml", "weba"):
            continue

        quality = f.get("format_note") or f.get("resolution") or ""
        if not quality and f.get("height"):
            quality = f"{f.get('height')}p"
        
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")
        
        is_audio_only = (vcodec == "none") or (vcodec is None and acodec is not None and acodec != "none" and not f.get("height"))

        fps = f.get("fps")
        filesize = f.get("filesize") or f.get("filesize_approx")
        abr = f.get("abr")
        tbr = f.get("tbr")

        fmt = MediaFormat(
            format_id=str(fmt_id),
            ext=str(ext),
            quality=str(quality) if quality else "unknown",
            fps=int(fps) if fps else None,
            vcodec=str(vcodec) if vcodec and vcodec != "none" else None,
            acodec=str(acodec) if acodec and acodec != "none" else None,
            filesize=int(filesize) if filesize else None,
            is_audio_only=bool(is_audio_only),
            abr=float(abr) if abr else None,
            tbr=float(tbr) if tbr else None
        )
        parsed.append(fmt)
    return parsed
