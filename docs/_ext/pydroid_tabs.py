"""MyST tab directives that render static code blocks as interactive tabs.

Mirrors the android-notify Vercel docs, where tappable examples are shown as
tabbed code blocks (e.g. "In-App" / "Pydroid 3" pairs, or the PIP / Kivy /
Flet / Pydroid 3 install options).

Directives build the sphinx-tabs nodes directly, so they work from MyST
markdown (sphinx-tabs' own ``tabs``/``tab`` directives rely on RST nested
parsing and cannot be composed from MyST).

Usage::

    :::{code-tabs}
    PIP
    ```bash
    pip install android-notify
    ```

    Kivy
    ```ini
    requirements = python3, kivy, pyjnius, android-notify
    ```
    :::

The label is the line right before each fenced block; the fence info string
gives the language / title.
"""

from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import Directive

from sphinx_tabs.tabs import (
    SphinxTabsContainer,
    SphinxTabsPanel,
    SphinxTabsTab,
    SphinxTabsTablist,
)

PRAVATAR = "https://i.pravatar.cc/300"
IMAGE_PLACEHOLDERS = (
    "assets/imgs/profile.png",
    "assets/imgs/photo.png",
    "imgs/profile.png",
    "imgs/photo.png",
)
GLOBALS_RE = re.compile(r"global\s+[a-zA-Z0-9_, ]+")


def make_literal_block(source: str, language: str = "default") -> nodes.literal_block:
    """Highlighted literal block, same as a fenced ``language`` code block."""
    code = nodes.literal_block(source, source)
    code["language"] = language
    code["classes"] = [language]
    return code


def build_tabs(env, docname: str, panels) -> SphinxTabsContainer:
    """Build a ``sphinx-tabs`` group from ``(label, source, language)`` panels.

    ``env`` is the Sphinx environment needed to generate unique tab ids.
    """
    serial = env.new_serialno(f"tabs:{docname}")
    base = f"tabs-{serial}"

    container = SphinxTabsContainer()
    container["classes"] = ["sphinx-tabs"]
    container["names"] = []
    container["dupnames"] = []
    container["backrefs"] = []

    tablist = SphinxTabsTablist()
    tablist["role"] = "tablist"
    tablist["aria-label"] = "Tabbed content"
    tablist["classes"] = ["closeable"]
    tablist["names"] = []
    tablist["dupnames"] = []
    tablist["backrefs"] = []

    for idx, (label, source, language) in enumerate(panels):
        tab_id = f"tab-{base}-{idx}"
        panel_id = f"panel-{base}-{idx}"
        name = f"{base}-{idx}"

        tab = SphinxTabsTab()
        tab["classes"] = ["sphinx-tabs-tab"]
        tab["ids"] = [tab_id]
        tab["name"] = name
        tab["role"] = "tab"
        tab["tabindex"] = "0" if idx == 0 else "-1"
        tab["aria-selected"] = "true" if idx == 0 else "false"
        tab["aria-controls"] = panel_id
        tab["names"] = []
        tab["dupnames"] = []
        tab["backrefs"] = []
        tab += nodes.Text(label)
        tablist += tab

        panel = SphinxTabsPanel()
        panel["ids"] = [panel_id]
        panel["name"] = name
        panel["role"] = "tabpanel"
        panel["tabindex"] = 0
        panel["aria-labelledby"] = tab_id
        panel["classes"] = ["sphinx-tabs-panel"]
        if idx:
            panel["hidden"] = "true"
        panel["names"] = []
        panel["dupnames"] = []
        panel["backrefs"] = []
        panel += make_literal_block(source, language)
        container += panel

    container.insert(0, tablist)
    return container


def generate_pydroid_wrapper(code: str) -> str:
    """Wrap a snippet so it runs as a Kivy app on Pydroid 3."""
    indented = "\n        ".join(code.split("\n")).rstrip()
    for placeholder in IMAGE_PLACEHOLDERS:
        indented = indented.replace(placeholder, PRAVATAR)

    globals_found = []
    for match in GLOBALS_RE.findall(code):
        if match.strip() not in globals_found:
            globals_found.append(match.strip())
    globals_decl = "        " + "        ".join(g + "\n        " for g in globals_found) if globals_found else ""

    return (
        "from kivy.app import App\n"
        "from kivy.uix.button import Button\n"
        "\n"
        "class MainApp(App):\n"
        "    def build(self):\n"
        "        return Button(\n"
        '            text="Run Code",\n'
        "            on_press=self.run_code,\n"
        "            size_hint=[None, None],\n"
        "            size=[200, 100],\n"
        '            pos_hint={"center_y": .5, "center_x": .5}\n'
        "        )\n"
        "\n"
        "    def run_code(self, *args):\n"
        f"        {globals_decl}{indented}\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    MainApp().run()\n"
    )


class PydroidDirective(Directive):
    """Render one snippet as an In-App / Pydroid 3 tab group."""

    has_content = True

    def run(self):
        env = getattr(self, "env", None) or self.state.document.settings.env
        code = "\n".join(self.content).strip("\n")

        panels = [
            ("In-App", code, "python"),
            ("Pydroid 3", generate_pydroid_wrapper(code), "python"),
        ]
        return [build_tabs(env, env.docname, panels)]


class CodeTabsDirective(Directive):
    """Render labelled code fences as a tab group.

    Body format: a label line immediately followed by a fenced block, e.g.::

        PIP
        ```bash
        pip install android-notify
        ```

        Kivy
        ```ini
        requirements = python3, kivy, pyjnius, android-notify
        ```
    """

    has_content = True

    def run(self):
        env = getattr(self, "env", None) or self.state.document.settings.env

        lines = [line for line in self.content]
        panels = []
        i = 0
        while i < len(lines):
            label = ""
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                if lines[i].strip():
                    label = lines[i].strip()
                i += 1
            if i >= len(lines):
                break
            info = lines[i].strip().lstrip("`").strip()
            language = info.split()[0] if info else "default"
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            if label:
                panels.append((label, "\n".join(code_lines).strip("\n"), language))

        return [build_tabs(env, env.docname, panels)]


def setup(app):
    app.add_directive("pydroid", PydroidDirective)
    app.add_directive("code-tabs", CodeTabsDirective)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }