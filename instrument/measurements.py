class Distance:
    _var: float  # millimeters

    def __init__(self, arg=None, mm: float = None, cm: float = None, m: float = None):
        if isinstance(arg,str):
            self._var = float(arg.replace('mm', ''))
        elif  mm:
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

    def __init__(self,arg=None, newton: float = None, kg_m_s2: float = None, dyne: float = None, g_cm_s2: float = None):
        kg_m_s2 = newton or kg_m_s2
        g_cm_s2 = dyne or g_cm_s2
        if isinstance(arg,str):
            self._var = float(arg.replace('kg-f','')) / 0.101971621297793
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
        return f'{self.kg_force():.2f}kg-f'


class Density:
    _var: float  # gcm3

    def __init__(self, arg=None, g_cm3: float = None, kg_m3: float = None):
        if isinstance(arg, str):
            g_cm3 = arg.replace('gm/cm³','')
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
