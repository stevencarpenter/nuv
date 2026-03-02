import logging
import sys

LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def configure(level: str = "WARNING") -> None:
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        stream=sys.stderr,
    )
    for name in ("py4j", "pyspark", "org.apache.spark"):
        logging.getLogger(name).setLevel(logging.WARNING)
