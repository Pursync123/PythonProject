import logging
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.archive_old_records import archive_old_records

logger = logging.getLogger(__name__)

# Create the scheduler instance
scheduler = BackgroundScheduler()

def setup_scheduler():
    """
    Configure and inject jobs into the background scheduler.
    """
    # Run the archival job automatically every day at 2:00 AM
    scheduler.add_job(
        func=archive_old_records,
        trigger="cron",
        hour=2,
        minute=0,
        id="archive_old_records_job",
        name="Archive old appointments and slots",
        replace_existing=True,
        # Default argument: archive everything older than 15 days
        kwargs={"days": 15},
    )
    logger.info("Scheduler configured: 'archive_old_records' will run daily at 02:00 AM.")

def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        setup_scheduler()
        scheduler.start()
        logger.info("Background scheduler started.")

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped.")
