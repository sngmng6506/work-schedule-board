from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence

from daymark.theme import (
    ACCENT,
    HOVER_BG,
    INPUT_FOCUS_BG,
    MUTED_TEXT,
    SUBTLE_TEXT,
    TEXT,
    WINDOW_BG,
    fonts,
)


class FlatSelect(tk.Menubutton):
    def __init__(
        self,
        master: tk.Misc,
        variable: tk.StringVar,
        values: Sequence[str],
        *,
        width: int = 24,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            master,
            textvariable=variable,
            background=INPUT_FOCUS_BG,
            activebackground=HOVER_BG,
            foreground=TEXT,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            anchor="w",
            padx=12,
            pady=8,
            width=width,
            cursor="hand2",
            font=fonts(master).dialog_body,
            indicatoron=True,
            takefocus=True,
        )
        menu = tk.Menu(
            self,
            tearoff=False,
            background=WINDOW_BG,
            foreground=TEXT,
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            font=fonts(master).dialog_body,
        )
        for value in values:
            menu.add_radiobutton(
                label=value,
                variable=variable,
                value=value,
                command=on_change,
            )
        self.configure(menu=menu)
        self.menu = menu


class FlatSlider(tk.Canvas):
    """A flat, keyboard-accessible slider used for live opacity preview."""

    HEIGHT = 30
    KNOB_RADIUS = 8

    def __init__(
        self,
        master: tk.Misc,
        variable: tk.DoubleVar,
        *,
        from_: float,
        to: float,
        resolution: float = 0.01,
        command: Callable[[str], None] | None = None,
        width: int = 400,
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=self.HEIGHT,
            background=WINDOW_BG,
            borderwidth=0,
            highlightthickness=0,
            takefocus=True,
            cursor="hand2",
        )
        self.variable = variable
        self.from_ = float(from_)
        self.to = float(to)
        self.resolution = float(resolution)
        self.command = command
        self.focused = False
        self.hovered = False
        self.bind("<Configure>", lambda _event: self._draw())
        self.bind("<Button-1>", self._pointer)
        self.bind("<B1-Motion>", self._pointer)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.bind("<Left>", lambda _event: self._step(-1))
        self.bind("<Right>", lambda _event: self._step(1))
        self.bind("<Home>", lambda _event: self._set(self.from_))
        self.bind("<End>", lambda _event: self._set(self.to))
        variable.trace_add("write", lambda *_args: self._draw())

    def _track_bounds(self) -> tuple[float, float]:
        width = max(1, self.winfo_width())
        return 12.0, max(12.0, width - 12.0)

    def _normalized(self) -> float:
        span = self.to - self.from_
        if span <= 0:
            return 0.0
        value = min(self.to, max(self.from_, float(self.variable.get())))
        return (value - self.from_) / span

    def _draw(self) -> None:
        if not self.winfo_exists():
            return
        self.delete("all")
        left, right = self._track_bounds()
        center = self.HEIGHT / 2
        knob_x = left + (right - left) * self._normalized()
        self.create_line(
            left,
            center,
            right,
            center,
            fill="#3A3A3C",
            width=4,
            capstyle="round",
        )
        self.create_line(
            left,
            center,
            knob_x,
            center,
            fill=ACCENT,
            width=4,
            capstyle="round",
        )
        outline = TEXT if self.focused else (SUBTLE_TEXT if self.hovered else MUTED_TEXT)
        self.create_oval(
            knob_x - self.KNOB_RADIUS,
            center - self.KNOB_RADIUS,
            knob_x + self.KNOB_RADIUS,
            center + self.KNOB_RADIUS,
            fill=TEXT,
            outline=outline,
            width=2 if self.focused else 1,
        )

    def _pointer(self, event: tk.Event) -> None:
        self.focus_set()
        left, right = self._track_bounds()
        ratio = min(1.0, max(0.0, (event.x - left) / max(1.0, right - left)))
        self._set(self.from_ + ratio * (self.to - self.from_))

    def _step(self, direction: int) -> str:
        self._set(float(self.variable.get()) + direction * self.resolution)
        return "break"

    def _set(self, value: float) -> str:
        bounded = min(self.to, max(self.from_, value))
        steps = round((bounded - self.from_) / self.resolution)
        normalized = self.from_ + steps * self.resolution
        self.variable.set(round(normalized, 4))
        if self.command is not None:
            self.command(str(self.variable.get()))
        return "break"

    def _enter(self, _event: tk.Event) -> None:
        self.hovered = True
        self._draw()

    def _leave(self, _event: tk.Event) -> None:
        self.hovered = False
        self._draw()

    def _focus_in(self, _event: tk.Event) -> None:
        self.focused = True
        self._draw()

    def _focus_out(self, _event: tk.Event) -> None:
        self.focused = False
        self._draw()
