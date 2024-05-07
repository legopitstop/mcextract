# mcextract

[![PyPI](https://img.shields.io/pypi/v/mcextract)](https://pypi.org/project/mcextract/)
[![Python](https://img.shields.io/pypi/pyversions/mcextract)](https://www.python.org/downloads//)
![Downloads](https://img.shields.io/pypi/dm/mcextract)
![Status](https://img.shields.io/pypi/status/mcextract)
[![Issues](https://img.shields.io/github/issues/legopitstop/mcextract)](https://github.com/legopitstop/mcextract/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Extract assets and data from the Minecraft jar.

## Installation
Install the module with pip:
```bat
pip3 install mcextract
```
Update existing installation: `pip3 install mcextract --upgrade`

## Features

- Easy to use command line interface.
- Choose to extract the assets or data folders from the Minecraft jar
- Map objects to get access to all sounds, langs, and other hidden assets that aren't in the jar.
- Run the built-in data generator to get reports, registries, and vanilla world generation files.

## Examples

### Run using the API
```py
import mcextract

api = mcextract.MCExtractAPI()
api.extract("1.20.4/1.20.4.jar", True, True, accept_eula=False)
api.map("16.json", accept_eula=True)
api.generate("1.20.6", ['--client', '--server', '--reports'], accept_eula=True)
```

### Run using CLI
```sh
mcextract extract 1.20.4/1.20.4.jar --assets --data -eula
mcextract map 16.json -eula
mcextract generate 1.20.6 --client --server --reports -eula
```

## Command line commands
```
usage: mcextract [-h] [-V] {extract,map,generate} ...

positional arguments:
  {extract,map,generate}
    extract             Extract data or assets folders from the Minecraft jar.
    map                 Maps Minecraft's objects using an index file.
    generate            Use Minecraft's built-in data generator.

options:
  -h, --help            show this help message and exit
  -V, --version         print the mcextract version number and exit.
```

## Planned Features

- Add minimize or maximize JSONs.


## License

This project's source code is under the MIT license and the Minecraft EULA. 
