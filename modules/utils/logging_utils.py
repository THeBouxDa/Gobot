import atexit
import json
import logging.config
from logging import Logger, LogRecord
from logging.handlers import QueueHandler
from typing import TYPE_CHECKING, cast, override

from modules.paths import logging_config

SUCCESS_LEVEL = 25


class EnhancedLogger(Logger):
    def success(self: Logger, msg: str, *args, **kwargs) -> None:
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, msg, args, **kwargs)


# define a filter for maximum log levels
class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int) -> None:
        super().__init__()
        self._max_level = max_level

    @override
    def filter(self, record: LogRecord) -> bool:
        return record.levelno <= self._max_level


def get_logger(name: str) -> EnhancedLogger:
    Logger.manager.setLoggerClass(EnhancedLogger)
    return cast("EnhancedLogger", Logger.manager.getLogger(name))


def setup_logging() -> None:
    with logging_config.open() as file:
        config = json.load(file)

    logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
    logging.config.dictConfig(config=config)

    queue_handler = logging.getHandlerByName("queue_handler")

    if queue_handler is not None:
        if TYPE_CHECKING:
            assert isinstance(queue_handler, QueueHandler)
            assert queue_handler.listener is not None

        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)

        # configure the discord logger to use the QueueHandler
        discord_logger = logging.getLogger("discord")
        discord_logger.setLevel(logging.INFO)
        discord_logger.addHandler(queue_handler)
