# -*- coding: utf-8 -*-
import os

bind = "0.0.0.0:8000"
accesslog = "-"
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"  # noqa: E501

workers = int(os.getenv("WEB_CONCURRENCY", 2))
threads = int(os.getenv("PYTHON_MAX_THREADS", 1))
timeout = 300
keepalive = 300  # HTTP keep-alive timeout
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))
