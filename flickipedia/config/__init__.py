import logging

FORMAT="%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


def log_set_level(level):
    """ Set logging level """
    log.setLevel(level)