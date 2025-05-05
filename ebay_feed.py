"""
Helpers for Sell Feed API (order report).
"""
import time, datetime as dt, requests, tempfile, gzip, shutil, os
from typing import Tuple
import auth, config
from logger import get_logger

log = get_logger("ebay_feed")

def _endpoint(path: str) -> str:
    base = "https://api.ebay.com" if config.EBAY_ENV == "PROD" \
           else "https://api.sandbox.ebay.com"
    return f"{base}{path}"

def create_order_task(start: dt.datetime, end: dt.datetime) -> str:
    log.info("Creating order task %s → %s", start, end)
    body = {
        "feedType": "LMS_ORDER_REPORT",
        "filterCriteria": {
            "creationDateRange": {
                "from": start.isoformat() + "Z",
                "to":   end.isoformat()   + "Z"
            }
        }
    }
    r = requests.post(
        _endpoint("/sell/feed/v1/order_task"),
        json=body,
        headers={
            "Authorization": f"Bearer {auth.get_user_token()}",
            "Content-Type": "application/json"
        },
        timeout=30
    )
    r.raise_for_status()
    task_id = r.json()["taskId"]
    log.debug("Created task_id=%s", task_id)
    return task_id

def wait_for_task(task_id: str, poll: int = 10, timeout: int = 300) -> Tuple[str,str]:
    """
    Polls until COMPLETED. Returns (file_id, file_status).
    """
    log.info("Polling task %s", task_id)
    end = time.time() + timeout
    status = ""
    while time.time() < end:
        r = requests.get(
            _endpoint(f"/sell/feed/v1/order_task/{task_id}"),
            headers={"Authorization": f"Bearer {auth.get_user_token()}"},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
        status = data["status"]
        if status == "COMPLETED":
            return data["fileReferenceId"], status
        elif status in ("FAILED", "ABORTED"):
            raise RuntimeError(f"Task {task_id} ended in {status}")
        time.sleep(poll)
    raise TimeoutError(f"Task {task_id} did not finish within {timeout}s")

def download_file(file_id: str) -> str:
    """
    Returns path to unzipped TSV file.
    """
    log.info("Downloading feed file %s", file_id)
    r = requests.get(
        _endpoint(f"/sell/feed/v1/file/{file_id}"),
        headers={"Authorization": f"Bearer {auth.get_user_token()}"},
        stream=True,
        timeout=60
    )
    r.raise_for_status()

    tmp_gz = tempfile.NamedTemporaryFile(delete=False, suffix=".gz")
    for chunk in r.iter_content(chunk_size=8192):
        tmp_gz.write(chunk)
    tmp_gz.close()

    out_path = tmp_gz.name[:-3] + ".tsv"
    with gzip.open(tmp_gz.name, "rb") as src, open(out_path, "wb") as dst:
        shutil.copyfileobj(src, dst)
    os.unlink(tmp_gz.name)
    log.debug("File downloaded to %s", out_path)
    return out_path
