from progress.bar import Bar
import os
import argparse
import logging
import zipfile
import shutil
import hashlib
import sys
import json
import re
import serverjars

PATH = os.getcwd()

# Commands
# extract <fp> --assets --data --output <output_folder>
# map <fp> <objects> --output <output_folder>
# generate <version> --client --server --reports --output <output_folder>

_logger = logging.getLogger('Server')

class Status:
    def __init__(self, id:str, name:str, max:int, callback, defaultbar:bool=True):
        self.id = id
        self.name = name
        self.max = max
        self.value = 0
        self.callback = callback
        self.defaultbar = defaultbar
        if defaultbar: self.bar = Bar(self.name, max=max)

    def next(self, n:int=1):
        self.value += n
        if self.defaultbar: self.bar.next(n)
        if self.callback is not None:
            ctx = StatusEvent(self)
            self.callback(ctx)

    def finish(self):
        if self.defaultbar: self.bar.finish()

class StatusEvent:
    def __init__(self, status:Status):
        self.name = status.name
        self.max = status.max
        self.value = status.value
        self.percent = (self.value / self.max) * 100

class Server():
    def __init__(self, **options):
        self.from_dict(options)

    @property
    def progressbar(self) -> bool:
        return getattr(self, '_progressbar', True)
    
    @progressbar.setter
    def progressbar(self, value:bool|None):
        if value is None:
            setattr(self, '_progressbar', True)
        elif isinstance(value, bool):
            setattr(self, '_progressbar', value)
        else:
            raise TypeError(f"Expected bool but got '{value}' instead")
        
    @property
    def status_command(self) -> None:
        return getattr(self, '_status_command', None)
    
    @status_command.setter
    def status_command(self, value):
        setattr(self, '_status_command', value)
        
    @property
    def status(self) -> Status|None:
        return getattr(self, '_status', None)
    
    @status.setter
    def status(self, value:Status):
        if value is None:
            setattr(self, '_status', None)
        elif isinstance(value, Status):
            setattr(self, '_status', value)
        else:
            raise TypeError(f"Expected Status or None but got '{value.__class__.__name__}' instead.")

    @property
    def path(self) -> str:
        return getattr(self, '_path', PATH)
    
    @path.setter
    def path(self, value:str):
        if value is None:
            setattr(self, '_path', PATH)
        else: setattr(self, '_path', str(value))

    @property
    def module(self) -> str|None:
        return getattr(self, '_module', None)
    
    @module.setter
    def module(self, value:str):
        setattr(self, '_module', str(value))

    @property
    def output(self) -> str:
        p = os.path.abspath(os.path.expandvars(getattr(self, '_output', os.path.join(self.path, 'Output'))))
        os.makedirs(p, exist_ok=True)
        return p
    
    @output.setter
    def output(self, value:str):
        if value is None:  setattr(self, '_output', os.path.join(self.path, 'Output'))
        else: setattr(self, '_output', str(value))

    @property
    def fp(self) -> str|None:
        return getattr(self, '_fp', None)
    
    @fp.setter
    def fp(self, value:str):
        if os.path.isfile(value):
            setattr(self, '_fp', os.path.join(value))
        else:
            raise FileNotFoundError(f"No such file or directory '{value}'")
    
    @property
    def assets(self) -> bool:
        return getattr(self, '_assets', False)
    
    @assets.setter
    def assets(self, value:bool|None):
        if value is None:
            setattr(self, '_assets', False)
        elif isinstance(value, bool):
            setattr(self, '_assets', value)
        else:
            raise TypeError(f"Expected bool but got '{value}' instead")
    
    @property
    def data(self) -> bool:
        return getattr(self, '_data', False)
    
    @data.setter
    def data(self, value:bool|None):
        if value is None:
            setattr(self, '_data', False)
        elif isinstance(value, bool):
            setattr(self, '_data', value)
        else:
            raise TypeError(f"Expected bool but got '{value}' instead")
    
    @property
    def client(self) -> bool:
        return getattr(self, '_client', False)
    
    @client.setter
    def client(self, value:bool|None):
        if value is None:
            setattr(self, '_client', False)
        elif isinstance(value, bool):
            setattr(self, '_client', value)
        else:
            raise TypeError(f"Expected bool but got '{value}' instead")
    
    @property
    def server(self) -> bool:
        return getattr(self, '_server', False)
    
    @server.setter
    def server(self, value:bool|None):
        if value is None:
            setattr(self, '_server', False)
        elif isinstance(value, bool):
            setattr(self, '_server', value)
        else:
            raise TypeError(f"Expected bool but got '{value}' instead")
    
    @property
    def reports(self) -> bool:
        return getattr(self, '_reports', False)
    
    @reports.setter
    def reports(self, value:bool|None):
        if value is None:
            setattr(self, '_reports', False)
        elif isinstance(value, bool):
            setattr(self, '_reports', value)
        else:
            raise TypeError(f"Expected bool but got '{value}' instead")
    
    @property
    def objects(self) -> str|None:
        return getattr(self, '_objects', None)
    
    @objects.setter
    def objects(self, value:str):
        if os.path.isdir(value):
            setattr(self, '_objects', os.path.join(value))
        else:
            raise FileNotFoundError(f"No such file or directory '{value}'")
    
    @property
    def version(self) -> str|None:
        return getattr(self, '_version', None)
    
    @version.setter
    def version(self, value:str):
        setattr(self, '_version', str(value))
    
    @property
    def eula(self) -> bool|None:
        return getattr(self, '_eula', None)
    
    @eula.setter
    def eula(self, value:bool):
        if value is None:
            setattr(self, '_eula', None)
        elif isinstance(value, bool):
            setattr(self, '_eula', value)
        else:
            raise TypeError(f"Expected bool but got '{value.__class__.__name__}' instead")

    def is_valid_file(self, arg, filetype:str):
        if not os.path.exists(arg):
            self.parser.error("The file %s does not exist!" % arg)
        elif not arg.endswith(''+filetype):
            self.parser.error("The file %s must be %s!" %(arg, filetype.upper()))
        else:
            return arg
        
    def is_valid_dir(self, arg):
        if not os.path.exists(arg):
            self.parser.error("The directory %s does not exist!" % arg)
        else:
            return arg

    @classmethod
    def from_args(cls, args=None):
        self = cls.__new__(cls)
        
        # Parser
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="module")
        extract_parser = subparsers.add_parser('extract') # jar <fp> --assets --data
        extract_parser.add_argument(dest='fp', type=lambda x: self.is_valid_file(x, 'jar'))
        extract_parser.add_argument('--assets', '-assets', action='store_true')
        extract_parser.add_argument('--data', '-data', action='store_true')
        extract_parser.add_argument('--output', '-o', type=str, const=None)
        extract_parser.add_argument('--eula', '-eula', action='store_true')

        map_parser = subparsers.add_parser('map') # map <fp> <objects>
        map_parser.add_argument(dest='fp', type=lambda x: self.is_valid_file(x, 'json'))
        map_parser.add_argument(dest='objects', type=lambda x: self.is_valid_dir(x))
        map_parser.add_argument('--output', '-o', type=str, const=None)
        map_parser.add_argument('--eula', '-eula', action='store_true')

        generate_parser = subparsers.add_parser('generate') # generate <version> --assets --data --reports
        generate_parser.add_argument(dest='version', type=str)
        generate_parser.add_argument('-client', '--client', action='store_true')
        generate_parser.add_argument('-server', '--server', action='store_true')
        generate_parser.add_argument('-reports', '--reports', action='store_true')
        generate_parser.add_argument('--output', '-o', type=str, const=None)
        generate_parser.add_argument('--eula', '-eula', action='store_true')

        _args = parser.parse_args(args)
        return self.from_dict(vars(_args))

    @classmethod
    def from_dict(cls, data:dict):
        self = cls.__new__(cls)
        for n,v in data.items(): setattr(self, n, v)
        return self

    def send_status(self, id:str, name:str=None, max:int=None):
        if self.status is None or self.status.id != id: # Create status
            if self.status is not None: self.status.finish()
            self.status = Status(id, name, max, self.status_command, self.progressbar)
        else:
            self.status.next()
            if self.status.value >= self.status.max: self.status.finish()
        return self.status

    def finish_status(self):
        if self.status is not None:
            self.status.finish()
            self.status = None
        return self

    def _countfiles(self, path, root=True):
        """Count the number of files in the directory."""
        count = 0
        for file in os.listdir(path):
            p = os.path.join(path, file)
            if os.path.isfile(p):
                count += 1
            elif os.path.isdir(p):
                count += self._countfiles(p,False)
        return count

    def _copydir(self, src:str, dst:str, root=True):
        """Copy all files from one directory to another."""
        files = os.listdir("\\\\?\\" + src)
        os.makedirs(dst, exist_ok=True)
        
        if root:
            total = self._countfiles(src)
            filename = os.path.basename(src)
            self.send_status('copy', f'Copying {filename}', total)

        for filename in files:
            source = os.path.join(src, filename)
            destination = os.path.join(dst, filename)
            if os.path.exists(source) and os.path.isfile(source):
                shutil.copy("\\\\?\\"+source, "\\\\?\\"+destination)
            else:
                self._copydir(source+'\\',destination+'\\', root=False)
            self.send_status('copy')

        if root:
            self.finish_status()

    def _run_extract(self):
        filename = os.path.basename(self.fp)
        cachename = hashlib.sha1(bytes('extract_'+str(filename), 'utf-8')).hexdigest()
        CACHE = os.path.join(self.output, '.cache')
        JAR_CACHE = os.path.join(CACHE, cachename) # TODO Instead of using UUID it should use an encoded version of "extract_<jar_name>" which it should then check before extracting.
        
        # Only extract if folder does'nt exist in .cache
        if not os.path.exists(JAR_CACHE):
            os.makedirs(JAR_CACHE, exist_ok=True)
            with zipfile.ZipFile('\\\\?\\'+self.fp) as zf:
                total = len(zf.infolist())
                self.send_status('extract', "Extracting JAR", total)
                for member in zf.infolist():
                    self.send_status('extract')
                    try:
                        # Ignore .class files
                        if member.filename.endswith('.class')==False:
                            try:
                                zf.extract(member, JAR_CACHE)
                            except Exception as err: pass
                                
                    except zipfile.error as e:
                        pass
                self.finish_status()
        else: _logger.info(f'Using .cache/{filename}')

        if self.assets:
            self._copydir(os.path.join(JAR_CACHE, 'assets'), os.path.join(self.output, 'assets'))
        
        if self.data:
            self._copydir(os.path.join(JAR_CACHE, 'data'), os.path.join(self.output, 'data'))

        _logger.info('Done!')

    def _run_map(self):
        with open(self.fp) as r: indx = json.load(r)
        TOTAL=len(indx['objects'])
        self.send_status('map', 'Mapping objects', max=TOTAL)

        for key in indx['objects']:
            hash = indx['objects'][key]['hash']
            hashfolder = re.match(r'^.{2}',hash)[0]
            # Create dir
            dir = os.path.dirname(key)
            os.makedirs(os.path.join(self.output, dir), exist_ok=True)
            source = os.path.join(self.objects, hashfolder, hash)
            dest=os.path.join(self.output,key)
            try: shutil.copy(source, dest)
            except FileNotFoundError: _logger.warning('Missing file "%s"',hash)
            except: _logger.exception('Failed: %s',key)
            self.send_status('map')

        self.finish_status()

        _logger.info('Done!')
        
    def _run_generate(self):
        JAVA = os.path.join(os.path.expanduser('~'),'AppData','Local','Packages','Microsoft.4297127D64EC6_8wekyb3d8bbwe','LocalCache','Local','runtime','java-runtime-gamma','windows-x64','java-runtime-gamma','bin', 'java.exe')
        if not os.path.isfile(JAVA):
            _logger.warning('Could not find java.exe at "%s". Using enviroment variable instead.', JAVA)
            JAVA = 'java'
        CACHE = os.path.join(self.output, '.cache')
        DATA_CACHE = os.path.join(CACHE, hashlib.sha1(bytes('generate_'+str(self.version), 'utf-8')).hexdigest())
        JAR = os.path.join(DATA_CACHE, 'server.jar')
        
        # Download server
        if not os.path.exists(DATA_CACHE):
            _logger.info('Downloading %s.jar (This may take a while)', self.version)
            os.makedirs(DATA_CACHE, exist_ok=True)
            serverjars.downloadJar('vanilla', JAR, self.version)

        args = ''
        if self.client: args+=' --client'
        if self.server: args+=' --server'
        if self.reports: args+=' --reports'

        prefix = ''
        if JAVA == 'java':
            prefix = 'java'
        else:
            prefix = f'"{JAVA}"'

        out = os.path.join(self.output, 'generated')
        cd = os.path.join(PATH, '.minecraft')
        os.makedirs(cd, exist_ok=True)
        if self.version=='1.17' or self.version=='1.17.1':
            command = f'cd "{cd}" & {prefix} -cp {JAR} net.minecraft.data.Main --output "{out}"{args}'
            _logger.info('Using 1.17 command: "%s"', command)

        else:
            command = f'cd "{cd}" & {prefix} -DbundlerMainClass=net.minecraft.data.Main -jar {JAR} --output "{out}"{args}'
            _logger.info('Using 1.18+ command: "%s"',command)

        _logger.info('Starting...')
        cmd = os.system(command)
        if cmd!=0:
            _logger.warning('Failed to run data generator! %s', command)

        _logger.info('Done!')

    def run(self, status_command=None, finish_command=None, logger:bool=True, progressbar:bool=True, eula:bool=None):
        """
        Run the commnad.

        Arguments
        ---
        `status_command` - The callback command that sends status updates and % completion data.

        `finish_command` - The callback command to trigger when the proccess is complete.

        `logger` - When false it will disable the default logger.

        `progressbar` - Whether or not it should show the console progressbar.

        `eula` - When true you agree to the EULA.
        """
        self.progressbar = progressbar
        if logger:
            logging.basicConfig(format='[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', datefmt='%I:%M:%S',handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)
        else:
            _logger.disabled = True


        if eula is not None: self.eula = eula
        if self.eula==False:
            _logger.info('You need to agree to the EULA in order to run this tool!')
            return None
        
        # Print details
        _logger.info("Output Folder: '%s'", self.output)

        if status_command is not None: self.status_command = status_command
        match self.module:
            case 'extract':
                self._run_extract()
            case 'map':
                self._run_map()
            case 'generate':
                self._run_generate()

        if finish_command is not None: finish_command()

if __name__=='__main__':
    app=Server.from_args()
    app.run()