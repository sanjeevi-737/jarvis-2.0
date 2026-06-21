from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

_console = Console()


class CLI:
    @staticmethod
    def _ts() -> str:
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def banner() -> None:
        _console.print()
        _console.rule("[bold cyan]JARVIS PRIME 2.0[/]", characters="=")
        _console.print(
            Text(" Just A Rather Very Intelligent System", style="cyan italic"),
            justify="center",
        )
        _console.rule(characters="=")
        _console.print()

    @staticmethod
    def status(msg: str) -> None:
        _console.print(f"  [{CLI._ts()}] {msg}", style="dim white")

    @staticmethod
    def user_input(text: str) -> None:
        label = Text(" You ", style="bold green on #1a3a1a")
        content = Text(text, style="green")
        panel = Panel(
            content,
            title=label,
            title_align="left",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        _console.print(panel)

    @staticmethod
    def assistant(text: str) -> None:
        label = Text(" JARVIS ", style="bold cyan on #0a2a3a")
        content = Text(text, style="white")
        panel = Panel(
            content,
            title=label,
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        _console.print(panel)

    @staticmethod
    def notification(text: str) -> None:
        _console.print(f"  [bold yellow]->[/] {text}", style="yellow")

    @staticmethod
    def listening() -> None:
        _console.print(
            Panel.fit(
                " [bold yellow]>> Listening... Speak now <<[/] ",
                border_style="yellow",
                box=box.SQUARE,
            )
        )

    @staticmethod
    def thinking() -> None:
        _console.print(
            Panel.fit(
                " [bold magenta]>> Processing... <<[/] ",
                border_style="magenta",
                box=box.SQUARE,
            )
        )
