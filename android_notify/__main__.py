import argparse
from .config import __version__

def print_version():
    text = f"android_notify: v{__version__}"
    border = '+'+'-'*(len(text) + 2)+'+'
    print(border)
    print(f'| {text} |')
    print(border)

def main():
    parser = argparse.ArgumentParser(description="Android Notify CLI")
    parser.add_argument('-v','--version', action='store_true', help="Show the version of android_notify")
    args = parser.parse_args()

    if args.version:
        print_version()
    # # Placeholder for the main functionality
    # print("Android Notify CLI is running...")
    # DEV:  pip install -e ., when edit and test project locally


if __name__ == "__main__":
    main()
