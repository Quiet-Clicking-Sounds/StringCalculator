from pathlib import Path
ROOT_DIR = Path(__file__).parent
WIRE_TYPE_CSV = ROOT_DIR / "interface/standard_wire_types.csv"
CACHE_MAX_AGE_SEC = 100

note_names = ('A', 'A♯', 'B', 'C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯')

file_types = (
    ('json files', '*.json'),
    ('All files', '*.*')
)