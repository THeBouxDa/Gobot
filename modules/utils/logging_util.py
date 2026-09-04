from typing import override, Callable, TYPE_CHECKING, Protocol, cast

from pathlib import Path
import json
import atexit

import logging.config
from logging.handlers import QueueHandler
from logging import Logger


SUCCESS_LEVEL = 25

config_file = Path.joinpath(Path.cwd(), "configs", "logging_config.json")



# class EnhancedLogger(Logger):
#     def success(self: Logger, msg: str, *args, **kwargs):
#         if self.isEnabledFor(SUCCESS_LEVEL):
#             self._log(SUCCESS_LEVEL, msg, args, **kwargs)

# def get_logger(name: str | None = None) -> Logger | EnhancedLogger:
#     return cast(Logger | EnhancedLogger, logging.getLogger(name))


# define a filter for maximum log levels
class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int):
        super().__init__()
        self._max_level = max_level

    @override
    def filter(self, record):
        return record.levelno <= self._max_level


def setup_logging():
    with open(config_file) as file:
        config = json.load(file)
    
    
    logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
    logging.config.dictConfig(config=config)
    
    def success(self: Logger, msg: str, *args, **kwargs):
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, msg, args, **kwargs)
    
    Logger.success = success # type: ignore
    
    queue_handler = logging.getHandlerByName("queue_handler")
    
    if queue_handler is not None:
        assert isinstance(queue_handler, QueueHandler)
        assert queue_handler.listener is not None
        
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
        
        # configure the discord logger to use the QueueHandler
        discord_logger = logging.getLogger('discord')
        discord_logger.setLevel(logging.INFO)
        discord_logger.addHandler(queue_handler)
        
