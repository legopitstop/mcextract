import os
import logging
import sys
import zipfile
import shutil
import json
import serverjars
import subprocess
import tempfile
import re

__version__ = "1.2.0"
__all__ = ["MCExtractAPI"]

DEFAULT_OUTPUT = os.path.join(os.getcwd(), 'generate')

class MCExtractAPI():
    def __init__(self, mcdirectory:str=None, logger:bool=True):
        if not mcdirectory: mcdirectory = os.path.expandvars('%appdata%\\.minecraft')
        self.mcdirectory = mcdirectory
        self.logger = logging.getLogger("mcextract")
        logging.basicConfig(
                format="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s",
                datefmt="%I:%M:%S",
                handlers=[logging.StreamHandler(sys.stdout)],
                level=logging.INFO,
            )
        if not logger:
            self.logger.disabled = False

    def accept_eula(self, prompt:str='You need to agree to the Minecraft End User License Agreement (EULA) https://www.minecraft.net/en-us/eula. y/N? ') -> bool:
        res = input(prompt)
        if res.lower()[0] == 'y':
            return True
        return False

    def get_docker(self, mcversion:str) -> str:
        if mcversion >= '1.20.5':
            suffix = 'delta' # 21.0.3
        else:
            suffix = 'gamma' # 17.0.8
        # 1.18 beta
        # 1.17 alpha
        docker = os.path.expandvars(
            os.path.join(
                "%localappdata%",
                "Packages",
                "Microsoft.4297127D64EC6_8wekyb3d8bbwe",
                "LocalCache",
                "Local",
                "runtime",
                "java-runtime-"+suffix,
                "windows-x64",
                "java-runtime-"+suffix,
                "bin",
                "java.exe",
            )
        )
        if os.path.isfile(docker):
            return docker
        return "java"

    def extract(self, jar_file:str, assets:bool=False, data:bool=False, output:str=None, accept_eula:bool=False) -> int:
        """
        Extracts data and assets folders from the Minecraft jar.

        :param jar_file: The client jar to extract.
        :type jar_file: str
        :param assets: Extract the assets folder?, defaults to False
        :type assets: bool, optional
        :param data: Extract the data folder?, defaults to False
        :type data: bool, optional
        :param output: The output folder, defaults to generate
        :type output: str, optional
        :param accept_eula: Specifies whether to automatically accept the Minecraft EULA Terms, defaults to False
        :type accept_eula: int, optional
        :rtype: int
        """
        if not accept_eula and not self.accept_eula(): return False
        jar_file = jar_file if os.path.isabs(jar_file) else os.path.join(self.mcdirectory, 'versions', jar_file)
        output = os.path.expandvars(output) if output else DEFAULT_OUTPUT
        cache = os.path.join(output, '.cache')
        cached_jar = os.path.join(cache, os.path.basename(jar_file))
        os.makedirs(cache, exist_ok=True)

        # Create a copy of the jar
        if not os.path.exists(cached_jar):
            self.logger.info("Copying: '%s'", jar_file)
            shutil.copyfile(jar_file, cached_jar)

        # Extract requested folders
        self.logger.info("Extracting: '%s'", jar_file)
        with zipfile.ZipFile(cached_jar) as zip:
            for file in zip.namelist():
                if data and file.startswith('data/'):
                    zip.extract(file, os.path.join(output, 'data'))
                elif assets and file.startswith('assets/'):
                    zip.extract(file, os.path.join(output, 'assets'))

        self.logger.info("Output: '%s'", output)
        return 1

    def generate(self, mcversion:str, args:list=[], output:str=None, accept_eula:bool=False) -> int:
        """
        Use Minecraft's built-in data generator. 

        :param mcversion: The Minecraft version to download or path to the jar.
        :type mcversion: str
        :param client: Generate client data?, defaults to False
        :type client: bool, optional
        :param server: Generate server data?, defaults to False
        :type server: bool, optional
        :param reports: Generate reports?, defaults to False
        :type reports: bool, optional
        :param output: The output folder, defaults to generate
        :type output: str, optional
        :param accept_eula: Specifies whether to automatically accept the Minecraft EULA Terms, defaults to False
        :type accept_eula: int, optional
        :rtype: int
        """
        if not accept_eula and not self.accept_eula(): return False
        output = os.path.expandvars(output) if output else DEFAULT_OUTPUT
        cache = os.path.join(output, '.cache')
        os.makedirs(cache, exist_ok=True)
        with tempfile.TemporaryDirectory() as temp:
            if mcversion.endswith('.jar'):
                jar_file = os.path.join(temp, "server.jar")
                shutil.copyfile(os.path.expandvars(mcversion), jar_file)
            else:
                jar_file = os.path.join(temp, mcversion+"-server.jar")
                if not os.path.isfile(jar_file):
                    self.logger.info("Downloading '%s-server.jar' (This may take a while)", mcversion)
                    cat = 'vanilla' if re.match(r'^\d+\.\d+(\.\d+)?$', mcversion) else 'snapshot'
                    serverjars.download_jar("vanilla", cat, jar_file, mcversion)

            version_args = []
            if mcversion <= "1.17.1":
                version_args = ['-cp', jar_file, 'net.minecraft.data.Main', '--output', output]
            else:
                version_args = ['-DbundlerMainClass=net.minecraft.data.Main', '-jar', jar_file, '--output', output]
            cmd = ['cd', temp, '&', self.get_docker(mcversion), *version_args, *args]
            self.logger.info("Starting data generator '%s'", ' '.join(cmd))
            process = subprocess.Popen(cmd, shell=True)
            process.wait()
        
        self.logger.info("Output: '%s'", output)
        return 1

    def map(self, index_file:str, objects_directory:str=None, output:str=None, accept_eula:bool=False) -> int:
        """
        Maps Minecraft's objects using an index file.

        :param index_file: The JSON file used to map objects.
        :type index_file: str
        :param objects_directory: The directory that contains the objects to map, defaults to None
        :type objects_directory: str, optional
        :param output: The output folder, defaults to generate
        :type output: str, optional
        :param accept_eula: Specifies whether to automatically accept the Minecraft EULA Terms, defaults to False
        :type accept_eula: int, optional
        :rtype: int
        """
        if not accept_eula and not self.accept_eula(): return False
        if not objects_directory: objects_directory = 'assets/objects'
        index_file = index_file if os.path.isabs(index_file) else os.path.join(self.mcdirectory, 'assets', 'indexes', index_file)
        objects_directory = objects_directory if os.path.isabs(objects_directory) else os.path.join(self.mcdirectory, objects_directory)
        output = os.path.expandvars(output) if output else DEFAULT_OUTPUT
        
        self.logger.info("Loading index: '%s'", index_file)
        with open(index_file) as r:
            indx = json.load(r)

        self.logger.info("Mapping objects: '%s'", objects_directory)
        for key in indx["objects"]:
            hash = indx["objects"][key]["hash"]
            hashfolder = hash[0:2]
            # Create dir
            dir = os.path.dirname(key)
            os.makedirs(os.path.join(output, dir), exist_ok=True)
            source = os.path.join(objects_directory, hashfolder, hash)
            dest = os.path.join(output, key)
            try:
                shutil.copy(source, dest)
            except FileNotFoundError:
                self.logger.warning(' Missing file "%s"', hash)
            except:
                self.logger.exception(" Failed: %s", key)

        self.logger.info("Output: '%s'", output)
        return 1
