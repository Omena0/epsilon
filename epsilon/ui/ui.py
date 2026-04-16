from ..minecraft import is_installed, ensure_install, get_launch_command, launch, MinecraftInstall, get_latest_loader_ver
from ..utils import ConfigStore, Logger
import minecraft_launcher_lib as mcl
from threading import Thread
from ..version import FULL
import engine as ui
import os

log = Logger('UI   ')

def get_cmd(login_data):
    log.trace(f'get_cmd({login_data['name']=})')
    if not d.value:
        log.trace(f'{d.value=}, returning..')
        return

    modloader, mcver = d.value.split('_',1)
    loader_ver = get_latest_loader_ver(modloader, mcver)

    install = MinecraftInstall(
        mcver,
        modloader,
        loader_ver,
        mc_dir
    )

    log.trace(f'{install=}')

    if not is_installed(install):
        install_version(install)

    return get_launch_command(install, login_data)

mc_dir = os.path.abspath('.minecraft')

installs = ConfigStore('versions.json', {'installs': []})

d:ui.Dropdown = None #type:ignore

def main(login_data):
    log.trace(f'main({login_data['name']=})')
    global d
    window = ui.Window((250, 220))
    window.title = FULL

    b = ui.Button(
        window,
        (25,50),
        "Launch",
        (200, 100),
        font=(None, 55),
        on_click=lambda x: (window.destroy(), Thread(target=launch,args=(get_cmd(login_data),),daemon=True).start())
    )

    d = ui.Dropdown(
        window,
        (25, 10),
        (160, 35),
        [i['modloader']+'_'+i['mcver'] for i in installs['installs']]
    )

    b2 = ui.Button(
        window,
        (190, 10),
        "+",
        (35, 35),
        font=(None,30),
        on_click=lambda _: Thread(target=select_version,args=(window,)).start()
    )

    window.mainloop()

def add_ver(d2, d3):
    log.trace(f'add_ver({d2=},{d3=})')
    if not (d2.value and d3.value):
        return
    installs['installs'].append({
        "mcver": d2.value,
        "modloader": d3.value
    })

def select_version(window:ui.Window):
    log.trace(f'select_version({window=})')
    window.title = 'Select Version'

    c = window.children
    window.children = []

    d2 = ui.Field(
        window,
        (10, 10),
        (None, 30),
        '',
        placeholder='MCVer',
        size=(85, 35),
    )

    d3 = ui.Dropdown(
        window,
        (100, 10),
        (100, 35),
        mcl.mod_loader.list_mod_loader()
    )
    d3._options.append('vanilla')
    d3._selected_index = -1

    b = ui.Button(
        window,
        (205, 10),
        "+",
        (35, 35),
        font=(None,30),
        on_click=lambda _: (
            add_ver(d2,d3),
            setattr(window, 'title', FULL),
            setattr(window, 'children', c),
            setattr(d, '_options', [i['modloader']+'_'+i['mcver'] for i in installs['installs']])
        )
    )

    window.render()

def install_version(install: MinecraftInstall):
    log.trace(f'install_version({install=})')
    window = ui.Window((500,120))
    window.title = f"Installing MC {install.modloader or "Vanilla"} {install.version}"

    t = ui.Label(
        window,
        (15, 10),
        "...",
        (None, 30),
        color=(255,255,255),
        bg_color=ui.theme.current['window_bg']
    )

    p = ui.ProgressBar(
        window,
        (10,60),
        (480, 18)
    )
    p.progressive = True
    p.progress_rate = 1.0
    p.progress_slowdown = 0.05

    t2 = ui.Label(
        window,
        (10, 90),
        "[0/0]",
        (None, 26),
        color=(255,255,255),
        bg_color=ui.theme.current['window_bg']
    )

    def set_status(text):
        t.text = text
        print(f'[{p.value}/{p._max}] {t.text}')
        t2.text = f'[{p.value}/{p._max}]'

    def set_progress(num):
        p.value = num
        print(f'[{p.value}/{p._max}] {t.text}')
        t2.text = f'[{p.value}/{p._max}]'

    def set_max(num):
        p._max = num
        print(f'[{p.value}/{p._max}] {t.text}')
        t2.text = f'[{p.value}/{p._max}]'

    callback = {
        "setStatus": set_status,
        "setProgress": set_progress,
        "setMax": set_max
    }

    Thread(target=lambda x,y: (ensure_install(x,y), window.destroy()), args=(install, callback), daemon=True).start()

    window.mainloop()


