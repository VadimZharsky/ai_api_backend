import logging

from app.tools.loggers.i_logger import ILogger
from app.tools.loggers.unified_logger import UnifiedLogger
from app_config import AppConstants


class LoggerHub:
    def __init__(self) -> None:
        self._title: str = f"TITLE: {AppConstants.TITLE}"
        self._version: str = f"VERSION: {AppConstants.VERSION}"
        self._release: str = f"RELEASE FROM: {AppConstants.RELEASE_DATE}"
        self._upper_bound: str = ">" * len(self._release)
        self._lower_bound: str = "<" * len(self._release)
        self._service_log: UnifiedLogger = UnifiedLogger(logger_name=AppConstants.LOGGER_NAME, logger_lvl=logging.INFO)
        self._api_log: UnifiedLogger = UnifiedLogger(logger_name="api", logger_lvl=logging.INFO)
        self._sql_log: UnifiedLogger = UnifiedLogger(
            logger_name="sqlalchemy.engine",
            logger_lvl=logging.INFO,
            console_log=True,
        )

    @property
    def service(self) -> ILogger:
        return self._service_log

    @property
    def api(self) -> ILogger:
        return self._api_log

    def initialize(self) -> None:
        self._log_startup(self._service_log)
        self._log_startup(self._api_log)
        self._log_startup(self._sql_log)

    def _log_startup(self, logger: ILogger) -> None:
        logger.info(self._upper_bound)
        logger.info(self._title)
        logger.info(self._version)
        logger.info(self._release)
        logger.info(self._lower_bound)


logger_hub = LoggerHub()
