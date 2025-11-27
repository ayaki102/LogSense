import sys
from colorama import Fore


def main():
    if len(sys.argv) < 3:
        print_colored(text="mode and log file is required, ", color=Fore.RED, exit=True)
        print("use -h for help")

    mode = (
        sys.argv[1]
        if sys.argv[1].lower() == "cli" or sys.argv[1].lower() == "web"
        else (_ for _ in ()).throw(
            SystemExit(f"{Fore.RED}given file type is not supported")
        )
    )

    filename = (
        sys.argv[2]
        if sys.argv[2].endswith(".log")
        else (_ for _ in ()).throw(
            SystemExit(f"{Fore.RED}given file type is not supported")
        )
    )

    if mode is not "cli" or "web":
        raise SystemExit("invalid mode")

    with open(filename, "r") as file:
        conts = file.readlines()
        print(conts)


def print_colored(text: str, color=Fore.WHITE, exit=False) -> None:
    print(color + text)
    if exit:
        raise SystemExit(1)


def print_help() -> None:
    print("""
usage:


logsense.py cli [FILENAME].log --export [type: html, csv, json, pdf]

or

logsense.py web [FILENAME].log --export [type: html, csv, json, pdf]
""")


if __name__ == "__main__":
    main()
