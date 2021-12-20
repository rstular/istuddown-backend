import json
import logging
import os
import signal
import sys
import time
from datetime import timedelta

import schedule

from helpers import time_since_last_healthcheck
from perform_healthcheck import perform_healthcheck

pid = str(os.getpid())
pidfile = "/run/hcdaemon/hcdaemon.pid"


hc_logger = logging.getLogger("HealthCheck daemon")
hc_logger.setLevel(logging.INFO)

# syslog_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
# syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
# syslog_handler.setFormatter(syslog_formatter)
# syslog_handler.setLevel(logging.INFO)
# hc_logger.addHandler(syslog_handler)

stdout_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(stdout_formatter)
stdout_handler.setLevel(logging.INFO)
hc_logger.addHandler(stdout_handler)

hc_logger.info("Starting healthcheck daemon")

try:
    with open(sys.argv[1]) as f:
        config = json.load(f)
except IOError as err:
    hc_logger.critical(str(err))
    exit(1)

# Check if PID file exists and the process owning it is alive
if os.path.isfile(pidfile):
    with open(pidfile) as f:
        pidfile_content = int(f.read())
    try:
        os.kill(pidfile_content, 0)
    except OSError:
        os.unlink(pidfile)
        hc_logger.warning("PID file belonging to a dead process exists, deleting it")
    else:
        hc_logger.error("PID file belonging to an active process exists, aborting")
        exit()


hc_logger.debug("Creating PID file")
with open(pidfile, "w") as f:
    f.write(pid)


def handler(signum, frame):
    if signum == signal.SIGUSR1:
        if time_since_last_healthcheck(config) > timedelta(
            seconds=config["min_check_interval"]
        ):
            hc_logger.info("Healthcheck triggered via SIGUSR1")
            perform_healthcheck(config)
        else:
            hc_logger.info("Healthcheck triggered via SIGUSR1, but it's to soon")
    elif signum == signal.SIGTERM:
        hc_logger.warn("SIGTERM received, quitting")
        os.unlink(pidfile)  # Delete PID file
        exit(0)


hc_logger.info("Registering signal handlers")
signal.signal(signal.SIGUSR1, handler)


hc_logger.debug("Scheduling tasks")
schedule.every(5).minutes.do(perform_healthcheck, config)

hc_logger.info("Running main loop")
try:
    while True:
        schedule.run_pending()
        time.sleep(5)
except KeyboardInterrupt:
    hc_logger.warn("Keyboard interrupt received, quitting")
    os.unlink(pidfile)  # Delete PID file
