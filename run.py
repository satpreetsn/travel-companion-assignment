import os

# Disable Hugging Face telemetry
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# Disable Hugging Face progress bars
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from transformers.utils import logging as hf_logging

from src.ui.terminal import main


# Suppress Transformers console output
hf_logging.set_verbosity_error()


PROJECT_ROOT = Path(__file__).resolve().parent

LOG_DIR = PROJECT_ROOT / "logs"


def configure_logging() -> Path:

    LOG_DIR.mkdir(exist_ok=True)

    session_timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    log_file = (
        LOG_DIR
        / f"backend_{session_timestamp}.log"
    )

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        encoding="utf-8",
    )

    return log_file


async def run_application():

    log_file = configure_logging()

    logger = logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("TRAVEL COMPANION SESSION STARTED")
    logger.info("=" * 70)
    logger.info(
        "Session log file: %s",
        log_file,
    )

    try:

        await main()

    except Exception:

        logger.exception(
            "Unhandled application error"
        )

        raise

    finally:

        logger.info("=" * 70)
        logger.info("TRAVEL COMPANION SESSION ENDED")
        logger.info("=" * 70)

        logging.shutdown()

        print()
        print("=" * 70)
        print("Session ended.")
        print()
        print("Backend log:")
        print(log_file.resolve())
        print("=" * 70)
        print()


if __name__ == "__main__":

    asyncio.run(
        run_application()
    )