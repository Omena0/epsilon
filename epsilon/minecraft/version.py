import minecraft_launcher_lib as mcl
from ..version import NAME, VERSION
from ..utils import Logger
import subprocess

log = Logger('MCVER')

class MinecraftInstall:
    version: str       # MC Version
    modloader: str     # Vanilla, fabric, forge
    modloader_ver: str # Mod loader version
    gameDir: str       # .minecraft Path

    def __init__(self, version, modloader, modloader_ver, gameDir):
        log.trace(f'MinecraftInstall({version=},{modloader=},{modloader_ver=},{gameDir=})')
        self.version = version
        self.modloader = modloader
        self.modloader_ver = modloader_ver
        self.gameDir = gameDir

    def __str__(self):
        return f'MinecraftInstall({self.version=},{self.modloader=},{self.modloader_ver=},{self.gameDir=})'

def get_launch_command(install:MinecraftInstall, login_data:mcl.microsoft_types.CompleteLoginResponse):
    log.trace(f'get_launch_command({install=},{login_data['name']=})')
    if not is_installed(install):
        log.info(f'Version not installed: {install.modloader}_{install.version}')
        return None

    options:mcl.types.MinecraftOptions = {
        # This is needed
        "username": login_data['name'],
        "uuid": login_data['id'],
        "token": login_data['access_token'],

        "jvmArguments": [],
        "launcherName": NAME,
        "launcherVersion": VERSION, 
        "gameDirectory": install.gameDir,

        "server": "as.hs.vc",
        "port":   "25565",
    }
    cmd = mcl.command.get_minecraft_command(
        install.version,
        install.gameDir,
        options
    )

    return cmd

def get_latest_loader_ver(modloader, mc_ver):
    log.trace(f'get_latest_loader_ver({modloader=},{mc_ver=})')
    if modloader in {None, 'vanilla'}:
        return None
    return mcl.mod_loader.get_mod_loader(modloader).get_latest_loader_version(mc_ver)

def is_installed(install: MinecraftInstall):
    log.trace(f'is_installed({install=})')
    if install.modloader not in {None, 'vanilla'}:
        loader = mcl.mod_loader.get_mod_loader(install.modloader)
        ver = loader.get_installed_version(install.version, install.modloader_ver)
    else:
        ver = install.version

    versions = [i['id'] for i in mcl.utils.get_installed_versions(install.gameDir)]

    return ver in versions

def ensure_install(install:MinecraftInstall, callback):
    log.trace(f'ensure_install({install=},{callback=})')
    if is_installed(install):
        return

    if install.modloader not in {None, 'vanilla'}:
        loader = mcl.mod_loader.get_mod_loader(install.modloader)
        loader.install(install.version, install.gameDir, loader_version=install.modloader_ver, callback=callback)

    else:
        mcl.install.install_minecraft_version(install.version, install.gameDir, callback)

    return True

def launch(cmd):
    log.trace(f'launch({cmd=})')
    subprocess.run(cmd)
