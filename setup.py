from setuptools import setup, find_packages

setup(
    name="android-notify",
    version="1.23",
    author="Fabian",
    author_email='fector101@yahoo.com',
    description="A Python package for sending Android notifications using PyJNIus in Kivy apps.",
    long_description=open("README.md").read(),
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
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "android",
        "notifications",
        "kivy",
        "mobile",
        "push notifications",
        "pyjnius",
        "android notifications",
        "kivy notifications",
        "python android",
        "mobile development"
    ],
    project_urls={
        "Documentation": "https://github.com/fector101/android-notify/",  # Replace with your documentation URL
        # "Documentation": "https://github.com/fector101/android-notify/wiki",  # Replace with your documentation URL
        "Source": "https://github.com/fector101/android-notify",
        "Tracker": "https://github.com/fector101/android-notify/issues",
        "Funding": "https://www.buymeacoffee.com/fector101"  # Replace with your Buy Me a Coffee link
    },
    license="MIT"
)