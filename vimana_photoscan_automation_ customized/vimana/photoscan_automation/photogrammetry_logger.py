import logging
import sys
import os.path


def setup_logging(folder=".", logfile="photogrammetry_workflow.log"):
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # root.setLevel(logging.DEBUG)

    handler = logging.FileHandler(os.path.join(folder, logfile))
    handler.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logformat = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    formatter = logging.Formatter(logformat)
    ch.setFormatter(formatter)
    handler.setFormatter(formatter)
    root.addHandler(ch)
    root.addHandler(handler)

