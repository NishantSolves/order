import logging, sys, config

def get_logger(name: str) -> logging.Logger:
    lvl = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(stream=sys.stdout, level=lvl, format=fmt, force=True)
    return logging.getLogger(name)
