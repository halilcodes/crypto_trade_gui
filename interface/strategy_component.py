import tkinter as tk
import typing

from interface.styling import *


class StrategyEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all_timeframes = ["1m", "5m", "15m", "30m","1h", "4h", "12h", "1d"]
        self._all_contracts = []

        self._body_index = 1

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text="Add strategy", font=GLOBAL_FONT,
                                     command=self._add_strategy_row, bg=BG_COLOR2, fg=FG_COLOR)

        self._add_button.pack(side=tk.TOP)



        self._headers = ["strategy", "contract", "timeframe", "balance %", "tp %", "sl %"]

        for idx, h in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=h.capitalize(),bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=idx)

        self.body_widgets = dict()

        for h in self._headers:
            self.body_widgets[h] = dict()

        self._body_index += 1

        self._base_params = [
            {"code_name": "strategy_type", "widget": tk.OptionMenu, "data_type": str, "value": ["Technical", "Breakout"], "width": 15},
            {"code_name": "contract", "widget": tk.OptionMenu, "data_type": str, "value": self._all_contracts, "width": 15},
            {"code_name": "timeframe", "widget": tk.OptionMenu, "data_type": str, "value": self._all_timeframes, "width": 7},
            {"code_name": "balance_pct", "widget": tk.Entry, "data_type": float,  "width": 7},
            {"code_name": "tp_pct", "widget": tk.Entry, "data_type": float,  "width": 7},
            {"code_name": "sl_pct", "widget": tk.Entry, "data_type": float,  "width": 7},
            {"code_name": "parameters", "widget": tk.Button, "data_type": float,  "width": 7, "text": "Parameters", "bg": BG_COLOR2, "command": self._show_popup},
            {"code_name": "activation", "widget": tk.Button, "data_type": float,  "width": 7, "text": "OFF", "bg": "darkred", "command": self._switch_strategy},
            {"code_name": "delete", "widget": tk.Button, "data_type": float,  "width": 7, "text": "Delete", "bg": "darkred", "command": self._delete_row},
        ]

    def _delete_row(self):
        return

    def _switch_strategy(self):
        return

    def _show_popup(self):
        return

    def _add_strategy_row(self):
        b_index = self._body_index


        self._body_index += 1