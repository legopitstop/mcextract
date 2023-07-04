# mcextract

Extract assets and data from the Minecraft jar.

## Install
Install using python and pip
```
pip install mcextract
```

## Features

- Includes a UI and a command line extractor.
- Saves configuration for the next time you use it.
- Choose to extract the assets or data folders from the jar
- Compile the objects to get access to all sounds, langs, and other hidden assets that aren't in the jar.
- Choose which version to extract using a simple dropdown menu. (may experience some issues if your mc is located in diff folder)
- Data Generator for generating reports, and vanilla world generation files.

## Examples
### Run with UI
```py
import mcextract

app=mcextract.CTkClient()
app.mainloop()
```
### Run with the command line
```py
import mcextract

svr=mcextract.Server.from_args()
svr.run()
```
Now run the Python script using the commands listed below

## Command line commands
### extract
#### Arguments
| Name |Required| Description |
|--|--|--|
|`<fp>`|Yes| The jar file to extract. Located: `%appdata%\.minecraft\versions\VERSION\VERSION.jar`|
|`--assets`|| Extract all files in assets folder. |
|`--data`|| Extract all files in data folder. |
|`--output <directory>`|| The output directory. |

#### Example
```
python main.py extract "%appdata%\.minecraft\versions\1.20.1\1.20.1.jar" --assets --data --output "%userprofile%\Downloads\Output"
```

### map
#### Arguments
| Name |Required| Description |
|--|--|--|
|`<index>`|Yes| The index JSON to map objects with. Located: `%appdata%\.minecraft\assets\indexes\INDEX.json`|
|`<objects>`| Yes | The directory that contains all objects. Located: `%appdata%\.minecraft\assets\objects`|
|`--output <directory>`|| The output directory. |

#### Example
```
python main.py map "%appdata%\.minecraft\assets\indexes\3.json" "%appdata%\.minecraft\assets\objects" --output "%userprofile%\Downloads\Output"
```

### generate
#### Arguments
| Name |Required| Description |
|--|--|--|
|`<version>`|Yes| The server jar version to download and use. |
|`--client`|| Generate client data. |
|`--server`|| Generate server data. |
|`--reports`|| Generate reports. |
|`--output <directory>`|| The output directory. |

#### Example
```
python main.py generate 1.20.1 --client --server --reports --output "%userprofile%\Downloads\Output"
```

## Planned Features

- Add minimize or maximize JSON's.
