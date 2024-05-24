#!/usr/bin/python3

import argparse
import sys

class MultiKeyStaticDict:
    def __init__(self, initial_dict):
        self._dict = {}

        for keys, value in initial_dict.items():
            for key in keys:
                self._dict[key] = value
    
    def __getitem__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            print(f"Unit '{key}' does not exist.")
            return None

    def keys(self):
        return self._dict.keys()

INT_LITERALS = ["0b", "0", "0x"]
UNITS = MultiKeyStaticDict({
    ("b ", "bit")      : 1,
    ("N ", "nibble")   : 4,
    ("B ", "byte")     : 8,

    ("KB", "kilobyte") : 10 ** 3 * 8,
    ("MB", "megabyte") : 10 ** 6 * 8,
    ("GB", "gigabyte") : 10 ** 9 * 8,
    ("TB", "terabyte") : 10 ** 12 * 8,
    ("PB", "petabyte") : 10 ** 15 * 8,
    ("EB", "exabyte")  : 10 ** 18 * 8,
    ("ZB", "zettabyte"): 10 ** 21 * 8,
    ("YB", "yottabyte"): 10 ** 24 * 8,

    ("KiB", "kibibyte"): 2 ** 10 * 8,
    ("MiB", "mebibyte"): 2 ** 20 * 8,
    ("GiB", "gibibyte"): 2 ** 30 * 8,
    ("TiB", "tebibyte"): 2 ** 40 * 8,
    ("PiB", "pebibyte"): 2 ** 50 * 8,
    ("EiB", "exbibyte"): 2 ** 60 * 8,
    ("ZiB", "zebibyte"): 2 ** 70 * 8,
    ("YiB", "yobibyte"): 2 ** 80 * 8,

    ("Kb", "kilobit")  : 10 ** 3,
    ("Mb", "megabit")  : 10 ** 6,
    ("Gb", "gigabit")  : 10 ** 9,
    ("Tb", "terabit")  : 10 ** 12,
    ("Pb", "petabit")  : 10 ** 15,
    ("Eb", "exabit")   : 10 ** 18,
    ("Zb", "zettabit") : 10 ** 21,
    ("Yb", "yottabit") : 10 ** 24,

    ("Kib", "kibibit") : 2 ** 10,
    ("Mib", "mebibit") : 2 ** 20,
    ("Gib", "gibibit") : 2 ** 30,
    ("Tib", "tebibit") : 2 ** 40,
    ("Pib", "pebibit") : 2 ** 50,
    ("Eib", "exbibit") : 2 ** 60,
    ("Zib", "zebibit") : 2 ** 70,
    ("Yib", "yobibit") : 2 ** 80,
})

####################
# Input Validation #
####################

def is_base(val):
    return val.lower() in INT_LITERALS

def is_unit(val):
    if not val in UNITS.keys() or not val.lower() in UNITS.keys():
        raise argparse.ArgumentError(f"Unit {val} does not exist")

###################
# Parse Arguments #
###################

HELP_BASE = "A prefix to define the base.\nDecimal: No prefix required or '0d'\nBinary: '0b'\nOctal: '0o'\nHexadecimal: '0x'"
HELP_UNITS = "From bit over nibble and KB, TB up to YB. There are also Kb, KiB and Kib (also up to Yotta/Yobi). You can also write it out like 'bit' or 'kilobyte'."
parser = argparse.ArgumentParser(
        description="""
        Unit Conversion: Effortlessly convert between storage units like Megabytes (MB), Kilobytes (KB), Gigabytes (GB), and more (including binary prefixes like GiB).
        Base Conversion: Switch seamlessly between decimal (base 10), binary (base 2), hexadecimal (base 16), and octal (base 8) representations of numbers.
        """,
        )
parser.add_argument(
        'number',
        help="A number to input (any base)",
        )
parser.add_argument(
        '-f',
        '--from-base',
        help=HELP_BASE,
        )
parser.add_argument(
        '-u',
        '--from-unit',
        help=HELP_UNITS,
        )
parser.add_argument(
        '-o',
        '--to-base',
        help=HELP_BASE,
        )
parser.add_argument(
        '-t',
        '--to-unit',
        help=HELP_UNITS,
        )
parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="If set outputs additional information",
        )
args = parser.parse_args()

UNIT = "KiLoByTe".lower()
print(UNITS[UNIT])
