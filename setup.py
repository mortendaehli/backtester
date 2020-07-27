import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="backtester",
    version="0.0.1",
    author="Morten Dæhli Aslesen",
    author_email="mortendaehli@gmail.com",
    description="A simple backtesting tool for testing trading strategies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mortendaehli/backtester",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)