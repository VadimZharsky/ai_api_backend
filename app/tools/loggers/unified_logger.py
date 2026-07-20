from logging import Logger
from typing import override

from app.tools.loggers.console_logger import BcColors, ConsoleLogger
from app.tools.loggers.i_logger import ILogger
from app.tools.loggers.logger_builder import LoggerBuilder


class UnifiedLogger(ILogger):
    """
    proxify logger with stdout
    """

    def __init__(
        self,
        logger_name: str,
        logger_lvl: int,
        color: BcColors = BcColors.ENDC,
        console_log: bool = True,
    ) -> None:
        self._prefix: str = f"{logger_name.upper()} >> "
        self._color: BcColors = color
        self._console_log: bool = console_log
        self._logger: Logger = LoggerBuilder(logger_name, logger_lvl).build

    @override
    def info(self, message: str) -> None:
        self._logger.info(message)
        if self._console_log:
            ConsoleLogger.c_print(f"{self._prefix}{message}", self._color)

    @override
    def warning(self, message: str) -> None:
        self._logger.warning(message)
        if self._console_log:
            ConsoleLogger.c_print(f"{self._prefix}{message}", BcColors.WARNING)

    @override
    def error(self, message: str) -> None:
        self._logger.error(message)
        if self._console_log:
            ConsoleLogger.c_print(f"{self._prefix}{message}", BcColors.FAIL)

    @override
    def exception(self, message: str) -> None:
        self._logger.exception(message)
        if self._console_log:
            ConsoleLogger.c_print(f"{self._prefix}{message}", BcColors.FAIL)
