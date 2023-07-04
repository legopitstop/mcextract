
from tkinter import DISABLED, E, EW, LEFT, NORMAL, W, BooleanVar, StringVar, filedialog, messagebox, IntVar
from UserFolder import User, Config
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkCheckBox, CTkProgressBar, CTkOptionMenu, CTkEntry
import os
import threading
import re
import logging
import customtkinter
import sys

from . import __version__, Server, StatusEvent

customtkinter.set_appearance_mode('System')
customtkinter.set_default_color_theme('blue')
LOCAL = os.path.dirname(os.path.realpath(__file__))

_logger = logging.getLogger('Client')
usr = User('com.legopitstop.minecraft_extracter')

class CTkClient(CTk):
    def __init__(self):
        super().__init__()
        self.is_running=False

        # Create default / fallback options
        JarVersionFolder = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','versions')
        ObjectFolder = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','objects')
        ObjectIndexFolder = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','indexes')
        OutputFolder = os.path.join(os.path.expanduser('~'),'Downloads', 'output')

        # Register config
        self.config = Config()
        self.config.registerItem('Version', __version__)
        self.config.registerItem('ShowOutput',True)
        self.config.registerItem('OutputFolder', OutputFolder)
        self.config.registerItem('JarModule',True)
        self.config.registerItem('JarAssets', True)
        self.config.registerItem('JarData',True)
        self.config.registerItem('JarVersion',"unset")
        self.config.registerItem('JarVersionFolder', JarVersionFolder)
        self.config.registerItem('ObjectModule', False)
        self.config.registerItem('ObjectFolder',ObjectFolder)
        self.config.registerItem('ObjectIndexFolder', ObjectIndexFolder)
        self.config.registerItem('ObjectIndex', "unset")
        self.config.registerItem('DataModule', False)
        self.config.registerItem('DataClient', True)
        self.config.registerItem('DataServer', True)
        self.config.registerItem('DataReports', True)
        self.config.registerItem('DataVersion', "unset")

        self.title('Minecraft Extractor %s'%(__version__))
        self.iconbitmap(os.path.join(LOCAL, 'assets', 'icon.ico'))
        self.minsize(600,400)
        self.geometry('600x400')
        self.protocol('WM_DELETE_WINDOW', self.exit)

        # Varables
        self.EXTRACT_MODULE = BooleanVar()
        self.EXTRACT_ASSETS = BooleanVar()
        self.EXTRACT_DATA = BooleanVar()
        self.EXTRACT_VERSION = StringVar()
        self.EXTRACT_VERSION_FOLDER = StringVar()

        self.MAP_MODULE = BooleanVar()
        self.MAP_INDEX = StringVar()
        self.MAP_INDEX_FOLDER = StringVar()
        self.MAP_FOLDER = StringVar()

        self.GENERATE_MODULE = BooleanVar()
        self.GENERATE_CLIENT = BooleanVar()
        self.GENERATE_SERVER = BooleanVar()
        self.GENERATE_REPORTS = BooleanVar()
        self.GENERATE_VERSION = StringVar()

        self.OUTPUT_FOLDER = StringVar()
        self.SHOW_OUTPUT = BooleanVar()

        # Progressbar
        self.PROGRESS_LBL = StringVar()
        self.PROGRESS_LBL.set('Waiting...')
        self.PROGRESS_MAX = IntVar()
        self.PROGRESS_MAX.set(100)
        self.PROGRESS_PER = StringVar()
        self.PROGRESS_PER.set('0%')

        # Functions
        def choose(varable,type):
            if type=='dir':
                path = filedialog.askdirectory(initialdir=varable.get(),mustexist=True)
                if path!='':
                    varable.set(path)

            elif type=='jar':
                types=[
                    ('Jar','.jar')
                ]
                path = filedialog.askopenfilename(defaultextension='.jar',filetypes=types,initialdir=varable.get())
                if path!='':
                    varable.set(path)
            elif type=='json':
                types=[
                    ('JSON','.json')
                ]
                path = filedialog.askopenfilename(defaultextension='.json',filetypes=types,initialdir=varable.get())
                if path!='':
                    varable.set(path)
            else:
                _logger.warning('Unknown choose type "%s"',type)

        # Widgets
        self.jar_btn = CTkButton(self,text='Jar Extractor', command=lambda: self.toggle_module(self.EXTRACT_MODULE))
        self.jar_btn.grid(row=0,column=0,sticky=EW,padx=3,pady=(10,0))

        self.object_btn = CTkButton(self,text='Object Mapper',command=lambda: self.toggle_module(self.MAP_MODULE))
        self.object_btn.grid(row=0,column=1,sticky=EW,padx=3,pady=(10,0))

        self.data_btn = CTkButton(self,text='Data Generator', command=lambda: self.toggle_module(self.GENERATE_MODULE))
        self.data_btn.grid(row=0,column=2,sticky=EW,padx=3,pady=(10,0))

        # Jar Extractor
        self.jar_wrapper = CTkFrame(self)
        self.jar_assets = CTkCheckBox(self.jar_wrapper, text='Assets', variable=self.EXTRACT_ASSETS, onvalue=True, offvalue=False)
        self.jar_assets.grid(row=0,column=0,sticky=W,padx=5,pady=5)
        self.jar_data = CTkCheckBox(self.jar_wrapper, text='Data',variable=self.EXTRACT_DATA, onvalue=True, offvalue=False)
        self.jar_data.grid(row=1,column=0,sticky=W,padx=5,pady=5)
        self.jar_version = CTkOptionMenu(self.jar_wrapper,variable=self.EXTRACT_VERSION)
        self.jar_version.grid(row=2,column=0, sticky=EW,padx=5,pady=5)
        self.jar_wrapper.grid(row=1,column=0,sticky='nesw',padx=10,pady=(0,10))

        # Object Mapper
        self.object_wrapper = CTkFrame(self)
        self.object_index = CTkOptionMenu(self.object_wrapper,variable=self.MAP_INDEX)
        self.object_index.grid(row=0,column=0, sticky=EW,padx=5,pady=5)
        self.object_wrapper.grid(row=1,column=1,sticky='nesw',padx=10,pady=(0,10))

        # Data Generator
        self.data_wrapper = CTkFrame(self)
        self.data_client = CTkCheckBox(self.data_wrapper, text='Assets', variable=self.GENERATE_CLIENT, onvalue=True, offvalue=False)
        self.data_client.grid(row=0,column=0,sticky=W,padx=5,pady=5)
        self.data_server = CTkCheckBox(self.data_wrapper, text='Data',variable=self.GENERATE_SERVER, onvalue=True, offvalue=False)
        self.data_server.grid(row=1,column=0,sticky=W,padx=5,pady=5)
        self.data_reports = CTkCheckBox(self.data_wrapper, text='Reports',variable=self.GENERATE_REPORTS, onvalue=True, offvalue=False)
        self.data_reports.grid(row=2,column=0,sticky=W,padx=5,pady=5)
        self.data_version = CTkOptionMenu(self.data_wrapper, variable=self.GENERATE_VERSION)
        self.data_version.grid(row=3,column=0, sticky=EW,padx=5,pady=5)
        self.data_wrapper.grid(row=1,column=2,sticky='nesw',padx=10,pady=(0,10))

        # Settings
        self.setting_lbl = CTkLabel(self,text='Settings', fg_color='black')
        self.setting_lbl.grid(row=2,column=0,columnspan=3,sticky=EW,padx=3,pady=(10,0))

        self.setting_wrapper = CTkFrame(self)
        
        self.show_output = CTkCheckBox(self.setting_wrapper, text='Show', variable=self.SHOW_OUTPUT)
        self.show_output.grid(row=0,column=0,columnspan=2,sticky=W,padx=5,pady=5)

        CTkLabel(self.setting_wrapper, text='Output Folder').grid(row=1,column=0,padx=5,pady=5,sticky=W)
        self.output_folder = CTkEntry(self.setting_wrapper, textvariable=self.OUTPUT_FOLDER)
        self.output_folder.grid(row=1,column=1,padx=5,pady=5,sticky=EW)

        self.output_btn = CTkButton(self.setting_wrapper, text='Choose', command=lambda: choose(self.OUTPUT_FOLDER, 'dir'))
        self.output_btn.grid(row=1,column=2,padx=5,pady=5,sticky=E)

        self.setting_wrapper.grid(row=3,column=0,columnspan=3,sticky=EW,padx=10,pady=(0,10))

        # Footer
        footer = CTkFrame(self)
        self.progress_lbl = CTkLabel(footer, textvariable=self.PROGRESS_LBL,wraplength=185, justify=LEFT,width=1)
        self.progress_lbl.grid(row=0,column=0,sticky=W,padx=0,pady=(5, 0))
        
        self.progress_per = CTkLabel(footer, textvariable=self.PROGRESS_PER,width=1)
        self.progress_per.grid(row=0,column=1,sticky=E,padx=0,pady=(5, 0))
    
        self.PROGRESS_BAR = CTkProgressBar(footer,height=10)
        self.PROGRESS_BAR.grid(row=1,column=0,columnspan=2,sticky=EW,padx=5,pady=(0,5))

        self.run_btn = CTkButton(footer, text='Run', command=self.start)
        self.run_btn.grid(row=0,column=2,rowspan=2,sticky=E,padx=5,pady=5)
        
        self.close_btn = CTkButton(footer, text='Close', command=self.exit)
        self.close_btn.grid(row=0,column=3,rowspan=2)
        
        footer.grid(row=4,column=0,sticky=EW,columnspan=3,padx=10,pady=10)

        # Responsive
        footer.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure([0,1,2], weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.jar_wrapper.grid_columnconfigure(0, weight=1)
        self.object_wrapper.grid_columnconfigure(0, weight=1)
        self.data_wrapper.grid_columnconfigure(0, weight=1)

        self.setting_wrapper.grid_columnconfigure(1, weight=1)

        # TODO Apply values from config
        self.update_options()
        self.status(value=100, maximum=100)

    def update_options(self):
        """Updates the VARIABLES from the config"""
        self.SHOW_OUTPUT.set(self.config.getItem('ShowOutput'))
        self.OUTPUT_FOLDER.set(self.config.getItem('OutputFolder'))
        self.EXTRACT_MODULE.set(self.config.getItem('JarModule'))
        self.EXTRACT_ASSETS.set(self.config.getItem('JarAssets'))
        self.EXTRACT_DATA.set(self.config.getItem('JarData'))
        self.EXTRACT_VERSION.set(self.config.getItem('JarVersion'))
        self.EXTRACT_VERSION_FOLDER.set(self.config.getItem('JarVersionFolder'))
        self.MAP_MODULE.set(self.config.getItem('ObjectModule'))
        self.MAP_FOLDER.set(self.config.getItem('ObjectFolder'))
        self.MAP_INDEX_FOLDER.set(self.config.getItem('ObjectIndexFolder'))
        self.MAP_INDEX.set(self.config.getItem('ObjectIndex'))
        self.GENERATE_MODULE.set(self.config.getItem('DataModule'))
        self.GENERATE_CLIENT.set(self.config.getItem('DataClient'))
        self.GENERATE_SERVER.set(self.config.getItem('DataServer'))
        self.GENERATE_REPORTS.set(self.config.getItem('DataReports'))
        self.GENERATE_VERSION.set(self.config.getItem('DataVersion'))


        # Update OptionMenus
        versions = [v for v in os.listdir(self.EXTRACT_VERSION_FOLDER.get())]
        self.jar_version.configure(values=versions)

        indexes = [i.replace('.json', '') for i in os.listdir(self.MAP_INDEX_FOLDER.get())]
        self.object_index.configure(values=indexes)
        
        self._update()

    def save(self):
        """Saves the config options from the window"""
        self.config.setItem('Version', __version__)
        self.config.setItem('ShowOutput',self.SHOW_OUTPUT.get())
        self.config.setItem('OutputFolder', self.OUTPUT_FOLDER.get())
        self.config.setItem('JarModule',self.EXTRACT_MODULE.get())
        self.config.setItem('JarAssets', self.EXTRACT_ASSETS.get() )
        self.config.setItem('JarData', self.EXTRACT_DATA.get())
        self.config.setItem('JarVersion',self.EXTRACT_VERSION.get())
        self.config.setItem('JarVersionFolder', self.EXTRACT_VERSION_FOLDER.get())
        self.config.setItem('ObjectModule', self.MAP_MODULE.get())
        self.config.setItem('ObjectFolder',self.MAP_FOLDER.get())
        self.config.setItem('ObjectIndexFolder', self.MAP_INDEX_FOLDER.get())
        self.config.setItem('ObjectIndex', self.MAP_INDEX.get())
        self.config.setItem('DataModule', self.GENERATE_MODULE.get())
        self.config.setItem('DataClient', self.GENERATE_CLIENT.get())
        self.config.setItem('DataServer', self.GENERATE_SERVER.get())
        self.config.setItem('DataReports', self.GENERATE_REPORTS.get())
        self.config.setItem('DataVersion',self.GENERATE_VERSION.get())

    def disable_all(self):
        """Disables all options"""
        self.jar_btn.configure(state=DISABLED)
        self.jar_assets.configure(state=DISABLED)
        self.jar_data.configure(state=DISABLED)
        self.jar_version.configure(state=DISABLED)
        self.object_btn.configure(state=DISABLED)
        self.object_index.configure(state=DISABLED)
        self.data_btn.configure(state=DISABLED)
        self.data_client.configure(state=DISABLED)
        self.data_server.configure(state=DISABLED)
        self.data_reports.configure(state=DISABLED)
        self.data_version.configure(state=DISABLED)
        self.show_output.configure(state=DISABLED)
        self.output_folder.configure(state=DISABLED)
        self.output_btn.configure(state=DISABLED)
        self.run_btn.configure(state=DISABLED)
    
    def enable_all(self):
        """Enables all options"""
        self.jar_btn.configure(state=NORMAL)
        self.jar_assets.configure(state=NORMAL)
        self.jar_data.configure(state=NORMAL)
        self.jar_version.configure(state=NORMAL)
        self.object_btn.configure(state=NORMAL)
        self.object_index.configure(state=NORMAL)
        self.data_btn.configure(state=NORMAL)
        self.data_client.configure(state=NORMAL)
        self.data_server.configure(state=NORMAL)
        self.data_reports.configure(state=NORMAL)
        self.data_version.configure(state=NORMAL)
        self.show_output.configure(state=NORMAL)
        self.output_folder.configure(state=NORMAL)
        self.output_btn.configure(state=NORMAL)
        self.run_btn.configure(state=NORMAL)
        self._update()

    def toggle_module(self, variable:BooleanVar):
        if variable.get()==False:
            variable.set(True)
            self._update()

        elif variable.get()==True:
            variable.set(False)
            self._update()

    def _update(self):
        # Update Version lists
        def getClientVersions(parent=True):
            """Returns a list of all client versions that are installed on this user"""
            ver = self.EXTRACT_VERSION_FOLDER.get()
            if os.path.exists(ver):
                vers=['unset']
                for v in os.listdir(ver):
                    if os.path.isfile(ver+'/'+v)==False:
                        for i in os.listdir(ver+'/'+v):
                            if i.endswith('.jar'):
                                vers.append(re.sub(r'\.jar$','',i))

                return vers
            else:
                if parent:
                    default = self.default_options['JarVersionFolder']
                    _logger.warning("Invalid version folder! Using default location '%s'", default)
                    self.EXTRACT_VERSION_FOLDER.set(default)
                    return getClientVersions(False)
                else:
                    _logger.warning('Invalid version folder!')
                    messagebox.showerror('Missing Folder!','The following version folder is missing! %s'%self.EXTRACT_VERSION_FOLDER.get())
                    return ['unset']

        def getServerVersions():
            """Returns a list of all the server versions that support data gen"""
            return [
                'unset',
                '1.20',
                '1.20.1',
                '1.19',
                '1.18.2',
                '1.18.1',
                '1.18',
                '1.17.1',
                '1.17'
            ]

        def getIndexes(parent=True):
            """Returns a list of all index versions that are installed on this user"""
            ver = self.MAP_INDEX_FOLDER.get()
            if os.path.exists(ver):
                ind=['unset']
                for i in os.listdir(ver):
                    if os.path.isfile(ver)==False:
                        if i.endswith('.json'):
                            ind.append(re.sub(r'\.json$','',i))
                return ind
            else:
                if parent:
                    default = self.default_options['ObjectIndexFolder']
                    _logger.warning("Invalid index folder! Using default location '%s'", default)
                    self.MAP_INDEX_FOLDER.set(default)
                    return getIndexes(False)
                else:
                    _logger.warning('Invalid index folder!')
                    messagebox.showerror('Missing Folder!','The following index folder is missing! %s'% self.MAP_INDEX_FOLDER.get())
                    return ['unset']

        self.jar_version.configure(values=getClientVersions())
        self.data_version.configure(values=getServerVersions())
        self.object_index.configure(values=getIndexes())

        # Disable run if all modules are off
        if self.EXTRACT_MODULE.get()==False and self.MAP_MODULE.get()==False and self.GENERATE_MODULE.get()==False: self.run_btn.configure(state=DISABLED)
        else: self.run_btn.configure(state=NORMAL)

        if self.EXTRACT_MODULE.get():
            self.jar_wrapper.configure(fg_color='darkgreen')
            self.jar_btn.configure(fg_color='#001b00', hover_color='#001b00')
            self.jar_assets.configure(state=NORMAL)
            self.jar_data.configure(state=NORMAL)
            self.jar_version.configure(state=NORMAL)

        else:
            self.jar_wrapper.configure(fg_color='#2A2D2E')
            self.jar_btn.configure(fg_color='black', hover_color='black')
            self.jar_assets.configure(state=DISABLED)
            self.jar_data.configure(state=DISABLED)
            self.jar_version.configure(state=DISABLED)
        
        if self.MAP_MODULE.get():
            self.object_wrapper.configure(fg_color='darkgreen')
            self.object_btn.configure(fg_color='#001b00', hover_color='#001b00')
            self.object_index.configure(state=NORMAL)

        else:
            self.object_wrapper.configure(fg_color='#2A2D2E')
            self.object_btn.configure(fg_color='black', hover_color='black')
            self.object_index.configure(state=DISABLED)
        
        if self.GENERATE_MODULE.get():
            self.data_wrapper.configure(fg_color='darkgreen')
            self.data_btn.configure(fg_color='#001b00', hover_color='#001b00')
            self.data_client.configure(state=NORMAL)
            self.data_server.configure(state=NORMAL)
            self.data_reports.configure(state=NORMAL)
            self.data_version.configure(state=NORMAL)
        else:
            self.data_wrapper.configure(fg_color='#2A2D2E')
            self.data_btn.configure(fg_color='black', hover_color='black')
            self.data_client.configure(state=DISABLED)
            self.data_server.configure(state=DISABLED)
            self.data_reports.configure(state=DISABLED)
            self.data_version.configure(state=DISABLED)

    def force_exit(self):
        """Forces the app to close"""
        self.destroy()
        _logger.warning('Force shutting down!')
        sys.exit()

    def exit(self):
        """Properly close the program"""
        if self.is_running:
            confirm = messagebox.askyesno('Force Shutdown', 'Are you sure you want to quit? Quitting now may result in errors or corruption.', icon='warning',default='no')
            if confirm==True:
                self.force_exit()
            
        else:
            _logger.info('Stopping!')
            self.destroy()

    def status(self,text:str=None, value:int=None, maximum:int=None, color:str=None):
        """Update the progress bar and progress label"""
        if text!=None:
            self.PROGRESS_LBL.set(str(text))

        if maximum!=None: self.PROGRESS_MAX.set(maximum)

        if value!=None:
            max = self.PROGRESS_MAX.get()
            des = value / max
            per = round(des * 100)
            self.PROGRESS_BAR.set(des)
            self.PROGRESS_PER.set(str(per)+'%')
            self.title('Minecraft Extractor %s - %s'%(__version__,str(per)+'%'))

        if color!=None:
            if color=='complete': self.PROGRESS_BAR.configure(progress_color='green')
            elif color=='reset': self.PROGRESS_BAR.configure(progress_color='#1F6AA5')
            else: self.PROGRESS_BAR.configure(progress_color=color)

    def _run(self):
        """Run the server. **Call .start() instead!**"""
        self.status(color='reset')
        
        def stat(e: StatusEvent):
            self.status(e.name, value=e.value, maximum=e.max)

        for m in self.modules:
            svr = Server.from_dict(m)
            svr.run(status_command=stat, progressbar=False, eula=True)

        # Done!
        self.status(text='Done!',value=100, maximum=100, color='green')
        self.is_running=False
        self.close_btn.configure(text='Close')
        self.enable_all()
        self.bell()

        # Open the output folder when complete.
        if self.SHOW_OUTPUT.get():
            os.startfile(self.OUTPUT_FOLDER.get())

    def start(self, logger:bool=True):
        """
        Start extracting

        Arguments
        ---
        `logger` -  When false it will disable the default logger.
        """
        if logger: logging.basicConfig(format='[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', datefmt='%I:%M:%S',handlers=[logging.FileHandler(usr.join('latest.log'),mode='w'),logging.StreamHandler(sys.stdout)], level=logging.INFO)
        else: _logger.disabled = True

        eula = messagebox.askyesnocancel('Minecraft Extractor', "By clicking 'yes' you agree to Minecraft's EULA. Read https://www.minecraft.net/en-us/eula for more info.")

        if eula==None:
            return None
        elif eula == False:
            _logger.info('You need to agree to the EULA in order to run this tool!')
            return None


        # Disable module if all options are false
        self.modules = []

        if self.EXTRACT_MODULE.get(): # Extract Module
            JAR = os.path.join(self.EXTRACT_VERSION_FOLDER.get(), self.EXTRACT_VERSION.get(), self.EXTRACT_VERSION.get()+'.jar')
            mod = {
                'module': 'extract',
                'output': self.OUTPUT_FOLDER.get(),
                'fp': JAR,
                'assets': self.EXTRACT_ASSETS.get(),
                'data': self.EXTRACT_DATA.get()
            }
            self.modules.append(mod)

        if self.GENERATE_MODULE.get(): # Generate Module
            mod = {
                'module': 'generate',
                'output': self.OUTPUT_FOLDER.get(),
                'client': self.GENERATE_CLIENT.get(),
                'server': self.GENERATE_SERVER.get(),
                'reports': self.GENERATE_REPORTS.get()
            }
            self.modules.append(mod)

        if self.MAP_MODULE.get(): # Map Module
            INDEX = os.path.join(self.MAP_INDEX_FOLDER.get(), self.MAP_INDEX.get()+'.json')
            mod = {
                'module': 'map',
                'output': self.OUTPUT_FOLDER.get(),
                'fp': INDEX,
                'objects': self.MAP_FOLDER.get()
            }
            self.modules.append(mod)

        self.is_running=True
        self.save()
        self.close_btn.configure(text='Cancel')
        self.disable_all()
        threading.Thread(target=self._run, args=(), daemon=True).start()
