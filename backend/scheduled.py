import datetime
import logging
import time

from schedule import Scheduler

from data_load import update_market, update_data, update_players

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
            logger.error('Uncaught scheduler exception', exc_info=True)
            job.last_run = datetime.datetime.now()
            job._schedule_next_run()


# Scheduler setup
scheduler = SafeScheduler()
scheduler.every(5).minutes.do(update_data)
scheduler.every(1).hours.do(update_market)
scheduler.every(1).day.do(update_players)

while True:
    scheduler.run_pending()
    time.sleep(1)
