import logging
import sys
from typing import Literal, Optional, TextIO

import colorama


class ColoredConsoleFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.CRITICAL: colorama.Fore.MAGENTA,
        logging.ERROR: colorama.Fore.RED,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.INFO: colorama.Fore.BLUE,
        logging.DEBUG: colorama.Fore.WHITE,
    }

    DEFAULT_LEVEL_COLOR = colorama.Fore.CYAN
    DEFAULT_FORMAT = "{__level_color__}{levelname}{__reset_color__} | {name} | {message}"

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "{",
        validate: bool = True,
    ):
        if fmt is None:
            fmt = self.DEFAULT_FORMAT

        sys.version

        super().__init__(
            fmt=fmt,
            datefmt=datefmt,
            style=style,
            validate=validate,
        )

    def formatMessage(self, record: logging.LogRecord) -> str:
        color_keys = {
            "__level_color__": self.LEVEL_COLORS.get(record.levelno, self.DEFAULT_LEVEL_COLOR),
            "__reset_color__": colorama.Fore.RESET,
        }
        record.__dict__.update(color_keys)
        return super().formatMessage(record)


def setup_stdout() -> logging.StreamHandler[TextIO]:
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredConsoleFormatter())
    root.addHandler(handler)

    return handler


def basic_setup() -> None:
    setup_stdout()
