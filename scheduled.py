import datetime
import logging
from schedule import Scheduler
import time

from data_load import check_market, update_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


class SafeScheduler(Scheduler):
    def __init__(self, reschedule_on_failure=True):
        self.reschedule_on_failure = reschedule_on_failure
        super().__init__()

    def _run_job(self, job):
        try:
            super()._run_job(job)
        except Exception:
            log.error('Uncaught scheduler exception', exc_info=True)
            job.last_run = datetime.datetime.now()
            job._schedule_next_run()


# Scheduler setup
scheduler = SafeScheduler()
scheduler.every(1).minutes.do(check_market)
scheduler.every(5).minutes.do(update_data)

while True:
    scheduler.run_pending()
    time.sleep(1)
