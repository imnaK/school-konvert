#!/usr/bin/python3

from typing import Iterator, List, Dict, Tuple, KeysView, ItemsView, Any
import argparse
import sys

flag_verbose = False
flag_number_only = False


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

    def items(self) -> ItemsView[str, int]:
        return self._dict.items()


BASES = MultiKeyStaticDict(
    {
        ("bin", "binary"): 2,
        ("ternary",): 3,
        ("quaternary",): 4,
        ("quinary",): 5,
        ("senary", "seximal"): 6,
        ("septimal", "septinary", "septenary"): 7,
        ("oct", "octal"): 8,
        ("nonary", "nonal"): 9,
        ("dec", "decimal", "denary"): 10,
        ("undecimal", "unodecimal", "undenary"): 11,
        ("duodecimal", "dozenal"): 12,
        ("tredecimal", "tridecimal"): 13,
        ("quattuordecimal", "quadrodecimal", "tetradecimal"): 14,
        ("quindecimal", "pentadecimal"): 15,
        ("hex", "hexadecimal", "sexadecimal", "sedecimal"): 16,
        ("septendecimal", "heptadecimal"): 17,
        ("octodecimal",): 18,
        ("undevicesimal", "nonadecimal", "enneadecimal"): 19,
        ("vigesimal",): 20,
        ("unvigesimal",): 21,
        ("duovigesimal",): 22,
        ("trivigesimal",): 23,
        ("quadravigesimal", "tetravigesimal"): 24,
        ("pentavigesimal",): 25,
        ("hexavigesimal",): 26,
        ("septemvigesimal", "heptavigesimal"): 27,
        ("octovigesimal",): 28,
        ("enneavigesimal",): 29,
        ("trigesimal",): 30,
        ("untrigesimal",): 31,
        ("duotrigesimal",): 32,
        ("tritrigesimal",): 33,
        ("tetratrigesimal",): 34,
        ("pentatrigesimal",): 35,
        ("hexatrigesimal",): 36,
    }
)
UNITS = MultiKeyStaticDict(
    {
        ("b", "bit"): 1,
        ("N", "nibble"): 4,
        ("B", "byte"): 8,
        ("KB", "kilobyte"): 10**3 * 8,
        ("MB", "megabyte"): 10**6 * 8,
        ("GB", "gigabyte"): 10**9 * 8,
        ("TB", "terabyte"): 10**12 * 8,
        ("PB", "petabyte"): 10**15 * 8,
        ("EB", "exabyte"): 10**18 * 8,
        ("ZB", "zettabyte"): 10**21 * 8,
        ("YB", "yottabyte"): 10**24 * 8,
        ("KiB", "kibibyte"): 2**10 * 8,
        ("MiB", "mebibyte"): 2**20 * 8,
        ("GiB", "gibibyte"): 2**30 * 8,
        ("TiB", "tebibyte"): 2**40 * 8,
        ("PiB", "pebibyte"): 2**50 * 8,
        ("EiB", "exbibyte"): 2**60 * 8,
        ("ZiB", "zebibyte"): 2**70 * 8,
        ("YiB", "yobibyte"): 2**80 * 8,
        ("Kb", "kilobit"): 10**3,
        ("Mb", "megabit"): 10**6,
        ("Gb", "gigabit"): 10**9,
        ("Tb", "terabit"): 10**12,
        ("Pb", "petabit"): 10**15,
        ("Eb", "exabit"): 10**18,
        ("Zb", "zettabit"): 10**21,
        ("Yb", "yottabit"): 10**24,
        ("Kib", "kibibit"): 2**10,
        ("Mib", "mebibit"): 2**20,
        ("Gib", "gibibit"): 2**30,
        ("Tib", "tebibit"): 2**40,
        ("Pib", "pebibit"): 2**50,
        ("Eib", "exbibit"): 2**60,
        ("Zib", "zebibit"): 2**70,
        ("Yib", "yobibit"): 2**80,
    }
)

####################
# Input Validation #
####################

ALNUM_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"
DELIMITER = "."
BASE_MIN = 2
BASE_MAX = 36


def get_abs(val: str) -> Tuple[str, bool]:
    negative_count = 0

    while val[0] in "-+":
        if val[0] == "-":
            negative_count += 1
        val = val[1:]
    is_negative = negative_count % 2 == 1

    return (val, is_negative)


def type_alphanumeric(val: str) -> Tuple[str, int, bool]:
    (val_form, is_negative) = get_abs(val.strip().lower())

    delimiter_pos = val_form.find(DELIMITER)
    delimiter_offset = None

    if delimiter_pos == -1:
        delimiter_offset = 0
    else:
        val_form = val_form.replace(DELIMITER, "")
        delimiter_offset = len(val_form) - delimiter_pos

    if all(c in ALNUM_LIST for c in val_form):
        return (val_form, delimiter_offset, is_negative)

    raise argparse.ArgumentTypeError(
        f"Number '{val}' may exist, but this program does not support it."
    )


def type_base(val: str) -> int:
    bases_list = list(BASES.keys())

    if val.lower() in bases_list:
        return BASES[val.lower()]
    else:
        number_base = base_to_int(val, BASES["decimal"])
        if BASE_MIN <= number_base <= BASE_MAX:
            return number_base

    raise argparse.ArgumentTypeError(
        f"Base '{val}' may exist, but this program does not support it."
    )


