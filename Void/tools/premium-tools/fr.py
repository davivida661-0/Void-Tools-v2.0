import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import os, time, math

_VOID = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _VOID not in sys.path:
    sys.path.insert(0, _VOID)

from lib import constants as C
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

C_GOLD    = "#FFD700"
C_GOLD2   = "#FFA500"
C_SILVER  = "#CCCCCC"

ASCII = r"""
   ██████╗ ██████╗ ███████╗███╗   ███╗██╗██╗   ██╗███╗   ███╗
   ██╔══██╗██╔══██╗██╔════╝████╗ ████║██║██║   ██║████╗ ████║
   ██████╔╝██████╔╝█████╗  ██╔████╔██║██║██║   ██║██╔████╔██║
   ██╔═══╝ ██╔══██╗██╔══╝  ██║╚██╔╝██║██║██║   ██║██║╚██╔╝██║
   ██║     ██║  ██║███████╗██║ ╚═╝ ██║██║╚██████╔╝██║ ╚═╝ ██║
   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
"""

def boot(tool_name):
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")
    lines = ASCII.strip("\n").split("\n")
    t0 = time.time()
    try:
        while time.time() - t0 < 1.4:
            t = time.time() - t0
            sys.stdout.write("\033[H\n")
            for line in lines:
                sys.stdout.write("  ")
                for c, ch in enumerate(line):
                    if ch == " ":
                        sys.stdout.write(" ")
                    else:
                        v = max(40, min(255, int(180 + 75 * math.sin(t * 10 - c * 0.2))))
                        sys.stdout.write(f"\033[38;2;{v};{int(v*0.7)};0m{ch}")
                sys.stdout.write("\033[0m\n")
            sys.stdout.write(f"\n  \033[38;2;120;100;0m{tool_name.upper()}   |   U L T R A   P R E M I U M\033[0m\n")
            sys.stdout.flush()
            time.sleep(0.025)
    finally:
        sys.stdout.write("\033[?25h\033[0m")
    os.system("cls" if os.name == "nt" else "clear")

def main(tool_name):
    boot(tool_name)
    with Progress(
        SpinnerColumn(spinner_name="dots2", style="green"),
        TextColumn("[bold green]VÉRIFICATION DE LA LICENCE VOID..."),
        console=console, transient=True
    ) as p:
        p.add_task("", total=None)
        time.sleep(1.5)
        
    console.print("\n" * 2)
    pnl = Panel(
        Align.center(Group(
            Text.from_markup(f"\n[bold #00FF00]✔ LICENCE VERIFIED — ACCESS GRANTED[/]"),
            Text.from_markup(f"\n[white]Module [bold #00FF00]{tool_name}[/] débloqué avec succès."),
            Text.from_markup(f"\n[white]Tous les modules premium sont maintenant accessibles."),
            Text.from_markup(f"\n[dim white]Void-Tools v{C.VERSION} · Full Access[/]")
        )),
        border_style="#00FF00", box=box.DOUBLE_EDGE, padding=(1, 5), title="[bold #00FF00]VOID_PREMIUM_UNLOCKED"
    )
    console.print(Align.center(pnl))
    console.print("\n")
    console.input(Align.center(" [dim]Appuyez sur [bold green]ENTRÉE[/] pour revenir...[/]"))

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Unknown Module"
    try: main(name)
    except KeyboardInterrupt: pass
