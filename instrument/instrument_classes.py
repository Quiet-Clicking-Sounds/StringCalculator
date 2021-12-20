from __future__ import annotations

import re
import typing
from math import pi

import definitions
from instrument.measurements import Distance, Force, Density

_note_names_ = ('A', 'A♯', 'B', 'C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯')


def note_name_to_number(name: str) -> int:
    """
    convert note names into standard scientific note numbers \n
    "A1" = 13, "C#" = 5, "D#20" = 247, "C♯4" = 53
    *matches negative numbers, DOES NOT MATCH FLAT* **♭**
    :param name: note in string format
    :return: standard note number
    """
    name = name.upper()
    name = name.replace('#', '♯')  # replace with correct hash mark
    match = re.match(r'([A-G][#♯]?)(-?\d*)', name)  # match letter (+sharp) (+ number)
    note_i = match.group(1)
    if match.group(2) == '':
        # checks for number after the letter (+ '#'), if none set to 0'th octave
        note_n = 0
    else:
        # set octave based on the final number
        note_n = int(match.group(2))
    # note = octave * 12 + note_position in `_note_name_` +1 (notes count from 1)
    note = note_n * 12 + _note_names_.index(note_i) + 1
    return note


def note_number_to_name(number: int) -> str:
    """
    convert standard note numbers to a note name \n
    5 = 'C#', 53='C#4'

    :param number: integer note number
    :return: string note name
    """

    name = _note_names_[(number - 1) % 12]
    octave = (number - 1) // 12
    return f'{name}{octave}'


class _WireMaterial:
    """
    _WireMaterial used to define
    """
    _code_dict: dict[str, _WireMaterial] = {}
    _name_dict: dict[str, _WireMaterial] = {}

    def __init__(self, code: str, name: str, density: Density):
        """
        :param code: reference code for wire type
        :param name: full name of wire type
        :param density: density of material in kg/m^2
        """
        self.code = code
        self.name = name
        self.density = density
        self._code_dict[self.code] = self
        self._name_dict[self.name] = self

    def delete(self):
        """
        Deletion routine to remove a given wire from the available stock types.
        This routine does not remove the type from memory, it only stops it being available as a new wire type.
        """
        self._code_dict.pop(self.code)
        self._name_dict.pop(self.name)

    def __str__(self):
        return f'{self.code}: {self.density} kg/m^2 | {self.name}'

    @classmethod
    def get_by_code(cls, code):
        """
        get :class:`_WireMaterial` item by code \n
        :param code: given code for a wire
        """
        return cls._code_dict[code]

    @classmethod
    def get_by_name(cls, name):
        """
        get :class:`_WireMaterial` item by name \n
        :param name: given name for a wire
        """
        return cls._name_dict[name]

    @classmethod
    def print_types(cls):
        """ print each material currently available """
        for k, material in cls._name_dict.items():
            print(f"{material.code} - {material.name} - {str(material.density)}")


with open(definitions.ROOT_DIR / "instrument/standard_wire_types.csv", 'r') as f:
    # import standard wire materials
    for line in f.readlines():
        line = line.strip()
        c, n, d = line.split(',')
        _WireMaterial(c, n, Density(kg_m3=float(d)))


