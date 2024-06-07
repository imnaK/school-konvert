#!/usr/bin/python3

from typing import Dict, Tuple, KeysView, Any
import argparse
import sys

class MultiKeyStaticDict:
    def __init__(self, initial_dict: Dict[tuple, int]):
        self._dict: Dict[str, int] = {}

        for keys, value in initial_dict.items():
            for key in keys:
                self._dict[key] = value
    
    def __getitem__(self, key: str) -> int:
        try:
            return self._dict[key]
        except KeyError:
            raise KeyError(f"Key '{key}' does not exist.")

    def keys(self) -> KeysView[str]:
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
    ("b", "bit")       : 1,
    ("N", "nibble")    : 4,
    ("B", "byte")      : 8,

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

ALNUM_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
ALNUM_DICT = {val: idx for idx, val in enumerate(ALNUM_LIST)}
DELIMITER = "."
BASE_MIN = 2
BASE_MAX = 36

def type_alphanumeric(val: str) -> Tuple[str, int]:
    delimiter_pos = val.find(DELIMITER) 
    delimiter_offset = len(val) - delimiter_pos
    
    if delimiter_pos == -1:
        delimiter_offset = 0
    else:
        val = val[:delimiter_pos] + val[delimiter_pos + 1:]

    if all(c in ALNUM_LIST for c in val.lower()):
        return (val.lower(), delimiter_offset)
    
    raise argparse.ArgumentTypeError(f"Number '{val}' may exist, but this program does not support it.")

def type_base(val: str) -> int:
    bases_list = list(BASES.keys())

    if val.lower() in bases_list:
        return BASES[val.lower()]
    else:
        number_base = base_to_int(val, BASES["decimal"])
        if BASE_MIN <= number_base <= BASE_MAX:
            return number_base
    
    raise argparse.ArgumentTypeError(f"Base '{val}' may exist, but this program does not support it.")

def type_unit(val: str) -> int:
    units_list = list(UNITS.keys())

    if val in units_list:
        return UNITS[val]
    elif val.lower() in units_list:
        return UNITS[val.lower()]
    
    raise argparse.ArgumentTypeError(f"Unit '{val}' may exist, but this program does not support it.")

###################
# Parse Arguments #
###################

def get_arguments() -> Any:
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
            help=f"A number to input (any base from {BASE_MIN} to {BASE_MAX})",
            type=type_alphanumeric,
            )
    parser.add_argument(
            "-b",
            "--from-base",
            help=HELP_BASE,
            type=type_base,
            default="decimal",
            )
    parser.add_argument(
            "-u",
            "--from-unit",
            help=HELP_UNITS,
            type=type_unit,
            default="bit",
            )
    parser.add_argument(
            "-o",
            "--to-base",
            help=HELP_BASE,
            type=type_base,
            default="decimal",
            )
    parser.add_argument(
            "-t",
            "--to-unit",
            help=HELP_UNITS,
            type=type_unit,
            default="bit",
            )

    return parser.parse_args()

#####################
# Convert Functions #
#####################

def float_to_int(num: float) -> int:
    if num < 0:
        return -(float_to_int(-num))

    num_str = str(num)
    num_whole = num_str.split(".")[0]

    res = 0
    for digit in num_whole:
        digit_num = ord(digit) - 48
        res = res * 10 + digit_num
    return res

def base_to_int(num: str, base: int) -> int:
    res = 0
    for i in num:
        c = ALNUM_DICT[i]
        if c + 1 > base:
            raise ValueError(f"Number '{num}' is not of base '{base}'.")
        res = c + base * res
    return res

def int_to_base(num: int, base: int) -> str:
    res = ""
    while num > 0:
        res = ALNUM_LIST[float_to_int(num % base)] + res
        num = num // base
    return res

def shift_by_offset(num: int, base: int, offset: int):
    return num * base ** -offset

###########
# Program #
###########

def main() -> int:
    args = get_arguments()    

    (num, delimiter_offset) = args.number

    print("num:", num)
    num = base_to_int(num, args.from_base)
    print("base_to_int:", num)
    num = shift_by_offset(num, args.from_base, delimiter_offset)
    print("shift_by_offset:", num)
    num = num / args.from_unit * args.to_unit
    print("unit calculation:", num)
    num = int_to_base(num, args.to_base)
    print("int_to_base:", num)

    print("base - number - unit")
    print(f"in :\t{args.from_base}\t{args.number[0]}\t{args.from_unit}")
    print(f"out:\t{args.to_base}\t{num}\t{args.to_unit}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# notes will be removed later, shouldn't be here in the first place tho
# 123.45 = 12345 / b^2
