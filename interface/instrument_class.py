from __future__ import annotations

import pathlib
import tkinter as tk
import typing
from math import pi
from tkinter import ttk

from interface import general_functions
from interface.material_and_measures import Distance, Force, WireMaterial


class Note:
    """ A single note in an instrument, contains functions and data related to the wire used  """
    instrument: Instrument
    _std_note: int
    _material_select: tk.StringVar
    _length: tk.DoubleVar
    _diameter: tk.DoubleVar
    _wire_count: tk.IntVar
    _frequency_var: tk.StringVar
    _frequency_float: float
    _tkk_items: list[ttk.Label | ttk.Combobox | ttk.Entry]
    tkk_input_items: list[ttk.Combobox | ttk.Entry]

    def __init__(self, instrument: Instrument, std_note: int):
        """
        :param instrument: parent :class:`Instrument`
        :param std_note: standard note number, A0 = 1, C0 = 4, A4 = 49
        """
        if not isinstance(std_note, int):
            raise ValueError(std_note)
        _row = std_note * 2 + 10
        self.instrument = instrument
        # Initialize variables
        self._std_note = std_note
        self._frequency_var = tk.StringVar(instrument, '0')
        self._wire_count = tk.IntVar(instrument, 1)
        self._material_select = tk.StringVar(instrument, None)
        self._diameter = tk.DoubleVar(instrument, '')
        self._length = tk.DoubleVar(instrument, '')
        self._force = tk.DoubleVar(instrument)
        self._frequency_float = 0
        self.calculate_frequency()

        # set tk items
        _lbl_std_note = ttk.Label(instrument, text=self._std_note, width=6)
        _lbl_str_note = ttk.Label(instrument, text=self.get_std_note_name(), width=6)
        _lbl_frequency = ttk.Label(instrument, textvariable=self._frequency_var)
        _combo_material_select = ttk.Combobox(instrument, textvariable=self._material_select,
                                              postcommand=lambda: _combo_material_select.configure(
                                                  values=WireMaterial.code_name_list()))
        _ent_length = ttk.Entry(instrument, textvariable=self._length)
        _ent_diameter = ttk.Entry(instrument, textvariable=self._diameter)
        _ent_wire_count = ttk.Entry(instrument, textvariable=self._wire_count)
        _ent_force = ttk.Label(instrument, textvariable=self._force)
        self._tkk_items = [_lbl_std_note, _lbl_str_note, _lbl_frequency,
                           _ent_length, _combo_material_select, _ent_diameter, _ent_wire_count, _ent_force]
        self.tkk_input_items = [_ent_length, _combo_material_select, _ent_diameter, _ent_wire_count]

        # set grid positions of items, uses the order set by tkk_input_items list
        for i, _t in enumerate(self._tkk_items):
            _t.grid(row=_row, column=i, sticky=tk.EW)

        # bind movement keys to tk input items
        for _n, _t in enumerate(self.tkk_input_items):
            # bind force calculation on focus loss
            _t.bind("<FocusOut>", self.update_force, add=True)
            # bind return to drop a cell down
            _t.bind("<Right>", lambda e, _n=_n: self.instrument.get_next_note_input(self._std_note, _n, 0, 1))
            _t.bind("<Left>", lambda e, _n=_n: self.instrument.get_next_note_input(self._std_note, _n, 0, -1))
            _t.bind("<Shift-Return>", lambda e, _n=_n: self.instrument.get_next_note_input(self._std_note, _n, -1))
            _t.bind("<Up>", lambda e, _n=_n: self.instrument.get_next_note_input(self._std_note, _n, -1))
            _t.bind("<Return>", lambda e, _n=_n: self.instrument.get_next_note_input(self._std_note, _n, 1))
            _t.bind("<Down>", lambda e, _n=_n: self.instrument.get_next_note_input(self._std_note, _n, 1))

        # highlighter bindings
        general_functions.bind_highlighting_on_focus(_ent_length, _ent_diameter, _ent_wire_count)

        # add separator above each C
        if std_note % 12 == 4:
            _separator = ttk.Separator(instrument, orient=tk.HORIZONTAL)
            _separator.grid(column=0, columnspan=len(self._tkk_items), row=_row - 1, sticky=tk.NSEW)

    def destroy(self):
        for i_ in self._tkk_items:
            i_.destroy()

    def calculate_frequency(self):
        """ calculate the _frequency_var of `Note` based the pitch of A1 in the parent :class:`Instrument` """
        # _frequency_var = 2 ** ((note_number - 49) / 12 ) * (_frequency_var of A1)
        self._frequency_float = 2 ** ((self.get_std_note_number() - 49) / 12) * self.instrument.get_pitch()
        self._frequency_var.set(f"{self._frequency_float:>.2f}hz")

    def get_std_note_number(self) -> int:
        return self._std_note

    def get_std_note_name(self) -> str:
        return general_functions.note_number_to_name(self._std_note)

    def get_frequency(self) -> float:
        return self._frequency_float

    def get_wire_count(self) -> int:
        return self._wire_count.get()

    def get_wire_type(self) -> WireMaterial:
        return WireMaterial.get_by_code(self._material_select.get().split(' ')[0])

    def get_diameter(self) -> Distance:
        return Distance(mm=self._diameter.get())

    def get_length(self) -> Distance:
        return Distance(mm=self._length.get())

    def get_force(self) -> Force:
        """
        calculate the tension and _diameter of the wire using methods from \n
        `sound_from_wire_equation <https://www.school-for-champions.com/science/sound_from_wire_equation.htm>`_ \n
        --- **f** is the _frequency_var in hertz (Hz) or cycles per second \n
        --- **L** is the _length of the wire in centimeters (cm) \n
        --- **d** is the _diameter of the wire in cm \n
        --- **T** is the tension on the wire in gm-cm/s² \n
        --- **π** is the Greek letter pi = 3.14 \n
        --- **δ** is the density of the wire in gm/cm³ (Greek letter small delta) \n

        :return: :class:`Tension` of the string as `T = πf²L²d²δ`
        """
        pi_hz = pi * self.get_frequency() ** 2  # πf²
        le = self.get_length().cm() ** 2  # L²
        di = self.get_diameter().cm() ** 2  # d²
        den = self.get_wire_type().density.g_cm3()  # δ
        gcm = pi_hz * le * di * den
        return Force(g_cm_s2=gcm * self.get_wire_count())

    def update_force(self, *arg):
        try:
            self._force.set(str(self.get_force()))
        except ValueError or TypeError:
            # ValueError is only thrown when missing required data
            pass

    def state_import(self, data: dict):
        """ convert dict of input fields to a Note """
        self._wire_count.set(int(data['_wire_count']))
        self._material_select.set(str(data['_material_select']))
        self._diameter.set(float(data['_diameter']))
        self._length.set(float(data['_length']))

        self.calculate_frequency()
        self.update_force()

    def state_export(self) -> dict[str, int | str]:
        """ convert input fields to a dict """
        return dict(_wire_count=self._wire_count.get(),
                    _material_select=self._material_select.get(),
                    _diameter=self._diameter.get(),
                    _length=self._length.get())

    def set_focus_to_input(self, input_pos):
        """ Used for binding <Enter>
        :param input_pos: position on the input items list
        """
        try:
            self.tkk_input_items[input_pos].focus_set()
        except IndexError as ie:
            # ignore index errors here, on the off chance its needed
            print(f"IndexError {ie} in Note.set_focus_to_input(self, {input_pos})")
            pass


