from urllib.parse import urlsplit


def normalize_hub_url(value):
    """Normalize HTTPS origin and trailing slashes; preserve the path prefix."""
    if not isinstance(value, str) or not value or not value.isascii():
        raise ValueError("Invalid Hub URL.")
    if any(c.isspace() or ord(c) < 32 for c in value) or "\\" in value:
        raise ValueError("Invalid Hub URL.")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or "?" in value
        or "#" in value
        or "%" in parsed.netloc
        or "%" in parsed.path
        or any(part in (".", "..") for part in parsed.path.split("/"))
    ):
        raise ValueError("Invalid Hub URL.")
    port = parsed.port
    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    authority = host if port in (None, 443) else f"{host}:{port}"
    return f"https://{authority}{parsed.path.rstrip('/')}"
