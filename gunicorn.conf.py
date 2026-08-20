# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/settings.html

# Use gthread (threaded) workers instead of sync to avoid blocking the
# entire worker process during long downloads + ffmpeg conversions.
worker_class = "gthread"
threads = 4
workers = 2

# Increase timeout to 120s to allow for large video downloads + ffmpeg
# MP3 conversion. The default 30s is far too short.
timeout = 120

# Graceful timeout — how long to wait for worker to finish after SIGTERM
graceful_timeout = 30
