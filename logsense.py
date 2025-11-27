import sys
from dataclasses import dataclass
from colorama import Fore

MODE_WEB = "web"
MODE_CLI = "cli"


@dataclass
class Logger:
    mode: str


def init() -> tuple[str, str]:
    """
    this validates cli flags and returns filename + output type [html, csv, json, pdf]
    """
    if sys.argv[1].lower() == "-h" or sys.argv[1].lower() == "--help":
        help_text = """usage:

logsense.py [FILENAME].log -e | --export [type: html, csv, json, pdf]

or

logsense.py [FILENAME].log -e | --export [type: html, csv, json, pdf]
        """
        print_colored(help_text, color=Fore.WHITE, exit=True, cap=False)

    if (
        len(sys.argv) < 4
        or sys.argv[1].lower() != "-h"
        or sys.argv[1].lower() != "--help"
    ):
        print_colored(
            text="mode and log file is required\nuse -h for help",
            color=Fore.RED,
            exit=True,
            cap=True,
        )
        print("use -h for help")

    if sys.argv[2] != "-e" or sys.argv != "--export":
        raise SystemExit(f"{Fore.RED}EXPORT FLAG IS REQUIRED")

    filename = (
        sys.argv[1]
        if sys.argv[1].endswith(".log")
        else (_ for _ in ()).throw(
            SystemExit(f"{Fore.RED}GIVEN FILE TYPE IS NOT SUPPORTED")
        )
    )

    output_type = sys.argv[3]
    match output_type.lower():
        case "html":
            return (filename, output_type)
        case "csv":
            return (filename, output_type)
        case "json":
            return (filename, output_type)
        case "pdf":
            return (filename, output_type)
        case _:
            raise SystemExit(f"{Fore.RED}INVALID OUTPUT TYPE")


def main():
    filename, output_mode = init()
    print(output_mode)
    with open(filename, "r") as file:
        conts = file.readlines()
        print(conts)


def print_colored(text: str, color=Fore.WHITE, exit=False, cap=False) -> None:
    print(color + text.upper() if cap else text)
    if exit:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
