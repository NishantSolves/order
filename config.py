"""
Centralised environment handling.
Raises clear errors if anything critical is missing.
"""
import os

def _must_get(var: str) -> str:
    val = os.getenv(var)
    if not val:
        raise RuntimeError(f"Missing required env var: {var}")
    return val

# eBay creds
EBAY_CLIENT_ID       = _must_get("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET   = _must_get("EBAY_CLIENT_SECRET")
EBAY_REFRESH_TOKEN   = _must_get("EBAY_REFRESH_TOKEN")
EBAY_ENV             = os.getenv("EBAY_ENV", "PROD").upper()   # default prod

# FTP creds
FTP_HOST   = _must_get("FTP_HOST")
FTP_PORT   = int(os.getenv("FTP_PORT", "21"))
FTP_USER   = _must_get("FTP_USER")
FTP_PASS   = _must_get("FTP_PASS")
FTP_PATH   = os.getenv("FTP_PATH", "/")

# Misc
LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")
