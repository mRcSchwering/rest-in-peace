"""
Adapted from tiangolo and Carsten's `logconfig_dict`
https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/docker-images/gunicorn_conf.py
"""
import json
import multiprocessing
import os
from app.config import HOST, PORT, LOG_LEVEL

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
max_workers_str = os.getenv("MAX_WORKERS")
use_max_workers = None
if max_workers_str:
    use_max_workers = int(max_workers_str)
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

bind_env = os.getenv("BIND", None)
if bind_env:
    use_bind = bind_env
else:
    use_bind = HOST + ":" + PORT

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)
    if use_max_workers:
        web_concurrency = min(web_concurrency, use_max_workers)

accesslog_var = os.getenv("ACCESS_LOG", "-")
use_accesslog = accesslog_var or None
errorlog_var = os.getenv("ERROR_LOG", "-")
use_errorlog = errorlog_var or None

graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "120")
timeout_str = os.getenv("TIMEOUT", "120")
keepalive_str = os.getenv("KEEP_ALIVE", "5")

# Gunicorn config variables
workers = web_concurrency
bind = use_bind
errorlog = use_errorlog
worker_tmp_dir = "/dev/shm"
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)

# man, you have to mimic the expectations of gunicorn here!
# https://github.com/benoitc/gunicorn/blob/19.9.0/gunicorn/glogging.py#L53
logconfig_dict = dict(
    version=1,
    disable_existing_loggers=False,

    loggers={
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": False,
            "qualname": "gunicorn.error"
        },

        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
            "qualname": "gunicorn.access"
        }
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout"
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr"
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s.%(msecs)03d %(process)d %(levelname)s %(message)s",
            "datefmt": "%Y%m%d-%H%M%S",
            "class": "logging.Formatter"
        }
    }
)

# For debugging and testing
log_data = {
    "loglevel": LOG_LEVEL,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "use_max_workers": use_max_workers,
    "host": HOST,
    "port": PORT,
}
print(json.dumps(log_data))
