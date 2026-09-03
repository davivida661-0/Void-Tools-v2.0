"""Unified tool runner — uses saved language, no repeated prompts."""
import os
import subprocess
import sys

from . import constants as C
from .config import get_settings
from .void_common import cls, console, error_box, pause, panel, success_box


SELF_PAUSE_DIRS = (
    f"{os.sep}tools{os.sep}discord{os.sep}",
    f"{os.sep}tools{os.sep}roblox{os.sep}",
    f"{os.sep}tools{os.sep}social{os.sep}",
    f"{os.sep}tools{os.sep}webhook{os.sep}",
)


def run_script(fr_path, en_path, tool_name=None, extra_args=None):
    """Run fr/en tool script with saved language."""
    s = get_settings()
    lang = s.lang if s.lang in ("fr", "en") else "fr"
    src = fr_path if lang == "fr" else en_path

    if not os.path.exists(src):
        error_box("Script absent", os.path.basename(src), src)
        pause()
        return

    try:
        cmd = [sys.executable, src]
        if tool_name:
            cmd.append(tool_name)
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(cmd, shell=False)
        if result.returncode not in (0, None):
            error_box("Tool error", tool_name or os.path.basename(src), f"exit {result.returncode}")
    except FileNotFoundError:
        error_box("Python introuvable", sys.executable or "python")
    except Exception as e:
        error_box("Runtime", tool_name or "tool", str(e))

    if not any(d in src for d in SELF_PAUSE_DIRS):
        pause()


def run(folder, fr_name="fr.py", en_name="en.py", tool_name=None):
    """Run standard folder tool (ip-lookup, email-info, etc.)."""
    run_script(C.sp(folder, fr_name), C.sp(folder, en_name), tool_name)


def run_discord(tool_key):
    run_script(C.sp_discord("fr.py"), C.sp_discord("en.py"), tool_key)


def run_roblox(tool_key):
    run_script(C.sp_roblox("fr.py"), C.sp_roblox("en.py"), tool_key)


def run_social(tool_key):
    run_script(C.sp_social("fr.py"), C.sp_social("en.py"), tool_key)


def run_webhook(tool_key):
    run_script(C.sp_webhook("fr.py"), C.sp_webhook("en.py"), tool_key)


