try:
    from config import config
except ImportError:
    pass

try:
    CONFIG = config.CONFIG
except NameError:
    CONFIG = dict(
        DSN='postgresql://postgres:password@localhost:5433/postgres',
        MAINTENANCE=False,
        DEV_MODE=True,
    )
