import atexit
import logging.config
from logging import Handler, Logger, LogRecord
from logging.handlers import QueueHandler, RotatingFileHandler
from typing import TYPE_CHECKING, cast, override

from modules.resources.configs import logging_config

CHECKPOINT_LEVEL = 22
SUCCESS_LEVEL = 25


class EnhancedLogger(Logger):
    def success(self: Logger, msg: str, *args, **kwargs) -> None:
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, msg, args, **kwargs)

    def checkpoint(self: Logger, msg: str, *args, **kwargs) -> None:
        if self.isEnabledFor(CHECKPOINT_LEVEL):
            self._log(CHECKPOINT_LEVEL, msg, args, **kwargs)


# define a filter for maximum log levels
class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int) -> None:
        super().__init__()
        self._max_level = max_level

    @override
    def filter(self, record: LogRecord) -> bool:
        return record.levelno <= self._max_level


def log_namer(name: str) -> str:
    """Namer to keep logfile names ending with .log"""

    if name.endswith(".log"):
        return name

    base_part, backup_number = name.rsplit(".", 1)
    base_name = base_part.replace(".log", "")

    return f"{base_name}_{backup_number}.log"


def get_logger(name: str) -> EnhancedLogger:
    Logger.manager.setLoggerClass(EnhancedLogger)
    return cast("EnhancedLogger", Logger.manager.getLogger(name))


def setup_logging() -> None:
    """Sets up all the configurations and objects for logging"""

    logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
    logging.addLevelName(CHECKPOINT_LEVEL, "CHECKPOINT")
    logging.config.dictConfig(config=logging_config)

    queue_handler: Handler | None = logging.getHandlerByName("queue_handler")
    rf_handler: Handler | None = logging.getHandlerByName("rotating_file")

    if TYPE_CHECKING:
        assert isinstance(queue_handler, QueueHandler)
        assert queue_handler.listener is not None

        assert isinstance(rf_handler, RotatingFileHandler)

    rf_handler.namer = log_namer

    queue_handler.listener.start()
    atexit.register(queue_handler.listener.stop)

    # configure the discord logger to use the QueueHandler
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.INFO)
    discord_logger.addHandler(queue_handler)