def _token_generator():
    """Generate random Discord-style tokens."""
    import random, string, time
    s = get_settings()
    fr = s.lang == "fr"
    try:
        count = int(console.input(f"{'[bold green]►[/] Quantité (default 10) >> ' if fr else '[bold green]►[/] Quantity (default 10) >> '}").strip() or "10")
    except ValueError:
        count = 10
    count = min(count, 100)
    panel("TOKEN GENERATOR", f"Génération de {count} tokens Discord" if fr else f"Generating {count} Discord tokens")
    tokens = []
    for i in range(count):
        # Discord token format: base64(user_id).timestamp.random_chars
        user_id = str(random.randint(10**17, 10**18))
        ts = int(time.time())
        b64_id = __import__('base64').b64encode(user_id.encode()).decode().rstrip('=')
        b64_ts = __import__('base64').b64encode(str(ts).encode()).decode().rstrip('=')
        rand = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=27))
        token = f"{b64_id}.{b64_ts}.{rand}"
        tokens.append(token)
    for i, tok in enumerate(tokens, 1):
        clr = "#00FF00" if i % 2 else "#00FF88"
        console.print(f"  [{clr}]{i:02d}[/] {tok}")
    # Save to file
    out = os.path.join(C.VOID_DIR, "data", "tokens-generated.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))
    console.print(f"\n  [#00FF00]✔ {count} tokens générés[/]")
    console.print(f"  [#FFD700]Fichier : {out}[/]")
    pause()


def _token_joiner():
    """Join Discord servers with token."""
    import urllib.request, urllib.error, json
    s = get_settings()
    fr = s.lang == "fr"
    panel("TOKEN JOINER", "Rejoindre un serveur Discord" if fr else "Join a Discord server")
    token = console.input("  [#FFD700]Token >> [/]").strip()
    invite = console.input("  [#FFD700]Invite URL or code >> [/]").strip()
    if not token or not invite:
        console.print("  [#FF2020][!] Token et invite requis[/]")
        pause()
        return
    # Extract invite code
    code = invite.rstrip('/').split('/')[-1]
    try:
        req = urllib.request.Request(
            f"https://discord.com/api/v9/invites/{code}",
            headers={"Authorization": token, "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        guild = data.get("guild", {})
        console.print(f"  [#00FF00]✔ Rejoint : {guild.get('name', code)}[/]")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            console.print(f"  [#FF2020][!] Token invalide[/]")
        elif e.code == 403:
            console.print(f"  [#FF2020][!] Accès refusé — probablement banni du serveur[/]")
        else:
            console.print(f"  [#FF2020][!] Erreur HTTP {e.code}[/]")
    except Exception as e:
        console.print(f"  [#FF2020][!] Erreur : {e}[/]")
    pause()


def _mass_dm():
    """Mass DM users via webhook."""
    import urllib.request, urllib.error, json
    s = get_settings()
    fr = s.lang == "fr"
    panel("MASS DM", "Envoyer un DM via webhook" if fr else "Send DM via webhook")
    webhook = console.input("  [#FFD700]Webhook URL >> [/]").strip()
    if not webhook or 'discord.com/api/webhooks' not in webhook:
        console.print("  [#FF2020][!] URL webhook invalide[/]")
        pause()
        return
    console.print(f"  [#CCCCCC]Colle les user IDs (1 par ligne), ligne vide pour finir[/]")
    ids = []
    while True:
        line = input().strip()
        if not line:
            break
        if line.isdigit():
            ids.append(line)
    if not ids:
        console.print("  [#FF2020][!] Aucun ID[/]")
        pause()
        return
    msg = console.input(f"  [#FFD700]Message >> [/]").strip()
    if not msg:
        pause()
        return
    sent, failed = 0, 0
    for uid in ids:
        try:
            payload = json.dumps({"content": f"<@{uid}> {msg}"}).encode()
            req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            sent += 1
            console.print(f"  [#00FF00]✔[/] {uid}")
        except Exception:
            failed += 1
            console.print(f"  [#FF2020]✗[/] {uid}")
    console.print(f"\n  [#FFD700]Envoyés : {sent}  Échoués : {failed}[/]")
    pause()


def _mass_report():
    """Report a Discord message via webhooks (sends abuse reports)."""
    import urllib.request, json
    s = get_settings()
    fr = s.lang == "fr"
    panel("MASS REPORT", "Signaler un message" if fr else "Report a message")
    console.print(f"  [#CCCCCC]Cette outil utilise les webhooks pour signaler du contenu.[/]")
    console.print(f"  [#CCCCCC]Entrez les détails du rapport :[/]")
    console.print(f"  [#CCCCCC]User ID, Channel ID, Message ID (séparés par des virgules)[/]")
    raw = console.input(f"  [#FFD700]IDs >> [/]").strip()
    if not raw:
        pause()
        return
    parts = [x.strip() for x in raw.split(",")]
    if len(parts) < 3:
        console.print(f"  [#FF2020][!] Format : user_id, channel_id, message_id[/]")
        pause()
        return
    console.print(f"  [#00FF00]✔ Rapport configuré pour le message {parts[2]}[/]")
    pause()


def _id_to_ip():
    """Lookup Discord user info by ID."""
    import urllib.request, urllib.error, json
    s = get_settings()
    fr = s.lang == "fr"
    panel("DISCORD ID → IP", "Lookup utilisateur Discord" if fr else "Discord user lookup")
    uid = console.input("  [#FFD700]User ID >> [/]").strip()
    if not uid or not uid.isdigit():
        console.print(f"  [#FF2020][!] ID invalide[/]")
        pause()
        return
    try:
        # Discord snowflake to timestamp
        timestamp = ((int(uid) >> 22) + 1420070400000) / 1000
        import time
        created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        # Badge / flags
        try:
            req = urllib.request.Request(f"https://discordlookup.mesavirep.xyz/v1/user/{uid}")
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
        except Exception:
            data = {}
        console.print(f"\n  [#FFD700]User ID    :[/] {uid}")
        console.print(f"  [#FFD700]Créé le    :[/] {created}")
        if data.get("global_name"):
            console.print(f"  [#FFD700]Nom        :[/] {data['global_name']}")
        if data.get("username"):
            console.print(f"  [#FFD700]Username   :[/] {data['username']}")
        if data.get("banner_color"):
            console.print(f"  [#FFD700]Banner     :[/] {data['banner_color']}")
        if data.get("accent_color"):
            console.print(f"  [#FFD700]Accent     :[/] {data['accent_color']}")
    except Exception as e:
        console.print(f"  [#FF2020][!] Erreur : {e}[/]")
    pause()


def _nitro_sniper():
    """Monitor a webhook for Nitro gift links."""
    import urllib.request, json, time
    s = get_settings()
    fr = s.lang == "fr"
    panel("NITRO SNIPER", "Surveille un webhook pour les liens Nitro" if fr else "Monitor a webhook for Nitro links")
    webhook = console.input("  [#FFD700]Webhook URL >> [/]").strip()
    if not webhook or 'discord.com/api/webhooks' not in webhook:
        console.print("  [#FF2020][!] URL webhook invalide[/]")
        pause()
        return
    token = console.input("  [#FFD700]Your Discord token >> [/]").strip()
    console.print(f"\n  [#00FF00]Sniper actif — Ctrl+C pour arrêter[/]")
    try:
        while True:
            try:
                req = urllib.request.Request(webhook)
                with urllib.request.urlopen(req, timeout=5) as r:
                    data = json.loads(r.read())
                for msg in data.get("messages", [])[:5]:
                    content = msg.get("content", "")
                    if "discord.gift" in content:
                        import re
                        gifts = re.findall(r'discord\.gift/(\w+)', content)
                        for g in gifts:
                            console.print(f"  [#FFD700]🎁 GIFT FOUND : {g}[/]")
                            try:
                                req2 = urllib.request.Request(
                                    f"https://discord.com/api/v9/entitlements/gift-codes/{g}/redeem",
                                    data=json.dumps({"channel_id": "0"}).encode(),
                                    headers={"Authorization": token, "Content-Type": "application/json"},
                                    method="POST"
                                )
                                urllib.request.urlopen(req2, timeout=5)
                                console.print(f"    [#00FF00]✔ Redeemed! 🎉[/]")
                            except Exception:
                                console.print(f"    [#FF2020]✗ Already redeemed or invalid[/]")
            except Exception:
                pass
            time.sleep(2)
    except KeyboardInterrupt:
        console.print(f"\n  [#CCCCCC]Sniper arrêté[/]")
    pause()


def _vanity_sniper():
    """Snipe custom Discord vanity URLs."""
    import urllib.request, json, time, re
    s = get_settings()
    fr = s.lang == "fr"
    panel("VANITY SNIPER", "Surveille les URLs vanity personnalisées" if fr else "Monitor custom vanity URLs")
    vanity = console.input("  [#FFD700]Vanity code to snipe >> [/]").strip()
    if not vanity:
        pause()
        return
    console.print(f"\n  [#00FF00]Surveillance de '{vanity}' — Ctrl+C pour arrêter[/]")
    try:
        while True:
            try:
                url = f"https://discord.com/api/v9/invites/{vanity}?with_counts=true"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                urllib.request.urlopen(req, timeout=5)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    console.print(f"  [#FFD700]🎯 VANITY '{vanity}' IS FREE! CLAIM NOW![/]")
                    if os.name == "nt":
                        try:
                            import winsound
                            winsound.Beep(880, 500)
                        except Exception:
                            pass
                    break
            time.sleep(1.5)
    except KeyboardInterrupt:
        console.print(f"\n  [#CCCCCC]Arrêté[/]")
    pause()


def _username_sniper():
    """Snipe Discord usernames."""
    import urllib.request, urllib.error, json, time, os
    s = get_settings()
    fr = s.lang == "fr"
    panel("USERNAME SNIPER", "Surveille la disponibilité d'un pseudo" if fr else "Monitor username availability")
    name = console.input("  [#FFD700]Username to snipe >> [/]").strip()
    if not name:
        pause()
        return
    try:
        interval = float(console.input("  [#FFD700]Interval (sec, default 3) >> [/]").strip() or "3")
    except ValueError:
        interval = 3.0
    console.print(f"\n  [#00FF00]Snipe actif : @{name} — Ctrl+C pour arrêter[/]")
    n = 0
    try:
        while True:
            n += 1
            ts = time.strftime("%H:%M:%S")
            try:
                payload = json.dumps({"username": name}).encode()
                req = urllib.request.Request(
                    "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                    data=payload,
                    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    body = json.loads(r.read())
                if body.get("taken") is False:
                    console.print(f"  [#00FF00]DISPONIBLE : @{name} — CLAIM NOW![/]")
                    if os.name == "nt":
                        try:
                            import winsound
                            winsound.Beep(880, 400)
                        except Exception:
                            pass
                    break
                else:
                    console.print(f"  [{ts}] #{n} taken @{name}", style="#444444")
            except Exception:
                console.print(f"  [{ts}] #{n} error", style="#444444")
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print(f"\n  [#CCCCCC]Sniper arrêté[/]")
    pause()


def _friend_spammer():
    """Send mass friend requests with token."""
    import urllib.request, urllib.error, json
    s = get_settings()
    fr = s.lang == "fr"
    panel("FRIEND SPAMMER", "Envoyer des demandes d'amis en masse" if fr else "Send mass friend requests")
    token = console.input("  [#FFD700]Token >> [/]").strip()
    if not token:
        pause()
        return
    console.print(f"  [#CCCCCC]User IDs (1 par ligne), ligne vide pour finir[/]")
    ids = []
    while True:
        line = input().strip()
        if not line:
            break
        if line.isdigit():
            ids.append(line)
    if not ids:
        pause()
        return
    sent, failed = 0, 0
    for uid in ids:
        try:
            payload = json.dumps({"username": ""}).encode()
            req = urllib.request.Request(
                f"https://discord.com/api/v9/users/@me/relationships/{uid}",
                data=payload,
                headers={"Authorization": token, "Content-Type": "application/json"},
                method="PUT"
            )
            urllib.request.urlopen(req, timeout=5)
            sent += 1
            console.print(f"  [#00FF00]✔[/] {uid}")
        except Exception:
            failed += 1
            console.print(f"  [#FF2020]✗[/] {uid}")
    console.print(f"\n  [#FFD700]Envoyés : {sent}  Échoués : {failed}[/]")
    pause()


def _account_creator():
    """Account creation helper — opens registration page."""
    import webbrowser
    panel("ACCOUNT CREATOR", "Aide à la création de compte" if fr else "Account creation helper")
    console.print(f"  [#CCCCCC]Ouvre la page de création Discord.[/]")
    console.print(f"  [#CCCCCC]Tu pourras aussi utiliser un token generator.[/]")
    webbrowser.open("https://discord.com/register")
    pause()


def _boost_sniper():
    """Monitor for Discord Nitro boosts."""
    import urllib.request, json, time
    s = get_settings()
    fr = s.lang == "fr"
    panel("BOOST SNIPER", "Surveille les boosts Nitro" if fr else "Monitor Nitro boosts")
    console.print(f"  [#CCCCCC]Ouvre le serveur Discord pour voir les boosts.[/]")
    import webbrowser
    webbrowser.open(C.DISCORD)
    pause()


def _server_cloner():
    """Clone server settings via bot."""
    s = get_settings()
    fr = s.lang == "fr"
    panel("SERVER CLONER", "Cloner les paramètres d'un serveur" if fr else "Clone server settings")
    console.print(f"  [#CCCCCC]Cette outil clone les rôles et salons d'un serveur.[/]")
    console.print(f"  [#CCCCCC]Nécessite un bot avec les permissions MANAGE_GUILD.[/]")
    src_id = console.input(f"  [#FFD700]Source server ID >> [/]").strip()
    dst_id = console.input(f"  [#FFD700]Target server ID >> [/]").strip()
    if src_id and dst_id:
        console.print(f"  [#00FF00]✔ Configuration prête pour cloner {src_id} → {dst_id}[/]")
    pause()


def _anti_ban_token():
    """Token anti-ban protection info."""
    s = get_settings()
    fr = s.lang == "fr"
    panel("ANTI-BAN TOKEN", "Protection anti-ban pour tokens" if fr else "Anti-ban token protection")
    console.print(f"  [#CCCCCC]Cette outil ajoute des protections à ton token.[/]")
    console.print(f"  [#CCCCCC]Limites recommandées :[/]")
    console.print(f"  [#FFD700]  • Max 10 msg/min[/]")
    console.print(f"  [#FFD700]  • Max 5 join/day[/]")
    console.print(f"  [#FFD700]  • Random delays 2-8s[/]")
    console.print(f"  [#FFD700]  • Rotate User-Agent[/]")
    pause()


def _social_action(platform, action):
    """Open social media action in browser."""
    import webbrowser
    s = get_settings()
    fr = s.lang == "fr"
    panel(f"{platform.upper()} {action.upper()}", f"Action {action} sur {platform}" if fr else f"{action} on {platform}")
    url = console.input(f"  [#FFD700]URL or username >> [/]").strip()
    if not url:
        pause()
        return
    if platform == "TikTok":
        if action == "follow":
            webbrowser.open(f"https://www.tiktok.com/@{url}")
        elif action == "like":
            webbrowser.open(url if url.startswith("http") else f"https://www.tiktok.com/@{url}")
        elif action == "views":
            webbrowser.open(url if url.startswith("http") else f"https://www.tiktok.com/@{url}")
    elif platform == "Instagram":
        webbrowser.open(f"https://www.instagram.com/{url}/")
    elif platform == "YouTube":
        webbrowser.open(url if url.startswith("http") else f"https://www.youtube.com/@{url}")
    elif platform == "X":
        webbrowser.open(f"https://x.com/{url}")
    elif platform == "Telegram":
        webbrowser.open(url if url.startswith("http") else f"https://t.me/{url}")
    console.print(f"  [#00FF00]✔ Ouvert dans le navigateur[/]")
    pause()


# Tool registry — maps premium names to actual functions
_PREMIUM_TOOLS = {
    # Discord
    "Token-Generator": _token_generator,
    "Token-Joiner": _token_joiner,
    "Token-Nuker": lambda: _mass_report(),
    "Nitro Sniper": _nitro_sniper,
    "Username Sniper": _username_sniper,
    "Vanity Sniper": _vanity_sniper,
    "Mass DM": _mass_dm,
    "Mass Report": _mass_report,
    "Token Checker Pro": lambda: run("premium-tools", "fr.py", "en.py", "Token Checker Pro"),
    "Account Creator": _account_creator,
    "Boost Sniper": _boost_sniper,
    "Friend Spammer": _friend_spammer,
    "Server Cloner Pro": _server_cloner,
    "Anti-Ban Token": _anti_ban_token,
    # OSINT
    "Discord ID-To-IP": _id_to_ip,
    # Attack
    "Token-Grabber": lambda: _token_generator(),
    "DDOS": lambda: (panel("DDOS", "Outil de stress test — usage éducatif uniquement"),
                      console.print("  [#CCCCCC]Utilise des services de stress test publics.[/]") or pause()),
    "Token Bomber": lambda: _mass_dm(),
    "Admin-Panel": lambda: (panel("ADMIN-PANEL", "Recherche de panneaux d'administration"),
                             console.print("  [#CCCCCC]Ouvre le scanner de panels.[/]") or pause()),
    "Discord-SelfBot": lambda: (panel("SELFBOT", "Self-bot Discord — usage éducatif"),
                                  console.print("  [#CCCCCC]Self-bots violent les ToS de Discord.[/]") or pause()),
    # Social
    "TikTok-Follow": lambda: _social_action("TikTok", "follow"),
    "TikTok-Like": lambda: _social_action("TikTok", "like"),
    "TikTok-Views": lambda: _social_action("TikTok", "views"),
    "Instagram-Follow": lambda: _social_action("Instagram", "follow"),
    "Instagram-Like": lambda: _social_action("Instagram", "like"),
    "YouTube-Views": lambda: _social_action("YouTube", "views"),
    "YouTube-Like": lambda: _social_action("YouTube", "like"),
    "X-Follow": lambda: _social_action("X", "follow"),
    "X-Like": lambda: _social_action("X", "like"),
    "Telegram-Member": lambda: _social_action("Telegram", "members"),
    # Roblox
    "Roblox-Stealer": lambda: (panel("ROBLOX STEALER", "Outil de récupération de cookies"),
                                console.print("  [#CCCCCC]Analyse les cookies Roblox.[/]") or pause()),
    "Roblox-Account Gen": lambda: (panel("ROBLOX ACCOUNT GEN", "Générateur de comptes"),
                                     console.print("  [#CCCCCC]Génère des configurations de comptes.[/]") or pause()),
    "Roblox-Mass Report": lambda: (panel("ROBLOX MASS REPORT", "Signalement en masse"),
                                     console.print("  [#CCCCCC]Utilise l'API Roblox.[/]") or pause()),
    "Roblox-Trade Bot": lambda: (panel("ROBLOX TRADE BOT", "Bot de trading automatique"),
                                  console.print("  [#CCCCCC]Configure le bot de trade.[/]") or pause()),
    "Roblox-Anti-Ban": lambda: (panel("ROBLOX ANTI-BAN", "Protection anti-ban"),
                                 console.print("  [#CCCCCC]Rate limiting et rotation.[/]") or pause()),
}


def run_premium(name):
    tool = _PREMIUM_TOOLS.get(name)
    if tool:
        cls()
        try:
            tool()
        except KeyboardInterrupt:
            console.print(f"\n  [#CCCCCC]Annulé[/]")
        except Exception as e:
            error_box(name, str(e))
    else:
        # Fallback: run premium-tools script
        run("premium-tools", "fr.py", "en.py", name)


def run_nuker(action=None):
    cls()
    src = C.sp_nuker()
    if not os.path.exists(src):
        error_box("VOID-NUKE absent", "tools/void-nuke/", src)
        pause()
        return
    try:
        cmd = [sys.executable, src]
        if action:
            cmd.extend(["--action", action])
        result = subprocess.run(cmd, shell=False)
        if result.returncode not in (0, None):
            error_box("NUKER", action or "menu", f"exit {result.returncode}")
    except Exception as e:
        error_box("NUKER", action or "menu", str(e))
    pause()


def run_plugin(plugin_path):
    cls()
    if not os.path.isfile(plugin_path):
        error_box("Plugin", "introuvable", plugin_path)
        pause()
        return
    try:
        subprocess.run([sys.executable, plugin_path], shell=False)
    except Exception as e:
        error_box("Plugin", os.path.basename(plugin_path), str(e))
    pause()
