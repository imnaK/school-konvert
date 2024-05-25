#!/usr/bin/python3

import argparse
from typing import List

class MultiKeyStaticDict:
    def __init__(self, initial_dict: dict):
        self._dict = {}

        for keys, value in initial_dict.items():
            for key in keys:
                self._dict[key] = value
    
    def __getitem__(self, key: str) -> int:
        try:
            return self._dict[key]
        except KeyError:
            print(f"Key '{key}' does not exist.")
            return None

    def keys(self) -> List[str]:
        return self._dict.keys()

BASES = MultiKeyStaticDict({
    ("bin", "binary")                                 : 2,
    ("ternary",)                                      : 3,
    ("quaternary",)                                   : 4,
    ("quinary",)                                      : 5,
    ("senary", "seximal")                             : 6,
    ("septimal", "septinary")                         : 7,
    ("oct", "octal")                                  : 8,
    ("nonary", "nonal")                               : 9,
    ("dec", "decimal", "denary")                      : 10,
    ("undecimal", "unodecimal", "undenary")           : 11,
    ("duodecimal", "dozenal")                         : 12,
    ("tredecimal", "tridecimal")                      : 13,
    ("quattuordecimal", "quadrodecimal")              : 14,
    ("quindecimal", "pentadecimal")                   : 15,
    ("hex", "hexadecimal", "sexadecimal", "sedecimal"): 16,
    ("septendecimal", "heptadecimal")                 : 17,
    ("octodecimal",)                                  : 18,
    ("undevicesimal", "nonadecimal")                  : 19,
    ("vigesimal",)                                    : 20,
    # 21
    # 22
    # 23
    ("quadravigesimal",)                              : 24,
    # 25
    ("hexavigesimal",)                                : 26,
    ("septemvigesimal",)                              : 27,
    # 28
    # 29
    ("trigesimal",)                                   : 30,
    # 31
    ("duotrigesimal",)                                : 32,
    # 33
    # 34
    # 35
    ("hexatrigesimal",)                               : 36,
})
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

def type_base(val: str) -> int:
    if val.lower() in BASES.keys():
        return BASES[val.lower()]
    else:
        number_base = int(val)
        if 2 <= number_base <= 36:
            return number_base

def type_unit(val: str) -> str:
    if val in UNITS.keys():
        return UNITS[val]
    elif val.lower() in UNITS.keys():
        return UNITS[val.lower()]

#####################
# Convert Functions #
#####################

def base_to_base(num: str, from_base: int, to_base: int):
   return None 

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
        "number",
        help="A number to input (any base)",
        type=str,
        )
parser.add_argument(
        "-b",
        "--from-base",
        help=HELP_BASE,
        type=type_base,
        )
parser.add_argument(
        "-u",
        "--from-unit",
        help=HELP_UNITS,
        type=type_unit,
        )
parser.add_argument(
        "-o",
        "--to-base",
        help=HELP_BASE,
        type=type_base,
        )
parser.add_argument(
        "-t",
        "--to-unit",
        help=HELP_UNITS,
        type=type_unit,
        )
args = parser.parse_args()

print(args)
