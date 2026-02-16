import hashlib
from urllib.parse import urlparse, urlunparse


def normalize_link(url: str) -> str:
    parsed = urlparse((url or "").strip())
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))


def hash_link(normalized_url: str) -> str:
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()
