import os
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = 1  # Single worker to minimize memory usage
worker_class = "sync"
worker_connections = 1000
max_requests = 500  # Restart workers more frequently
max_requests_jitter = 50
preload_app = False  # Don't preload to save memory
reload = False

# Timeouts
timeout = 60  # Reduced from 120s
keepalive = 2
graceful_timeout = 30

# Memory optimization
worker_tmp_dir = "/dev/shm"  # Use RAM for temp files
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "bethel"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Environment variables
raw_env = [
    "WEB_CONCURRENCY=1",
    "PYTHONUNBUFFERED=1",
]

# Memory monitoring
def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid) 