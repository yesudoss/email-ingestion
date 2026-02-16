from config.logging_config import setup_logging
from scheduler.job_runner import JobRunner

def main():
    logger = setup_logging()
    logger.info("Initializing Email Ingestion Service...")
    
    runner = JobRunner()
    runner.start()

if __name__ == "__main__":
    main()
