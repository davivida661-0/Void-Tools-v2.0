"""Check and optionally install Python dependencies."""
import importlib
import subprocess
import sys
import os

# Core dependencies required for the application to function
REQUIRED = [
    ("colorama", "colorama"),
    ("rich", "rich"),
]

# Optional dependencies used by specific tools
OPTIONAL = [
    ("dns.resolver", "dnspython"),
    ("requests", "requests"),
    ("aiohttp", "aiohttp"),
    ("bs4", "beautifulsoup4"),
    ("discord", "discord.py"),
    ("pynput", "pynput"),
    ("phonenumbers", "phonenumbers"),
    ("pyzipper", "pyzipper"),
    ("websocket", "websocket-client"),
    ("urllib3", "urllib3"),
]


def check_deps(auto_install=True) -> bool:
    """Check if all dependencies are installed, optionally install missing ones.
    
    Args:
        auto_install: If True, automatically install missing packages via pip
        
    Returns:
        True if all required dependencies are satisfied, False otherwise
    """
    missing = []
    for mod, pkg in REQUIRED + OPTIONAL:
        try:
            importlib.import_module(mod.split(".")[0] if "." in mod else mod)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return True

    req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
    if auto_install:
        pkgs = list(dict.fromkeys(missing))
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q"] + pkgs,
                check=False,
                capture_output=True,
            )
            return True
        except Exception:
            pass
    return len([p for p in missing if p in [x[1] for x in REQUIRED]]) == 0


def get_installed_versions():
    """Return a dict of package_name -> installed_version for all known deps."""
    versions = {}
    for mod, pkg in REQUIRED + OPTIONAL:
        try:
            module = importlib.import_module(mod.split(".")[0] if "." in mod else mod)
            version = getattr(module, "__version__", "unknown")
            versions[pkg] = version
        except ImportError:
            versions[pkg] = "not installed"
    return versions


def print_deps_status():
    """Print the status of all dependencies to console."""
    from .void_common import console
    from rich.table import Table
    
    table = Table(title="Dependencies Status", show_header=True)
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Required", style="yellow")
    
    versions = get_installed_versions()
    for pkg, version in versions.items():
        is_required = any(p[1] == pkg for p in REQUIRED)
        status = "✓" if version != "not installed" else "✗"
        table.add_row(pkg, f"{status} {version}", "Yes" if is_required else "No")
    
    console.print(table)
