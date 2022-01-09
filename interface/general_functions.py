from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

import definitions


def note_name_to_number(name: str) -> int:
    """
    convert note names into standard scientific note numbers \n
    "A1" = 13, "C#" = 5, "D#20" = 247, "C♯4" = 53
    *matches negative numbers, DOES NOT MATCH FLAT* **♭**
    :param name: note in string format
    :return: standard note number
    """
    name = name.strip()
    if name.isnumeric():
        return int(name)
    name = name.upper()
    name = name.replace('#', '♯')  # replace with correct hash mark
    # match letter (+sharp) (+ number)
    match = re.match(r'([A-G][#♯]?)(-?\d*)', name)
    note_i = match.group(1)
    if match.group(2) == '':
        # checks for number after the letter (+ '#'), if none set to 0'th octave
        note_n = 0
    else:
        # set octave based on the final number
        note_n = int(match.group(2))
    # note = octave * 12 + note_position in `_note_name_` +1 (notes count from 1)
    note = note_n * 12 + definitions.note_names.index(note_i) + 1
    return note


def note_number_to_name(number: int) -> str:
    """
    convert standard note numbers to a note name \n
    5 = 'C#', 53='C#4'

    :param number: integer note number
    :return: string note name
    """

    name = definitions.note_names[(number - 1) % 12]
    octave = (number - 1) // 12
    return f'{name}{octave}'


def bind_select_all(*entries: ttk.Entry):
    for entry in entries:
        entry: ttk.Entry
        entry.bind('<FocusIn>', lambda e: e.widget.select_range(0, tk.END), add=True)
        entry.bind('<FocusOut>', lambda e: e.widget.select_range(0, 0), add=True)

