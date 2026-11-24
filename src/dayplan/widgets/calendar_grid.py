"""Monthly calendar renderer."""

from __future__ import annotations

from datetime import date

from rich import box
from rich.table import Table
from textual.widgets import Static

from dayplan.utils.dates import month_grid

_DAY_NAMES = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]


class CalendarGrid(Static):
    """A Rich table showing one month with task and event indicators."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.year = date.today().year
        self.month = date.today().month
        self.marks: dict[date, dict[str, int]] = {}
        self.selected: date | None = None
        self.today: date = date.today()

    def set_month(
        self,
        year: int,
        month: int,
        marks: dict[date, dict[str, int]],
        selected: date | None = None,
        today: date | None = None,
    ) -> None:
        self.year, self.month = year, month
        self.marks = marks
        self.selected = selected
        self.today = today or date.today()
        self.update(self._build_table())

    def _build_table(self) -> Table:
        table = Table(box=box.SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
        for name in _DAY_NAMES:
            table.add_column(name, justify="center", no_wrap=True, width=12)

        for week in month_grid(self.year, self.month):
            cells = []
            for day in week:
                if day is None:
                    cells.append("")
                    continue
                marks = self.marks.get(day, {})
                indicators = []
                if marks.get("events"):
                    indicators.append(f"◆{marks['events']}")
                if marks.get("tasks"):
                    indicators.append(f"●{marks['tasks']}")
                if marks.get("overdue"):
                    indicators.append("!")
                cell = str(day.day)
                if indicators:
                    cell += " " + " ".join(indicators)
                if day == self.today:
                    cell = f"[bold reverse]{cell}[/]"
                elif day == self.selected:
                    cell = f"[bold]{cell}[/]"
                cells.append(cell)
            table.add_row(*cells)
        return table
