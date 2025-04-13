""" For Packing """
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme_data:
    long_description = readme_data.read()

setup(
    name="android-notify",
    version="1.57",
    author="Fabian",
    author_email='fector101@yahoo.com',
    description="A Python package that simpilfies creating Android notifications in Kivy apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fector101/android-notify",
    packages=find_packages(),
    install_requires=[
        "kivy>=2.0.0",
        "pyjnius>=1.4.2"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Android",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "android",
        "notifications",
        "kivy",
        "mobile",
        "post-notifications",
        "pyjnius",
        "android-notifications",
        "kivy-notifications",
        "python-android",
        "mobile-development",
        'push-notifications',
        'mobile-app',
        'kivy-application'
    ],
    project_urls={
        "Documentation": "https://github.com/fector101/android-notify/",
        # "Documentation": "https://github.com/fector101/android-notify/wiki",
        "Source": "https://github.com/fector101/android-notify",
        "Tracker": "https://github.com/fector101/android-notify/issues",
        "Funding": "https://www.buymeacoffee.com/fector101"
    },
    license="MIT"
)
