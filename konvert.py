#!/usr/bin/python3

from typing import List, Dict, Tuple, KeysView, ItemsView, Any
import argparse
import sys
import threading
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import json
import webbrowser

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


BASES_RAW = {
    ("binary", "bin"): 2,
    ("ternary",): 3,
    ("quaternary",): 4,
    ("quinary",): 5,
    ("senary", "seximal"): 6,
    ("septimal", "septinary", "septenary"): 7,
    ("octal", "oct"): 8,
    ("nonary", "nonal"): 9,
    ("decimal", "dec", "denary"): 10,
    ("undecimal", "unodecimal", "undenary"): 11,
    ("duodecimal", "dozenal"): 12,
    ("tredecimal", "tridecimal"): 13,
    ("quattuordecimal", "quadrodecimal", "tetradecimal"): 14,
    ("quindecimal", "pentadecimal"): 15,
    ("hexadecimal", "hex", "sexadecimal", "sedecimal"): 16,
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
UNITS_RAW = {
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
BASES = MultiKeyStaticDict(BASES_RAW)
UNITS = MultiKeyStaticDict(UNITS_RAW)

####################
# HTML WebUI Stuff #
####################

WEBUI_HOST = "localhost"
WEBUI_PORT = 42069
WEBUI_BACKEND_ENDPOINT = "/backend"
WEBUI_SHUTDOWN_ENDPOINT = "/shutdown"
WEBUI_BASE_OPTIONS = "\n".join(
    [
        '<option value="{0}">{1}</option>'.format(
            val,
            str(val) + " | " + key[0].capitalize(),
        )
        for key, val in BASES_RAW.items()
    ]
)
WEBUI_UNIT_OPTIONS = "\n".join(
    [
        '<option value="{0}">{1}</option>'.format(
            val, key[0] + " | " + key[1].capitalize()
        )
        for key, val in UNITS_RAW.items()
    ]
)

WEBUI_HTML = (
    """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Konvert WebUI</title>
        <!-- reset styles -->
        <style>
            *,
            *::before,
            *::after {
                box-sizing: border-box;
                margin: 0;
                font-weight: normal;
            }

            html {
                scroll-behavior: smooth;
            }

            body {
                text-rendering: optimizeLegibility;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
        </style>
        <!-- own styles -->
        <style>
            /* colors */
            :root {
                --color-base: #191724;
                --color-surface: #1f1d2e;
                --color-overlay: #26233a;
                --color-muted: #6e6a86;
                --color-subtle: #908caa;
                --color-text: #e0def4;
                --color-love: #eb6f92;
                --color-gold: #f6c177;
                --color-rose: #ebbcba;
                --color-pine: #31748f;
                --color-foam: #9ccfd8;
                --color-iris: #c4a7e7;
                --color-highlight-low: #21202e;
                --color-highlight-med: #403d52;
                --color-highlight-high: #524f67;

                --default-radius: 1.25rem;
            }

            * {
                outline-color: var(--color-highlight-low);
                outline: none;
            }

            body {
                background-color: var(--color-base);
                background-image: radial-gradient(var(--color-surface) 0.125rem, transparent 0.125rem);
                background-size: 2.125rem 2.125rem;
                color: var(--color-text);
                font-family: monospace;
                font-size: 1rem;
            }

            .container-wrapper {
                padding: 2rem;
            }

            .container {
                margin: 0 auto;
                width: min(42rem, 100%);
            }

            .layout-duo {
                display: flex;
                gap: 1rem;
                flex-direction: column;
            }

            @media screen and (min-width: 768px) {
                .layout-duo {
                    flex-direction: row;
                }
            }

            form {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            label {
                display: flex;
                flex-direction: column;
                color: var(--color-subtle);
            }

            label > input,
            label > select {
                margin-top: 0.5rem;
            }

            input,
            select,
            #shutdown {
                appearance: none;
                padding: 0 1rem;
                height: 2.5rem;
                border: none;
                border-radius: var(--default-radius);
                background-color: var(--color-base);
                color: var(--color-text);
                font-family: monospace;
                font-size: 1rem;
                box-shadow: 0.25rem 0.25rem 1.5rem 0 #000b,
                    -0.25rem -0.25rem 1.5rem -0.75rem #fff5;
                transition: color 0.2s ease-out, background-color 0.2s ease-out, box-shadow 0.2s ease-out;
            }

            #shutdown {
                cursor: pointer;
                margin-top: 2rem;
                float: right;
                color: var(--color-base);
                background-color: var(--color-love);
            }

            input:focus,
            input:disabled,
            select:focus,
            select:disabled,
            #shutdown:active {
                box-shadow: 0.25rem 0.25rem 1.5rem 0 transparent,
                    -0.25rem -0.25rem 1.5rem -0.75rem transparent,
                    inset 0 0 1rem -0.5rem black;
            }

            #shutdown:active {
                color: var(--color-love);
                background-color: var(--color-base);
            }

            input:invalid {
                color: var(--color-love);
            }

            h1 {
                text-align: center;
                font-weight: bold;
            }

            #error {
                background-color: var(--color-love);
                border-radius: var(--default-radius);
                text-align: center;
                align-content: center;
                padding: 0.25rem 1rem;
                margin-bottom: 1rem;
                color: var(--color-base);
                box-shadow: inset 0 0 1rem -0.5rem black;
            }

            b {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container-wrapper">
            <div class="container">
                <h1>Konvert WebUI</h1>
            </div>
        </div>
        <div class="container-wrapper">
            <div class="container">
                <div id="error" style="display: none">
                    <b>An expected error occured:</b><br />
                    Please input a valid number matching the base.
                </div>
            </div>
            <div class="container">
                <div class="layout-duo">
                    <form action="javascript:void(0);">
                        <label
                            >&emsp;Input Number
                            <input
                                id="input-number"
                                name="input-number"
                                type="text"
                                pattern="^[a-zA-Z0-9]+(\\.[a-zA-Z0-9]*)?$"
                            />
                        </label>
                        <label
                            >&emsp;From Base
                            <select id="from-base" name="from-base">
"""
    + WEBUI_BASE_OPTIONS
    + """
                            </select>
                        </label>
                        <label
                            >&emsp;From Unit
                            <select id="from-unit" name="from-unit">
"""
    + WEBUI_UNIT_OPTIONS
    + """
                            </select>
                        </label>
                    </form>

                    <form action="javascript:void(0);">
                        <label
                            >&emsp;Output Number
                            <input
                                id="output-number"
                                name="output-number"
                                type="text"
                                disabled
                            />
                        </label>
                        <label
                            >&emsp;To Base
                            <select id="to-base" name="to-base">"""
    + WEBUI_BASE_OPTIONS
    + """
                            </select>
                        </label>
                        <label
                            >&emsp;To Unit
                            <select id="to-unit" name="to-unit">"""
    + WEBUI_UNIT_OPTIONS
    + """
                            </select>
                        </label>
                    </form>
                </div>
                <button id="shutdown" onclick="shutdownWebUI()">Exit Konvert WebUI</button>
            </div>
        </div>

        <!-- script for communicating with the backend -->
        <script>
            // get all elements
            const errorEl = document.getElementById("error");
            const inputNumberEl = document.getElementById("input-number");
            const fromBaseEl = document.getElementById("from-base");
            const fromUnitEl = document.getElementById("from-unit");
            const outputNumberEl = document.getElementById("output-number");
            const toBaseEl = document.getElementById("to-base");
            const toUnitEl = document.getElementById("to-unit");
            // other variables for input validation
            const inputNumberRegex = /^[a-zA-Z0-9]+(\\.[a-zA-Z0-9]*)?$/;

            // add event listeners to the elements to check for updates
            inputNumberEl.addEventListener("input", handleChange);
            fromBaseEl.addEventListener("change", handleChange);
            fromUnitEl.addEventListener("change", handleChange);
            toBaseEl.addEventListener("change", handleChange);
            toUnitEl.addEventListener("change", handleChange);

            function updateError(message = "") {
                if (!message) {
                    errorEl.style.display = "none";
                } else {
                    errorEl.textContent = message;
                    errorEl.style.display = "block";
                }
            }

            function shutdownWebUI() {
                fetch(\""""
    + WEBUI_SHUTDOWN_ENDPOINT
    + """\")
                    .finally(() => {
                        window.close();
                    });
            }

            function handleChange(event) {
                const inputNumber = inputNumberEl.value;
                const inputValid = inputNumberRegex.test(inputNumber);
                
                if (!inputValid) {
                    updateError("Please input a valid number: a-z A-Z 0-9");
                    return;
                }

                updateError();
                updateOutputNumber();
            }

            function updateOutputNumber() {
                const queryParams = new URLSearchParams({
                    inputNumber: inputNumberEl.value,
                    fromBase: fromBaseEl.value,
                    fromUnit: fromUnitEl.value,
                    toBase: toBaseEl.value,
                    toUnit: toUnitEl.value,
                }).toString();

                fetch(\""""
    + WEBUI_BACKEND_ENDPOINT
    + """?\" + queryParams)
                    .then(res => res.text())
                    .then(mid => JSON.parse(mid))
                    .then(data => {
                        console.table(data);
                        console.log(typeof data);
                        outputNumberEl.value = data.result;
                    });
            }
        </script>
    </body>
</html>
"""
)


class WebUIHTTPHandler(http.server.SimpleHTTPRequestHandler):
    server_instance = None

    @classmethod
    def set_server_instance(cls, server):
        cls.server_instance = server

    def do_GET(self):
        # startpage
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(WEBUI_HTML.encode())
        # endpoint for talking to the backend
        elif self.path.startswith(WEBUI_BACKEND_ENDPOINT):
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            try:
                # get arguments from url
                inputNumber = params["inputNumber"][0]
                fromBase = params["fromBase"][0]
                fromUnit = params["fromUnit"][0]
                toBase = params["toBase"][0]
                toUnit = params["toUnit"][0]

                # argument sanitization
                try:
                    inputNumber = type_alphanumeric(inputNumber)
                    fromBase = type_base(fromBase)
                    fromUnit = type_unit(fromUnit)
                    toBase = type_base(toBase)
                    toUnit = type_unit(toUnit)
                except Exception as e:
                    raise e

                # conversation
                (num, delimiter_offset, is_negative) = inputNumber
                verbose("num, del, neg:", num, delimiter_offset, is_negative)

                num = base_to_int(num, fromBase)
                verbose("base_to_int:", num)

                if not delimiter_offset == 0:
                    num = shift_right(num, fromBase, delimiter_offset)
                    verbose("shift_right:", num)

                num = num * fromUnit / toUnit
                verbose("unit calculation:", num)

                num = float_to_base(num, toBase)
                verbose("float_to_base:", num)

                # add zero in front of number if it has "decimal' places and is below 1
                if num[0] == DELIMITER:
                    num = "0" + num

                # add negative sign if input number was negative
                if is_negative:
                    num = "-" + num

                # send happy response back to the client
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()

                # return the converted output to the webui
                res_data = {
                    "result": num,
                }
                self.wfile.write(json.dumps(res_data).encode())
                # self.wfile.write(json.dumps(response_data).encode())
            except (KeyError, ValueError) as e:
                # send sad response back to the client
                self.send_error(400, "Invalid parameters", str(e))
        # endpoint for shutting the server down via the frontend
        elif self.path.startswith(WEBUI_SHUTDOWN_ENDPOINT):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Shutting down...")
            threading.Thread(target=self.shutdown_server).start()
        # this page does not exist
        else:
            self.send_error(404)

    def shutdown_server(self):
        if self.server_instance:
            self.server_instance.shutdown()
            self.server_instance.server_close()


def open_browser():
    webbrowser.open_new_tab(f"http://{WEBUI_HOST}:{WEBUI_PORT}")


def start_webui():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", WEBUI_PORT), WebUIHTTPHandler) as httpd:
        WebUIHTTPHandler.set_server_instance(httpd)
        print(f"Serving WebUI at http://{WEBUI_HOST}:{WEBUI_PORT}")

        # open the webui in a new tab in a new thread
        threading.Thread(target=open_browser).start()

        # serve the webui endpoints via the tcp server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server interrupted by user")
        finally:
            httpd.server_close()
            print("Server closed")


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

    required_group = parser.add_mutually_exclusive_group(required=True)

    required_group.add_argument(
        "-w",
        "--web-ui",
        help="Starts a webserver for graphical input",
        action="store_true",
    )
    required_group.add_argument(
        "-n",
        "--number",
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
    for _ in range(10):
        if num_decimals == 0:
            break
        num_decimals *= base
        digit = float_to_int(num_decimals)
        res_decimals += ALNUM_LIST[digit]
        num_decimals -= digit

    return (res + DELIMITER + res_decimals) if res_decimals else res


def shift_right(num: int, base: int, offset: int) -> float:
    return num / base**offset


########
# Util #
########


def fill_spaces(text: str, n: int) -> str:
    return (" " * (n - len(text))) + text


def output_as_table(two_dim_list: List[List[str]]):
    col_lenghts = [0] * max([len(inner_list) for inner_list in two_dim_list])

    for row in range(len(two_dim_list)):
        for col in range(len(two_dim_list[row])):
            col_len = len(str(two_dim_list[row][col]))
            if col_lenghts[col] < col_len:
                col_lenghts[col] = col_len

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
    return ""


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

    # if webui flag is set, start it
    if args.web_ui:
        start_webui()
        # return after exiting webui
        return 0

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

    # add zero in front of number if it has "decimal' places and is below 1
    if num[0] == DELIMITER:
        num = "0" + num

    # add negative sign if input number was negative
    if is_negative:
        num = "-" + num

    # only print number as output if flag is set, else make a fancy table output
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
