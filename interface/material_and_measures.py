from __future__ import annotations

import re

import definitions

_extraction_for_numbers_ = re.compile(r'\d+(?:\.\d*)?')


def extract_numeric(var: str) -> float:
    var = _extraction_for_numbers_.findall(var)[0]
    return float(var)


class Distance:
    _var: float  # millimeters

    def __init__(self, arg=None, mm: float = None, cm: float = None, m: float = None):
        if isinstance(arg, str):
            self._var = extract_numeric(arg)
        elif mm:
            self._var: float = float(mm)
        elif cm:
            self._var: float = float(cm) * 10
        elif m:
            self._var: float = float(m) * 1000
        else:
            raise ValueError('accepted type not given')

    def mm(self):
        return self._var

    def cm(self):
        return self._var / 10

    def m(self):
        return self._var / 1000

    def __str__(self):
        return f'{self._var}mm'


class Force:
    _var: float  # newtons

    def __init__(self, arg=None, newton: float = None, kg_m_s2: float = None, dyne: float = None,
                 g_cm_s2: float = None):
        kg_m_s2 = newton or kg_m_s2
        g_cm_s2 = dyne or g_cm_s2
        if isinstance(arg, str):
            self._var = extract_numeric(arg) / 0.101971621297793
        elif kg_m_s2:
            self._var = float(kg_m_s2)
        elif g_cm_s2:
            self._var = float(g_cm_s2) / 100000
        else:
            raise ValueError('accepted type not given')

    def kg_m_s2(self):
        return self._var

    def g_cm_s2(self):
        return self._var * 100000

    def kg_force(self):
        return self._var * 0.101971621297793

    dyne = g_cm_s2
    newton = kg_m_s2

    def __str__(self):
        return f'{self.kg_force():10.3f}kg-f'


class Density:
    _var: float  # gcm3

    def __init__(self, arg=None, g_cm3: float = None, kg_m3: float = None):
        if isinstance(arg, str):
            self._var = extract_numeric(arg)
        if g_cm3:
            self._var: float = float(g_cm3)
        elif kg_m3:
            self._var: float = float(kg_m3) / 1000
        else:
            raise ValueError('accepted type not given')

    def g_cm3(self):
        return self._var

    def kg_m3(self):
        return self._var * 1000

    def __str__(self):
        return f'{self._var:.2f}gm/cm³'


class WireMaterial:
    """
    WireMaterial used to define
    """
    _code_dict: dict[str, WireMaterial] = {}
    _name_dict: dict[str, WireMaterial] = {}

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

    def __hash__(self):
        return hash((self.code, self.name, self.density))

    def delete(self):
        """
        Deletion routine to remove a given wire from the available stock types.
        This routine does not remove the type from memory, it only stops it being available as a new wire type.
        """
        self._code_dict.pop(self.code)
        self._name_dict.pop(self.name)

    def __str__(self, long=False):
        if long:
            return f'{self.code}: {self.density} kg/m^2 | {self.name}'
        return f'{self.code}'

    def __eq__(self, other: WireMaterial):
        return self.code == other.code and self.density == other.density and self.name == other.name

    @classmethod
    def get_by_code(cls, code: str) -> WireMaterial:
        """
        get :class:`WireMaterial` item by code \n
        :param code: given code for a wire
        """
        return cls._code_dict.get(code, None)

    @classmethod
    def get_by_name(cls, name: str) -> WireMaterial:
        """
        get :class:`WireMaterial` item by name \n
        :param name: given name for a wire
        """
        return cls._name_dict[name]

    @classmethod
    def print_types(cls):
        """ print each material currently available """
        for k, material in cls._name_dict.items():
            print(f"{material.code} - {material.name} - {str(material.density)}")

    @classmethod
    def material_list(cls) -> list[tuple[str, str, str]]:
        """ return material list """
        mat_list = []
        for k, material in cls._name_dict.items():
            mat_list.append((
                str(material.code),
                str(material.name),
                str(material.density)
            ))
        return mat_list

    @classmethod
    def code_name_list(cls) -> list[str]:
        """ return human readable code + name of every material in a list """
        return [f'{material.code} {material.name}' for k, material in cls._name_dict.items()]


with open(definitions.WIRE_TYPE_CSV, 'r') as f:
    # import standard wire materials
    for line in f.readlines():
        line = line.strip()
        c, n, d = line.split(',')
        WireMaterial(c, n, Density(kg_m3=float(d)))
