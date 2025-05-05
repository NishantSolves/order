"""
Cron entry‑point.  Runs hourly.
"""
import datetime as dt, sys
from logger import get_logger
import ebay_feed, transform, ftp_client

log = get_logger("cron")

def main() -> int:
    try:
        # window = previous hour
        end = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        start = end - dt.timedelta(hours=1)

        task_id = ebay_feed.create_order_task(start, end)
        file_id, _ = ebay_feed.wait_for_task(task_id)
        tsv_path = ebay_feed.download_file(file_id)

        csv_path = transform.transform(tsv_path)
        if csv_path:
            ftp_client.upload(csv_path)
        else:
            log.info("Nothing to upload")

        return 0
    except Exception:
        log.exception("Hourly job failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
