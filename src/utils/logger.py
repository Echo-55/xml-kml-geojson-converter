import enum
import logging
import random
from typing import Optional, Union, Any

import rich.status
from rich.highlighter import JSONHighlighter
from rich.logging import RichHandler
from rich.console import Console, RenderableType, JustifyMethod, OverflowMethod
from rich.progress import ProgressColumn, GetTimeCallable
from rich.style import Style
from rich import pretty, progress
# noinspection PyProtectedMember
from rich._spinners import SPINNERS

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.config import Config


class Logger:
    def __init__(self, config: "Config"):
        self._initialized = False

        self._console = Console(
            color_system="auto",
            log_path=True,
            log_time_format="[%X]",
            highlighter=JSONHighlighter()
        )

        log_level_str = config.get("GENERAL", "log_level", fallback="INFO")
        log_level = self._get_log_level(log_level_str)
        with self._console.status("[bold green]Initializing logger...[/bold green]"):
            self._init_logger("BatchConverter", log_level)

    def _init_logger(self, name, log_level):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(log_level)
        self._logger.propagate = False

        self._handler = RichHandler(
            show_time=False,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        self._formatter = logging.Formatter(
            "%(name)s - %(levelname)s - %(message)s"
        )
        self._handler.setFormatter(self._formatter)
        self._logger.addHandler(self._handler)
        self._initialized = True

    @staticmethod
    def _get_log_level(log_level_str: str) -> int:
        """Convert log level string to logging level."""
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return log_levels.get(log_level_str.upper(), logging.INFO)

    @staticmethod
    def track(*args, **kwargs):
        return progress.track(*args, **kwargs)

    @staticmethod
    def progress(*columns: Union[str, ProgressColumn],
                 console: Optional[Console] = None,
                 auto_refresh: bool = True,
                 refresh_per_second: float = 10,
                 speed_estimate_period: float = 30.0,
                 transient: bool = False,
                 redirect_stdout: bool = True,
                 redirect_stderr: bool = True,
                 get_time: Optional[GetTimeCallable] = None,
                 disable: bool = False,
                 expand: bool = False) -> progress.Progress:
        """Renders an auto-updating progress bar(s).

        Args:
            console (Console, optional): Optional Console instance. Defaults to an internal Console instance writing to stdout.
            auto_refresh (bool, optional): Enable auto refresh. If disabled, you will need to call `refresh()`.
            refresh_per_second (Optional[float], optional): Number of times per second to refresh the progress information or None to use default (10). Defaults to None.
            speed_estimate_period: (float, optional): Period (in seconds) used to calculate the speed estimate. Defaults to 30.
            transient: (bool, optional): Clear the progress on exit. Defaults to False.
            redirect_stdout: (bool, optional): Enable redirection of stdout, so ``print`` may be used. Defaults to True.
            redirect_stderr: (bool, optional): Enable redirection of stderr. Defaults to True.
            get_time: (Callable, optional): A callable that gets the current time, or None to use Console.get_time. Defaults to None.
            disable (bool, optional): Disable progress display. Defaults to False
            expand (bool, optional): Expand tasks table to fit width. Defaults to False.
        """
        return progress.Progress(
            *columns,
            console=console,
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            speed_estimate_period=speed_estimate_period,
            transient=transient,
            redirect_stdout=redirect_stdout,
            redirect_stderr=redirect_stderr,
            get_time=get_time,
            disable=disable,
            expand=expand,
        )

    def status(self, status: RenderableType, use_random_spinner=False, **kwargs) -> rich.status.Status:
        """Display a status and spinner. See `rich.console.Console.status` for details.
        Args:
            status (RenderableType): A status renderable (str or Text typically).
            use_random_spinner (bool): If True, use a random spinner from the available spinners.

        Returns:
            Status: A Status object that may be used as a context manager.
        """
        if use_random_spinner:
            spinner = self._get_random_spinner()
            kwargs["spinner"] = spinner
        return self._console.status(status, **kwargs)

    def print(
            self,
            *objects: Any,
            sep: str = " ",
            end: str = "\n",
            style: Optional[Union[str, Style]] = None,
            justify: Optional[JustifyMethod] = None,
            overflow: Optional[OverflowMethod] = None,
            no_wrap: Optional[bool] = None,
            emoji: Optional[bool] = None,
            markup: Optional[bool] = None,
            highlight: Optional[bool] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            crop: bool = True,
            soft_wrap: Optional[bool] = None,
            new_line_start: bool = False, ):
        self._console.print(
            *objects,
            sep=sep,
            end=end,
            style=style,
            justify=justify,
            overflow=overflow,
            no_wrap=no_wrap,
            emoji=emoji,
            markup=markup,
            highlight=highlight,
            width=width,
            height=height,
            crop=crop,
            soft_wrap=soft_wrap,
            new_line_start=new_line_start
        )

    def print_json(self, json, **kwargs: object) -> None:
        self._console.print_json(json, indent=4, **kwargs)

    @staticmethod
    def pprint(obj):
        pretty.pprint(obj)

    def print_exception(self, exc):
        self._console.print_exception()
        self._logger.error(exc)

    def info(self, msg):
        self._logger.info(msg)

    def success(self, msg):
        self._logger.info(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)

    def debug(self, msg):
        self._logger.debug(msg)

    def critical(self, msg):
        self._logger.critical(msg)

    @staticmethod
    def _get_random_spinner():
        random_index = random.randint(0, len(SPINNERS) - 1)
        return list(SPINNERS.keys())[random_index]

    class EPrintStyle(enum.Enum):
        INFO = Style(color="blue")
        SUCCESS = Style(color="green")
        WARNING = Style(color="yellow")
        ERROR = Style(color="red")
        CRITICAL = Style(color="red", bold=True)
        DEBUG = Style(color="cyan")
