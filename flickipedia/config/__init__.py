import logging

global log

# NullHandler was added in Python 3.1.
try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Add a do-nothing NullHandler to the module logger to prevent "No handlers
# could be found" errors. The calling code can still add other, more useful
# handlers, or otherwise configure logging.
log = logging.getLogger(__name__)
log.addHandler(NullHandler())


def set_log(args, out, err, level_override=None):
    """
    Configures a logger and returns it.

    :param args: command line args
    :param out: stdout
    :param err: stderr
    """

    if not level_override:
        # Default to info if args not present
        if hasattr(args, 'verbose') and hasattr(
            args, 'silent') and hasattr(args, 'quiet'):
            level = logging.WARNING - ((args.verbose - args.quiet) * 10)
            if args.silent:
                level = logging.CRITICAL + 1
        else:
            level = logging.INFO
    else:
        level = level_override

    log_format = "%(asctime)s %(levelname)-8s %(message)s"
    handler = logging.StreamHandler(err)
    handler.setFormatter(logging.Formatter(fmt=log_format,
                         datefmt='%b-%d %H:%M:%S'))

    log = logging.getLogger(__name__)
    log.addHandler(handler)
    log.setLevel(level)

    return log