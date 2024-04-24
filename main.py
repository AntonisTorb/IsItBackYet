import logging
from pathlib import Path

from is_it_back_yet import IsItBackYet, maintain_log


def main() -> None:

    cwd = Path.cwd()
    logger_path = cwd / "is_it_back_yet.log"
    main_logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(filename=logger_path, 
                        level=logging.INFO,
                        format="%(asctime)s|%(levelname)8s|%(name)s|%(message)s")
    
    try:
        maintain_log(logger_path, 30)
        bot = IsItBackYet()
        main_logger.info("Starting bot...")
        bot.run_bot()
        main_logger.info("Closing bot...")
    except Exception as e:
        main_logger.exception(e)

if __name__ == "__main__":
    
    main()