class Note:
    """ Given note """
    instrument: Instrument
    wire_material: _WireMaterial
    length: Distance
    diameter: Distance
    std_note: int
    wire_count: int

    def __init__(self, instrument: Instrument, std_note: int):
        """
        :param instrument: parent :class:`Instrument`
        :param std_note: standard note number, A0 = 1, C0 = 4, A4 = 49
        """
        assert isinstance(std_note, int)
        self.instrument = instrument
        # note info
        self.std_note = std_note
        self.frequency = None
        self.calculate_frequency()

        # wire info
        # noinspection PyTypeChecker
        self.wire_count = None
        # noinspection PyTypeChecker
        self.wire_material = None
        # noinspection PyTypeChecker
        self.length = None
        # noinspection PyTypeChecker
        self.diameter = None

    def __str__(self):
        tension = ''
        if all((self.frequency, self.length.cm(), self.diameter.cm(), self.wire_material.density.g_cm3())):
            tension = f'| {self.force()}'

        return f'Note {self.std_note}: {note_number_to_name(self.std_note)} Frequency {self.frequency:.4f} hz {tension}'

    def calculate_frequency(self):
        """ calculate the frequency of `Note` based the pitch of A1 in the parent :class:`Insrument` """
        # frequency = 2 ** ((note_number - 49) / 12 ) * (frequency of A1)
        self.frequency = 2 ** ((self.std_note - 49) / 12) * self.instrument.pitch_a4()

    def set_material(self, code: str):
        """ :param code: wire material code given as string """
        self.wire_material: _WireMaterial = _WireMaterial.get_by_code(code)

    def set_length(self, length: Distance | float):
        """ :param length: :class:`Distance` or as millimeters """
        if not isinstance(length, Distance):
            length = Distance(mm=length)
        self.length: Distance = length

    def set_diameter(self, diameter: Distance | float):
        """ :param diameter: :class:`Distance` or as millimeters """
        if not isinstance(diameter, Distance):
            diameter = Distance(mm=diameter)
        self.diameter: Distance = diameter

    def set_wire_count(self, wire_count: int):
        """  number of wires used per note given as integer """
        self.wire_count: int = int(wire_count)

    def set_wire(self, code: str, length: Distance | float, diameter: Distance | float, wire_count=1):
        """
        Set wire information for the Note
        :param code: wire material code given as string
        :param length: wire length given as :class:`Distance` object or in millimeters
        :param diameter: wire diameter given as :class:`Distance` object or in millimeters
        :param wire_count: number of wires used per note given as integer (auto 1)
        """
        self.set_material(code)
        self.set_length(length)
        self.set_diameter(diameter)
        self.set_wire_count(wire_count)

    def force(self) -> Force:
        """
        calculate the tension and diameter of the wire using methods from \n
        `sound_from_wire_equation <https://www.school-for-champions.com/science/sound_from_wire_equation.htm>`_ \n
        --- **f** is the frequency in hertz (Hz) or cycles per second \n
        --- **L** is the length of the wire in centimeters (cm) \n
        --- **d** is the diameter of the wire in cm \n
        --- **T** is the tension on the wire in gm-cm/s² \n
        --- **π** is the Greek letter pi = 3.14 \n
        --- **δ** is the density of the wire in gm/cm³ (Greek letter small delta) \n

        :return: :class:`Tension` of the string as `T = πf²L²d²δ`
        """
        pi_hz = pi * self.frequency ** 2  # πf²
        le = self.length.cm() ** 2  # L²
        di = self.diameter.cm() ** 2  # d²
        den = self.wire_material.density.g_cm3()  # δ
        gcm = pi_hz * le * di * den
        return Force(g_cm_s2=gcm * self.wire_count)


class Instrument:
    """
    """
    notes: dict[int, Note]
    _pitch: float

    def __init__(self, lowest_key: str | int, highest_key: str | int, pitch: float = 440):
        """
        :param lowest_key: lowest key on the Instrument, given as std number (A0=1) or Scientific Name 'A#2'
        :param highest_key: lowest key on the Instrument, given as std number (A0=1) or Scientific Name 'A#2'
        :param pitch: frequency of note A1 in hz
        """
        self._pitch = pitch

        if isinstance(lowest_key, str):
            lowest_key: int = note_name_to_number(lowest_key)
        if isinstance(highest_key, str):
            highest_key: int = note_name_to_number(highest_key)

        self.notes = {i: Note(self, i) for i in range(lowest_key, highest_key + 1)}

    def drop_key(self, key: str | int) -> None:
        """
        :param key: key given as std number (A0=1) or Scientific Name 'A#2'
        :return:
        """
        self.notes.pop(note_name_to_number(key))

    def pitch_a4(self) -> float:
        """ get frequency of A1 in the :class:`Instrument`"""
        return self._pitch

    def set_pitch(self, pitch: float):
        """
        :param pitch: frequency of key A4 (note 49)
        :return: None
        """
        self._pitch = pitch
        # recalculate frequencies for each note based on pitch of A1
        for _, note in self.notes.items():
            note.calculate_frequency()

    def apply_to_note(self, function: typing.Callable[[Note], any], note_number: int | str):
        """
        Apply function to a single note
        :param function: any function, applied as function(note)
        :param note_number: any note, given as std number (A0=1) or scientific name 'A#2'
        """
        if isinstance(note_number, str):
            note_number = note_name_to_number(note_number)
        if note_number not in self.notes.items():
            return
        return function(self.notes[note_number])

    def apply_to_note_list(self, function: typing.Callable[[Note], None], note_list: list[int | str]):
        """
        Apply function to each note in the note list given
        :param function: any function, applied as function(note)
        :param note_list: list of notes, given as std number (A0=1) or Scientific Name 'A#2' or a combination of both
        """
        note_list = [var if isinstance(var, int) else note_name_to_number(var) for var in note_list]
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
