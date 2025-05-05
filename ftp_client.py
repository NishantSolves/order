"""
Simple FTP uploader.
"""
import ftplib, os, pathlib
import config
from logger import get_logger

log = get_logger("ftp")

def upload(local_path: str):
    fname = pathlib.Path(local_path).name
    log.info("Uploading %s → ftp://%s%s", fname, config.FTP_HOST, config.FTP_PATH)

    try:
        with ftplib.FTP() as ftp:
            ftp.connect(config.FTP_HOST, config.FTP_PORT, timeout=30)
            ftp.login(config.FTP_USER, config.FTP_PASS)
            ftp.cwd(config.FTP_PATH)
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {fname}", f)
    except Exception as e:
        log.exception("FTP upload failed")
        raise
    else:
        log.info("FTP upload successful")
