from setuptools import setup, find_packages

setup(
    name='android_notify',
    version='1.2',
    author='Fabian',
    url='https://github.com/Fector101/android_notify/',
    description='A Python package for sending Android notifications.',
    packages=find_packages(),
    install_requires=['pyjnius'],
    author_email='fabianjoseph063@gmail.com',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    project_urls={
        'Funding': 'https://buymeacoffee.com/fector101',
        'Source': 'https://github.com/Fector101/android_notify/',
    },
)