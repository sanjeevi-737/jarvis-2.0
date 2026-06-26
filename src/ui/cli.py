from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.live import Live
from rich.spinner import Spinner

_console = Console(legacy_windows=False)

# ── Design Tokens (AI-Native Dark) ────────────────────────
class Theme:
    bg = "#0A0A0F"
    surface = "#141420"
    primary = "#A78BFA"
    primary_bg = "#2D1B69"
    secondary = "#818CF8"
    secondary_bg = "#1E1B4B"
    accent = "#F472B6"
    success = "#34D399"
    success_bg = "#064E3B"
    warning = "#FBBF24"
    text = "#E2E8F0"
    text_dim = "#94A3B8"
    text_darker = "#64748B"
    border = "#2D2D3F"
    error = "#F87171"


class CLI:
    _thinking_live: Live | None = None

    @staticmethod
    def _ts() -> str:
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def banner() -> None:
        _console.print()
        _console.rule(
            Text(" JARVIS ", style=f"bold {Theme.primary}"),
            characters="=",
            style=Theme.border,
        )
        _console.print(
            Text(
                "  Just A Rather Very Intelligent System",
                style=f"italic {Theme.text_dim}",
            ),
            justify="center",
        )
        _console.print(
            Text(f"  >> {CLI._ts()} Neural interface active", style=Theme.success),
            justify="center",
        )
        _console.rule(characters="=", style=Theme.border)
        _console.print()

    @staticmethod
    def status(msg: str) -> None:
        _console.print(
            f"  {CLI._ts()} - {msg}",
            style=Theme.text_darker,
        )

    @staticmethod
    def user_input(text: str) -> None:
        label = Text("  YOU  ", style=f"bold {Theme.secondary}")
        content = Text(text, style=Theme.text)
        _console.print(
            Panel(
                content,
                title=label,
                title_align="left",
                border_style=Theme.secondary,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

    @staticmethod
    def assistant(text: str) -> None:
        label = Text("  >> JARVIS  ", style=f"bold {Theme.primary}")
        content = Text(text, style=Theme.text)
        _console.print(
            Panel(
                content,
                title=label,
                title_align="left",
                border_style=Theme.primary,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

    @staticmethod
    def notification(text: str) -> None:
        _console.print(f"  [{Theme.accent}]*[/] {text}", style=Theme.accent)

    @staticmethod
    def listening() -> None:
        _console.print(
            Panel.fit(
                Text.assemble(
                    (f" {CLI._ts()} ", Theme.text_darker),
                    (">> ", Theme.success),
                    ("Listening... Speak now ", Theme.text),
                ),
                border_style=Theme.success,
                box=box.SQUARE,
            )
        )

    @staticmethod
    def thinking() -> None:
        _console.print(
            Panel.fit(
                Text.assemble(
                    (f" {CLI._ts()} ", Theme.text_darker),
                    (".. ", Theme.primary),
                    ("Processing... ", Theme.text),
                ),
                border_style=Theme.primary,
                box=box.SQUARE,
            )
        )

    @staticmethod
    def start_thinking() -> None:
        """Start an animated thinking spinner (optional, replaces thinking())."""
        spinner = Spinner(
            "dots",
            style=Theme.primary,
            text=Text(" Processing...", style=Theme.text),
        )
        CLI._thinking_live = Live(
            Panel(spinner, border_style=Theme.primary, box=box.SQUARE),
            refresh_per_second=10,
        )
        CLI._thinking_live.start()

    @staticmethod
    def stop_thinking() -> None:
        """Stop the animated thinking spinner."""
        if CLI._thinking_live:
            CLI._thinking_live.stop()
            CLI._thinking_live = None

    @staticmethod
    def error(text: str) -> None:
        _console.print(
            Panel(
                Text(text, style=Theme.error),
                border_style=Theme.error,
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )
