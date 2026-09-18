"""Add SEO meta tags (description, keywords) to every page."""

import html

META = {
    "description": (
        "Android Notify documentation - create rich Android notifications "
        "in Kivy and Flet apps with the android-notify Python package."
    ),
    "keywords": "android notifications, kivy, flet, pyjnius, python, pydroid",
}


def install_meta(app, pagename, templatename, context, doctree):
    tags = context.get("metatags", "")
    for name, content in META.items():
        tags += f'\n<meta name="{html.escape(name)}" content="{html.escape(content)}"/>'
    context["metatags"] = tags


def setup(app):
    app.connect("html-page-context", install_meta)
    return {"parallel_read_safe": True}