from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from config.logging_config import setup_logging
from processor.email_processor import EmailProcessor

logger = setup_logging()

class JobRunner:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.processor = EmailProcessor()

    def start(self):
        logger.info("Initializing APScheduler...")
        
        # Schedule the job
        self.scheduler.add_job(
            func=self.processor.process_emails,
            trigger=IntervalTrigger(minutes=settings.SCHEDULE_INTERVAL_MINUTES),
            id='email_processing_job',
            name='Process new emails from Gmail',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        logger.info(f"Job scheduled to run every {settings.SCHEDULE_INTERVAL_MINUTES} minutes.")
        
        try:
            # Run the processor once immediately on startup? 
            # The user didn't explicitly ask for immediate run but it's good practice for testing.
            # However, APScheduler interval trigger waits for first interval by default.
            # We will stick to the schedule.
            
            logger.info("Starting scheduler...")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
