import datetime
import getpass
import logging
import socket
import sys
import time
from logging.handlers import SMTPHandler

from schedule import Scheduler

from config import CONFIG
from importer import import_market, import_assets, import_players, import_daily_sales

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

mail_handler = SMTPHandler(
    mailhost=("localhost", 25),
    fromaddr="{}@{}".format(getpass.getuser(), socket.gethostname()),
    toaddrs=[CONFIG["EMAIL"]],
    subject="Error on PixyShip sheduled worker!",
)

mail_handler.setLevel(logging.ERROR)
logger.addHandler(mail_handler)


class SafeScheduler(Scheduler):
    """
    An implementation of Scheduler that catches jobs that fail, logs their
    exception tracebacks as errors, optionally reschedules the jobs for their
    next run time, and keeps going.
    Use this to run jobs that may or may not crash without worrying about
    whether other jobs will run or if they'll crash the entire script.
    """

    def __init__(self, reschedule_on_failure=True):
        """
        If reschedule_on_failure is True, jobs will be rescheduled for their
        next run as if they had completed successfully. If False, they'll run
        on the next run_pending() tick.
        """
        self.reschedule_on_failure = reschedule_on_failure
        super().__init__()

    def _run_job(self, job):
        try:
            super()._run_job(job)
        except Exception:
            logger.exception("Uncaught scheduler exception", exc_info=True)

            if self.reschedule_on_failure:
                job.last_run = datetime.datetime.now()
                job._schedule_next_run()
            else:
                logger.error("Exit scheduler")
                sys.exit(1)  # the whole script will be restarted by supervisor, circus or whatever


# Scheduler setup
scheduler = SafeScheduler(False)
scheduler.every(5).minutes.do(import_assets)
scheduler.every().hour.do(import_market)
scheduler.every().hour.do(import_players)
scheduler.every().day.do(import_daily_sales)

while True:
    scheduler.run_pending()
    time.sleep(1)
