"""
String Calculator for early keyboard instruments.
"""
import definitions
import instrument

test_harpsichord = []
with open(definitions.ROOT_DIR / 'test_data_files/test_harpsichord.csv', 'r') as f:
    for line in f.readlines():
        line = line.strip()
        l, d, c, x = line.split(',')
        test_harpsichord.append(
            (c, l, d,x)
        )



if __name__ == '__main__':
    harpsichord = instrument.Instrument(9, 71, 425)
    i=0
    for note in harpsichord.iter_notes():
        note.set_wire(*test_harpsichord[i])
        i += 1
    print(harpsichord)

    instrument.plot_instrument(harpsichord)
    print(1)