def type_unit(val: str) -> int:
    units_list = list(UNITS.keys())

    if val in units_list:
        return UNITS[val]
    elif val.lower() in units_list:
        return UNITS[val.lower()]

    raise argparse.ArgumentTypeError(
        f"Unit '{val}' may exist, but this program does not support it."
    )


###################
# Parse Arguments #
###################


def get_arguments() -> Any:
    HELP_BASE = f"Base range is from {BASE_MIN} to {BASE_MAX} and accepts numbers and also the common words."
    HELP_UNITS = "From bit over nibble and KB, TB up to YB. There are also Kb, KiB and Kib (also up to Yotta/Yobi). You can also write it out like 'bit' or 'kilobyte'."

    parser = argparse.ArgumentParser(
        description="""
            Unit Conversion: Effortlessly convert between storage units like Megabytes (MB), Kilobytes (KB), Gigabytes (GB), and more (including binary prefixes like GiB).
            Base Conversion: Switch seamlessly between any base representations of numbers. See below for the range of bases this program supports.
            """,
    )
    parser.add_argument(
        "-n",
        "--number",
        help=f"A number to input (any base from {BASE_MIN} to {BASE_MAX})",
        type=type_alphanumeric,
        required=True,
    )
    parser.add_argument(
        "-b",
        "--from-base",
        help=HELP_BASE,
        type=type_base,
        default="decimal",
    )
    parser.add_argument(
        "-a",
        "--to-base",
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
        "-t",
        "--to-unit",
        help=HELP_UNITS,
        type=type_unit,
        default="bit",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="More verbose output and mid-calculations",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--number-only",
        help="Only output the final number as a result",
        action="store_true",
    )

    return parser.parse_args()


#####################
# Convert Functions #
#####################


def float_to_int(num: float) -> int:
    if num < 0:
        return -(float_to_int(-num))

    num_str = str(num)
    num_whole = num_str.split(DELIMITER)[0]

    res = 0
    for digit in num_whole:
        digit_num = ALNUM_LIST.index(digit)
        res = res * 10 + digit_num
    return res


def base_to_int(num: str, base: int) -> int:
    res = 0
    for digit in num:
        n = ALNUM_LIST.index(digit)
        if n + 1 > base:
            raise ValueError(f"Number '{num}' is not of base '{base}'.")
        res = n + base * res
    return res


def float_to_base(num: float, base: int) -> str:
    res = ""
    num_whole = float_to_int(num)
    num_decimals = num - num_whole

    while num_whole > 0:
        res = ALNUM_LIST[float_to_int(num_whole % base)] + res
        num_whole //= base

    res_decimals = ""
    for i in range(10):
        if num_decimals == 0:
            break
        num_decimals *= base
        l = float_to_int(num_decimals)
        res_decimals += ALNUM_LIST[l]
        num_decimals -= l

    return (res + DELIMITER + res_decimals) if res_decimals else res


def shift_right(num: int, base: int, offset: int) -> float:
    return num / base**offset


########
# Util #
########


def fill_spaces(s: str, l: int) -> str:
    return (" " * (l - len(s))) + s


def output_as_table(two_dim_list: List[List[str]]):
    col_lenghts = [0] * max([len(inner_list) for inner_list in two_dim_list])

    for row in range(len(two_dim_list)):
        for col in range(len(two_dim_list[row])):
            col_len = len(str(two_dim_list[row][col]))
            if col_lenghts[col] < col_len:
                col_lenghts[col] = col_len

    col_sum = sum(col_lenghts)
    row_separator = (
        "+" + "+".join(["-" * (col_len + 2) for col_len in col_lenghts]) + "+"
    )
    for row in range(len(two_dim_list)):
        print(row_separator)
        print("|", end="")
        for col in range(len(two_dim_list[row])):
            print(
                " " + fill_spaces(str(two_dim_list[row][col]), col_lenghts[col]) + " |",
                end="",
            )
        print()
    print(row_separator)


def num_to_unit(num: int) -> str:
    for key, val in UNITS.items():
        if val == num:
            return key
    return None


###########
# Program #
###########


def init_flags(args):
    global flag_verbose, flag_number_only

    flag_verbose = args.verbose
    flag_number_only = args.number_only


def verbose(*o):
    global flag_verbose

    if flag_verbose:
        print(*o)


def main() -> int:
    global flag_number_only

    args = get_arguments()
    init_flags(args)

    (num, delimiter_offset, is_negative) = args.number
    verbose("num, del, neg:", num, delimiter_offset, is_negative)

    num = base_to_int(num, args.from_base)
    verbose("base_to_int:", num)

    if not delimiter_offset == 0:
        num = shift_right(num, args.from_base, delimiter_offset)
        verbose("shift_right:", num)

    num = num * args.from_unit / args.to_unit
    verbose("unit calculation:", num)

    num = float_to_base(num, args.to_base)
    verbose("float_to_base:", num)

    # add zero in front if decimal and below 1
    if num[0] == DELIMITER:
        num = "0" + num

    # add negative sign if negative
    if is_negative:
        num = "-" + num

    if flag_number_only:
        print(num)
    else:
        num_in = (
            ("-" if is_negative else "")
            + args.number[0][:-delimiter_offset]
            + (DELIMITER if not delimiter_offset == 0 else "")
            + args.number[0][-delimiter_offset:]
        )
        table = [
            ["", "Number", "Unit", "Base"],
            ["Input", num_in, num_to_unit(args.from_unit), args.from_base],
            ["Output", num, num_to_unit(args.to_unit), args.to_base],
        ]

        output_as_table(table)

    return 0


if __name__ == "__main__":
    sys.exit(main())