class Instrument(ttk.Frame):
    notes: dict[int, Note]
    lowest_key: tk.StringVar
    highest_key: tk.StringVar
    pitch: tk.DoubleVar
    file_uri: pathlib.Path | None

    def __init__(self, parent):
        super(Instrument, self).__init__(parent)
        """
        """
        self.parent = parent
        self.file_uri = None

        # Labels
        _lbl_inst_name = ttk.Label(self, text="Instrument Name")
        _lbl_lowest_key = ttk.Label(self, text="Lowest Key")
        _lbl_highest_key = ttk.Label(self, text="Highest Key")
        _lbl_pitch = ttk.Label(self, text="Pitch of A1 (hz)")
        # Labels position
        _lbl_inst_name.grid(row=0, column=0, columnspan=3)
        _lbl_lowest_key.grid(row=0, column=3)
        _lbl_highest_key.grid(row=0, column=4)
        _lbl_pitch.grid(row=0, column=5)

        # Variables Initialize
        self.inst_name = tk.StringVar(self, 'Instrument')
        self.lowest_key = tk.StringVar(self, '1')
        self.highest_key = tk.StringVar(self, '40')
        self.pitch = tk.DoubleVar(self, 440)

        # Variables set tk types
        _inst_name = ttk.Entry(self, textvariable=self.inst_name)
        _lowest_key = ttk.Entry(self, textvariable=self.lowest_key)
        _highest_key = ttk.Entry(self, textvariable=self.highest_key)
        _pitch = ttk.Entry(self, textvariable=self.pitch)
        _button = ttk.Button(self, text="Update Instrument", command=self.update_notes)

        # Variables position
        _inst_name.grid(row=1, column=0, columnspan=3, sticky=tk.EW)
        _lowest_key.grid(row=1, column=3, sticky=tk.EW)
        _highest_key.grid(row=1, column=4, sticky=tk.EW)
        _pitch.grid(row=1, column=5, sticky=tk.EW)
        _button.grid(row=0, column=6, rowspan=2, columnspan=3, sticky=tk.S)

        # add heading labels for Notes
        for i, name in enumerate(['Number', 'Name', 'Frequency', 'Length(mm)', 'Material',
                                  'Diameter(mm)', 'Count', 'Force(kgF)']):
            ttk.Label(self, text=name, anchor=tk.CENTER).grid(row=2, column=i, sticky=tk.EW)
            self.grid_columnconfigure(i,
                                      weight=1,
                                      minsize=75 if i in {0, 1, 2, 7} else 50)

        # bindings
        general_functions.bind_highlighting_on_focus(_inst_name, _lowest_key, _highest_key, _pitch)

        self.notes = dict()

    def update_notes(self, *args):
        """
        update the notes shown based on the lowest and highest keys given,
        destroys notes outside of the given range
        """
        note_numbers = list(range(self.get_lowest_key(), self.get_highest_key() + 1))
        # add new notes
        for nt in note_numbers:
            if nt in self.notes:
                continue
            self.notes[nt] = Note(self, nt)
        # delete no longer required Notes
        for k in list(self.notes.keys()):
            if k not in set(note_numbers):
                self.notes[k].destroy()
                self.notes.pop(k)
        # update frequencies
        for k, nt in self.notes.items():
            nt.calculate_frequency()

    def get_name(self) -> str:
        """ get the given Instrument name as a string """
        return self.inst_name.get()

    def get_pitch(self) -> float:
        """ get Instrument pitch as a float"""
        return self.pitch.get()

    def get_lowest_key(self) -> int:
        """ get lowest key as an integer """
        return general_functions.note_name_to_number(self.lowest_key.get())

    def get_highest_key(self) -> int:
        """ get highest key as an integer """
        return general_functions.note_name_to_number(self.highest_key.get())

    def apply_to_note(self, function: typing.Callable[[Note], any], note_number: int | str):
        """
        Apply function to a single note
        :param function: any function, applied as function(note)
        :param note_number: any note, given as std number (A0=1) or scientific name 'A#2'
        """
        if isinstance(note_number, str):
            note_number = general_functions.note_name_to_number(note_number)
        if note_number not in self.notes.items():
            return
        return function(self.notes[note_number])

    def apply_to_note_list(self, function: typing.Callable[[Note], None], note_list: list[int | str]):
        """
        Apply function to each note in the note list given
        :param function: any function, applied as function(note)
        :param note_list: list of notes, given as std number (A0=1) or Scientific Name 'A#2' or a combination of both
        """
        note_list = [var if isinstance(
            var, int) else general_functions.note_name_to_number(var) for var in note_list]
        for note in note_list:
            self.apply_to_note(function, note)

    def apply_to_all_notes(self, function: typing.Callable[[Note], None]):
        """
        Apply function to all notes in the Instrument
        :param function: any function, applied as function(note)
        """
        for k, note in self.notes.items():
            function(note)

    def iter_notes(self) -> typing.Iterator[Note]:
        """
        Iterate through each note in the Instrument starting from lowest note to highest note
        :returns: each Note in the Instrument from lowest to highest
        """
        for _, note in self.notes.items():
            yield note

    def note_list(self) -> list[Note]:
        """ get a list of all Notes currently in the Instrument """
        return list(self.notes.values())

    def state_import(self, data: dict):
        """
        Convert dict of input fields to an Instrument, includes calls for Note fields.
        This resets all current notes.
        """
        for k_, note in self.notes.items():
            note.destroy()
        self.notes = dict()
        self.inst_name.set(data['inst_name'])
        self.lowest_key.set(data['lowest_key'])
        self.highest_key.set(data['highest_key'])
        self.pitch.set(float(data['pitch']))
        self.update_notes()
        for key, var in self.notes.items():
            key = int(key)
            var.state_import(data['notes'][str(key)])

    def state_export(self) -> dict:
        """ convert all input fields to a dictionary, this includes all Notes and their inputs"""
        note_dict = {k: n_.state_export() for k, n_ in self.notes.items()}
        return dict(inst_name=self.inst_name.get(),
                    lowest_key=self.lowest_key.get(),
                    highest_key=self.highest_key.get(),
                    pitch=self.pitch.get(),
                    notes=note_dict)

    def get_next_note_input(self, note_number: int, input_pos: int, note_increment=0, input_increment=0):
        """
        Used for binding <Enter>
        :param note_number: integer representation of the note
        :param input_pos: position in the input items list of a Note
        :param note_increment: number of positions to move vertically - positive moves down
        :param input_increment: number of positions to move horizontally - positive moves right
        """
        input_count = 4
        note_number += note_increment
        input_pos += input_increment

        if input_pos % input_count:
            note_number += input_pos // input_count
            input_pos = input_pos % input_count

        if note_number > max(self.notes):
            note_number = min(self.notes)
        elif note_number < min(self.notes):
            note_number = max(self.notes)

        next_note: Note = self.notes.get(note_number)
        next_note.set_focus_to_input(input_pos)
