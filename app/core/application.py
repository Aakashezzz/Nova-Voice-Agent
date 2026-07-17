from loguru import logger

from app.config.settings import settings
from app.core.logger import setup_logger


class Application:
    def __init__(self) -> None:
        setup_logger()

    def start(self) -> None:
        logger.info("Starting {}", settings.APP_NAME)
        logger.info("Version: {}", settings.APP_VERSION)
        logger.info("Configuration loaded successfully.")
        logger.success("Application initialized successfully.")