import argparse
import os
import shutil
from .config import __version__

BUILD_PATHS = [
    os.path.join(".buildozer", "android", "platform", "build-arm64-v8a_armeabi-v7a", "build", "python-installs"),
    os.path.join(".buildozer", "android", "platform", "build-arm64-v8a_armeabi-v7a", "dists"),
# ".buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/python-installs",
# ".buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists",
]

def print_version():
    text = f"android_notify: v{__version__}"
    border = '+'+'-'*(len(text) + 2)+'+'
    print(border)
    print(f'| {text} |')
    print(border)

def cmd_prune(args):
    project_path = str(os.path.abspath(args.path))
    items = []

    for rel in BUILD_PATHS:
        root = os.path.join(project_path, rel)
        if not os.path.isdir(root):
            continue
        for dirpath, dir_names, filenames in os.walk(root):
            for name in dir_names + filenames:
                if name.startswith("android_notify"):
                    items.append(os.path.join(dirpath, name))

    if not items:
        print("No android_notify items found.")
        return

    print("\n=== android_notify items found ===")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    print("==================================\n")

    ans = input("Delete these? (y/N) ").strip().lower()
    if ans == "y":
        items.sort(key=len, reverse=True)
        for item in items:
            if not os.path.exists(item):
                continue
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print(f"  Deleted: {item}")
        print("Done.")
    else:
        print("Skipped.")

def main():
    parser = argparse.ArgumentParser(description="Android Notify CLI")
    parser.add_argument('-v', '--version', action='store_true', help="Show the version of android_notify")

    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    prune_parser = subparsers.add_parser('prune', help='Remove old android_notify build artifacts from .buildozer')
    prune_parser.add_argument('-p', '--path', default='.', help='Path to the project directory (default: current directory)')

    args = parser.parse_args()

    if args.version:
        print_version()
    elif args.command == 'prune':
        cmd_prune(args)
    elif args.command is None:
        parser.print_help()

if __name__ == "__main__":
    main()
