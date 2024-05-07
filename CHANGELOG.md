# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 5-6-2024
### General
- Updated for serverjars-api 1.3.0
- Replaced Server with MCExtractAPI
- Moved client to its own package [mcextract-desktop](https://pypi.org/project/mcextract-desktop/)

## [1.1.0] - 8-18-2023
### General
- You can now run the package from the command line: `python -m mcextract <cmd> <args>`
- Added `--eula` argument. If defined it will except the eula. If undefined the script will stop.
- Removed ask eula from console. use --eula instead.
- Default path is now %cd%/Output instead of %userprofile%/Desktop/Output
- --output should now correctly interprit path variables (`%userdata%`, `%userprofile%`, etc)

## [1.0.0] - 7-4-2023

Initial Release
