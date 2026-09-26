#!/usr/bin/env python3
"""
Print an image's alpha channel as ASCII art.

Android renders a status-bar small icon from its alpha mask and throws the RGB
away, so the transparency is the part that actually matters and the part most
easily lost in a re-export. This prints it so you can eyeball it.

Run with the system interpreter, which has Pillow:

    ./tests/scripts/preview_fallback_icon.py            # the shipped icons
    ./tests/scripts/preview_fallback_icon.py a.png b.jpg # any image(s)
    ./tests/scripts/preview_fallback_icon.py flet       # a shipped icon
    ./tests/scripts/preview_fallback_icon.py ~/img/x.png

Bare names are looked up in the shipped icon directory, so `flet` and
`flet-appicon.png` both work. Anything else is treated as a path, relative to
the current directory unless it is absolute.

An image with no alpha channel (a JPEG, say) converts to fully opaque and
prints as a solid block - which is the point: that is exactly what Android
would render from it.

The preview window is a fixed 2:1, so the shipped square icons are all shown
in full at the same visual scale. Non-square images are squashed to fit, which
is fine for reading an alpha structure but not a general-purpose viewer.

The .venv where pytest runs deliberately has no Pillow - the headless suite
installs no third-party packages at all - so run this with `python3`, not
`.venv/bin/python`.
"""

import os
import sys

ICON_DIR = os.path.join(
    # Resolved from this file rather than relative to the cwd, so the shipped
    # icons are found from anywhere in the repo.
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "android_notify",
    "fallback-icons",
)

# Order matters: it is the order a notification is most likely to need them in.
ICON_NAMES = ("kivy-appicon.png", "flet-appicon.png", "pydroid3-appicon.png")

WIDTH, HEIGHT = 56, 28


def resolve(argument):
    """Turn a command-line argument into a readable file path.

    Falls back to the shipped-icon directory so the common case needs no path.
    Returns None if nothing matched, so the caller can report every failure at
    once rather than one per run.
    """
    if os.path.isfile(argument):
        return argument

    for candidate in (argument, f"{argument}.png", f"{argument}-appicon.png"):
        path = os.path.join(ICON_DIR, candidate)
        if os.path.isfile(path):
            return path

    return None


def preview(path, label):
    from PIL import Image, UnidentifiedImageError

    try:
        rgba = Image.open(path).convert("RGBA")
    except (UnidentifiedImageError, OSError) as error:
        sys.exit(f"could not read {path} as an image: {error}")

    alpha = rgba.getchannel("A").resize((WIDTH, HEIGHT), Image.LANCZOS)

    print(f"--- alpha preview of {label} ({rgba.width}x{rgba.height}) ---")
    for y in range(HEIGHT):
        print(
            "".join(
                "#" if alpha.getpixel((x, y)) > 170
                else "+" if alpha.getpixel((x, y)) > 80
                else "." if alpha.getpixel((x, y)) > 20
                else " "
                for x in range(WIDTH)
            )
        )
    print()


def main(argv):
    # Pillow is checked here rather than imported at module scope: pytest
    # imports every file it scans, and a module-level failure would surface as
    # an INTERNALERROR rather than "no tests collected".
    try:
        import PIL.Image
    except ModuleNotFoundError:
        sys.exit(
            "Pillow is not installed in this interpreter.\n"
            "Run this with the system python3, which has it:\n"
            "    ./tests/scripts/preview_fallback_icon.py"
        )

    if argv:
        names = tuple(argument.replace("~", os.path.expanduser("~")) for argument in argv)
    else:
        names = ICON_NAMES

    resolved = {}
    for name in names:
        path = resolve(name)
        if path is None:
            sys.exit(
                f"not a readable file: {name}\n"
                f"looked for it as a path, and in {ICON_DIR}"
            )
        # A shipped icon is reported by its bare name, anything else in full.
        resolved[path] = name if os.path.dirname(path) == ICON_DIR else path

    for path, label in resolved.items():
        preview(path, label)


if __name__ == "__main__":
    main(sys.argv[1:])
