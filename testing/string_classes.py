import unittest

from instrument import Distance, Force, Density
from instrument.instrument_classes import note_name_to_number


class MyTestCase(unittest.TestCase):
    def test_note_name_to_number(self):
        self.assertEqual(note_name_to_number("C-1"), -8)
        self.assertEqual(note_name_to_number("C0"), 4)
        self.assertEqual(note_name_to_number("A"), 1)
        self.assertEqual(note_name_to_number("A4"), 49)

    def test_Distance(self):
        # convert to self
        self.assertEqual(Distance(mm=10).mm(), 10)
        self.assertEqual(Distance(cm=1).cm(), 1)
        self.assertEqual(Distance(m=1).m(), 1)
        # convert to other
        self.assertEqual(Distance(mm=10).cm(), 1)
        self.assertEqual(Distance(mm=1000).m(), 1)
        self.assertEqual(Distance(cm=1).mm(), 10)
        self.assertEqual(Distance(cm=1).m(), 0.01)
        self.assertEqual(Distance(m=1).mm(), 1000)
        self.assertEqual(Distance(m=1).cm(), 100)

    def test_Force(self):
        self.assertEqual(Force(kg_m_s2=10).g_cm_s2(), 1000000)
        self.assertEqual(Force(kg_m_s2=10).kg_m_s2(), 10)
        self.assertEqual(Force(g_cm_s2=10).kg_m_s2(), 0.0001)
        self.assertEqual(Force(g_cm_s2=10).g_cm_s2(), 10)

    def test_Density(self):
        self.assertEqual(Density(kg_m3=1).g_cm3(),0.001)
        self.assertEqual(Density(kg_m3=1).kg_m3(), 1)
        self.assertEqual(Density(g_cm3=10).kg_m3(), 10000)
        self.assertEqual(Density(g_cm3=10).g_cm3(), 10)


if __name__ == '__main__':
    unittest.main()
