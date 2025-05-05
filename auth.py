"""
Refreshes eBay user access tokens transparently.
"""
import base64, time, requests
import config
from logger import get_logger

log = get_logger("auth")

_TOKEN: str | None = None
_EXPIRY = 0

def _endpoint(path: str) -> str:
    base = "https://api.ebay.com" if config.EBAY_ENV == "PROD" \
           else "https://api.sandbox.ebay.com"
    return f"{base}{path}"

def get_user_token() -> str:
    global _TOKEN, _EXPIRY
    if _TOKEN and (_EXPIRY - time.time() > 60):
        return _TOKEN

    log.info("Refreshing eBay user access token")
    b64 = base64.b64encode(
        f"{config.EBAY_CLIENT_ID}:{config.EBAY_CLIENT_SECRET}".encode()
    ).decode()

    try:
        r = requests.post(
            _endpoint("/identity/v1/oauth2/token"),
            headers={
                "Authorization": f"Basic {b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": config.EBAY_REFRESH_TOKEN,
                "scope": "https://api.ebay.com/oauth/api_scope/sell.feed.readonly"
            },
            timeout=30
        )
        r.raise_for_status()
    except requests.RequestException as e:
        log.exception("OAuth refresh failed")
        raise RuntimeError("Unable to refresh eBay token") from e

    data = r.json()
    _TOKEN  = data["access_token"]
    _EXPIRY = time.time() + int(data["expires_in"])
    log.debug("Token refreshed, expires in %s seconds", data["expires_in"])
    return _TOKEN
