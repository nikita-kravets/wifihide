""" 
 Wi-Fi SSID and password updater
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 Version 0.0.5 / June 2025
 Author Nikita Kravets (nikita.kravets@gmail.com)

 Could be used to secure personal Wi-Fi by automation of periodic changing of its SSID and password
 which, in turn, could mitigate potential security issues.

 Program needs three configuration files: settings.ini, containig main program settings, 
 .ssid_prefixes and .ssid_endings, containing lists of the beginigs and endings for creating 
 random SSID names.  

 Note, that Wi-Fi passwords are created by using a simple algorithm based on current date and microtime. 

 For more detailed information about usage please refer to README.md and pydoc.

 Distributed under the MIT license.
"""

import pexpect
import os
import hashlib
import datetime
import random
import time
import argparse
import configparser
import platform
from importlib.metadata import version

if platform.system() == "Darwin":
    try:
        import macwifi
        _wifi = "macwifi"
    except ImportError:
        pass
elif platform.system() == "Windows":
    try:
        import winwifi
        _wifi = "winwifi"
    except ImportError:
        pass
from pathlib import Path
from colorama import Fore, Style
from getpass import getpass

ROUTER_ADMIN_ENV = "ROUTER_ADMIN"
ROUTER_PASS_ENV = "ROUTER_PASS"

class Logger:
    """Yet another implementation of a simple colorized logger.
    
    Usage: 
         Logger.log("<your message>",Logger.<INFO | WARNING | ERROR | SUCCESS (default)>).

    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    
    @classmethod
    def __get_color(cls, level: str = SUCCESS):
        if level == cls.WARNING:
            return Fore.YELLOW
        elif level == cls.ERROR:
            return Fore.RED
        elif level == cls.INFO:
            return Fore.BLUE
        return Fore.GREEN
    
    @classmethod
    def out(cls, msg: str, level: str = SUCCESS, callback = print):
        """Message output to some destination using callback (default to a console)."""
        if not (msg and callback):
            return

        if not callable(callback):
            raise Exception("Parameter 'callback' should reference to a callable function!")
        
        plevel = f"[{level}]".ljust(12)
        callback(cls.__get_color(level) + f"{Style.BRIGHT}{plevel}{Style.RESET_ALL}{msg}")

def parse_config(confpath: str) -> tuple:
    """Reads and parses the main config file.

    Returns:
        All pre-configured data needed for program executution as a tuple.
    """
    config = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
    config.read(confpath)

    ROUTER = "ROUTER"
    POST_EXEC = "POST_EXEC"
    EXEC = "EXEC_"
    MISC = "MISC"
    
    ssid_default = config[ROUTER]["ssid_default"]
    router_admin = config[ROUTER]["router_admin"] if "router_admin" in config[ROUTER]\
            else os.getenv(ROUTER_ADMIN_ENV)
    router_pass = config[ROUTER]["router_pass"] if "router_pass" in config[ROUTER]\
            else os.getenv(ROUTER_PASS_ENV)
    botcmd_tpl = config[POST_EXEC]["botcmd_tpl"]
    mailcmd_tpl = config[POST_EXEC]["mailcmd_tpl"]
    secret_phrase = config[MISC]["secret_phrase"].strip()
    
    commands = []
    commands.append(config[ROUTER]["conn_cmd"])

    i = 1

    while True:
        key = EXEC + str(i)
        if not key in config:
            break
        commands.append({
            "cmd": config[key]["cmd"],
            "exp": (config[key]["exp"] if "exp" in config[key] else None),
            "append": (config[key]["append"] if "append" in config[key] else "")})
        i = i + 1 

    return commands, ssid_default, router_admin, router_pass, botcmd_tpl, mailcmd_tpl, secret_phrase
    
def ssid_parts(confpath: str) -> list:
    """Populates a specific list with the lines of a given file.

    Returns:
        A list of the strings without empty entries.
    """
    result = None
    
    with open(confpath, "r") as f:
        result = list(filter(None, f.read().splitlines()))
    
    return result

def combine(a: list, b: list, ssid_default: str) -> str:
    """Combines two random elements from a given arrays.

    Parameters:
        a: a list of possible SSID prefixes.
        b: a list of possible SSID endings.
    
    Returns:
        A new SSID string. 
        Note that ending is not added if prefix equals to ssid_default.
    """
    if not len(a):
        return ssid_default

    choice_a = random.choice(a)
    
    if choice_a == ssid_default:
        return ssid_default

    return choice_a + "-" + random.choice(b)

def connect(cmd: str, login: str, password: str) -> pexpect.spawn:
    """Implements basic connection functionality.

    Parameters:
        cmd: router connection command.
        login: router administrative login.
        password: router password.

    Returns:
        Opened terminal session.
    """
    terminal = pexpect.spawn(cmd)
    terminal.expect("Login:")
    terminal.sendline(login)
    terminal.expect("Password:")
    terminal.sendline(password)
    terminal.expect("(config)", timeout = 3)

    return terminal

def execute(cmd: str, terminal: pexpect.spawn, expline: str = "(config)", timeout: int = 2):
    """Executes router command using an opened terminal session.

    Parameters:
        cmd: any valid router command.
        terminal: an opened pexpect terminal session.
        expline: any terminal reponse should appear after command execution.
        timeout: a maximum amount of time to wait given terminal response to appear.
    """
    terminal.sendline(cmd)
    
    if expline:
        terminal.expect(expline, timeout)

def wifi_reconnect(ssid: str, password: str) -> bool:
    """Tries to reconnect to Wi-Fi.

    Returns:
        True if connection was successful, otherwise False.
    """
    reconnected = False
        
    if _wifi is not None:
        Logger.out("Trying to reconnect to Wi-Fi using updated SSID and password (3 attempts)...", 
                   Logger.INFO)
        
        for i in range(1,4):
            Logger.out("Attempt %d..." % i, Logger.INFO)
            time.sleep(5)
            try:
                if _wifi == "macwifi":
                    macwifi.connect(ssid, password)
                    reconnected = True
                elif _wifi == "winwifi":
                    winwifi.WinWiFi.connect(ssid, password, True)
                    reconnected = True
                break
            except Exception:
                continue

        if not reconnected:
            Logger.out("Oops! It seems that we cannot reconnect to Wi-Fi!", Logger.WARNING)
    else:
        Logger.out("It seems that your platform doesn't support automatic Wi-Fi reconnection!", 
                   Logger.WARNING)
 
    return reconnected

def passwd_gen(secret_phrase: str = "") -> tuple:
    """Performs simple password generation based on current microtime and date.
    A password which should be used for Wi-Fi authentication is a concatenation 
    of both: newpass and secret.
    Newpass along with SSID is sent to the target user who already 
    knows what is the secret part should be 
    ("-" + "2 digits, representing current date" or a pre-configured secret prhase).

    Parameters:
        secret: None or the vaule of the parameter secret_phrase
        
    Returns:
        New password divided in two parts as tuple.
    """
    newpass = "#" + str(hashlib.md5(str(datetime.datetime.now().microsecond).encode()).hexdigest())[3:9]
    secret = "-" + (str(datetime.date.today().day).rjust(2, "0") if not secret_phrase else secret_phrase)

    return newpass, secret

def extend_path(file_name: str) -> str:
    """Creates default config path dependent on a platform"""
    app_name = os.path.basename(__file__).replace(".py", "")

    if platform.system() == "Windows":
        return str(Path.home().joinpath(str(os.environ.get("localappdata")), app_namei, file_name))

    return str(Path.home().joinpath(".config", app_name, file_name))

def check_necessary(path: str):
    """Checks whether a config file needed for the program to run exists. 
    If not - tries to copy it from the package bundle directory.
    """
    try:
        conf_dir = os.path.dirname(__file__) + "/conf"
        dest_dir = os.path.dirname(path)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        copy_cmd = "copy" if platform.system() == "Windows" else "cp"
        
        if not os.path.exists(path):
            os.system(f"{copy_cmd} '{conf_dir}/{os.path.basename(path)}' '{path}'")
    except Exception as e:
        Logger.out(f"An error '{str(e)}' occured while copying required config file!", Logger.ERROR)

def main():
    parser = argparse.ArgumentParser()

    def_ini = extend_path("settings.ini")
    check_necessary(def_ini)
    parser.add_argument("--version","-V",help="print installed version",action='store_true')
    parser.add_argument("--config-file", type=str,
                        default=def_ini,
                        help=f"path to program configuration. default: {def_ini}")
    def_pfx = extend_path(".ssid_prefixes")
    check_necessary(def_pfx)
    parser.add_argument("--ssid-prefix-list-file", type=str,
                        default=def_pfx,
                        help=f"path to SSID prefix list file. default: {def_pfx}")
    def_end = extend_path(".ssid_endings")
    check_necessary(def_end)
    parser.add_argument("--ssid-ending-list-file", type=str,
                        default=def_end,
                        help=f"path to SSID ending list file. default: {def_end}")
    parser.add_argument("--send-mail", 
                        help="if given, program will try to send out new credentials by mail using pre-configured command template from the settings.ini file", 
                        action="store_true")
    parser.add_argument("--send-bot", 
                        help="if given, program will try to send out new credentials via a Telegram bot using pre-configured command template from the settings.ini file", 
                        action="store_true")

    parsed, args = parser.parse_known_args()
    args_valid = True
    
    if os.path.exists(parsed.config_file):
        try:
            commands, ssid_default, router_admin, router_pass, botcmd_tpl, mailcmd_tpl, secret_phrase = \
                    parse_config(parsed.config_file)
        except Exception:
            Logger.out(f"Config file {Style.BRIGHT}'{parsed.config_file}'{Style.RESET_ALL} invalid!", 
                       Logger.ERROR)
            args_valid = False
    else:
        Logger.out(f"Config file {Style.BRIGHT}'{parsed.config_file}'{Style.RESET_ALL} should exist!", 
                   Logger.ERROR)
        args_valid = False
    
    if os.path.exists(parsed.ssid_prefix_list_file):
        ssid_prefixes = ssid_parts(parsed.ssid_prefix_list_file)
    else:
        Logger.out(f"SSID prefix file {Style.BRIGHT}'{parsed.ssid_prefix_list_file}'{Style.RESET_ALL} should exist!", 
                   Logger.ERROR)
        args_valid = False
     
    if os.path.exists(parsed.ssid_ending_list_file):
        ssid_endings = ssid_parts(parsed.ssid_ending_list_file)
    else:
        Logger.out(f"SSID ending file {Style.BRIGHT}'{parsed.ssid_ending_list_file}'{Style.RESET_ALL} should exist!", 
                   Logger.ERROR)
        args_valid = False

    argsp = vars(parsed)

    if argsp["version"] == True:
        print(f"Current version: {Style.BRIGHT}{Fore.RED}{version('wifihide')}{Style.RESET_ALL}")
        return

    send_mail = argsp["send_mail"] == True
    send_bot = argsp["send_bot"] == True

    if not args_valid:
        return
    
    newssid = combine(ssid_prefixes, ssid_endings, ssid_default)
    newpass, secret = passwd_gen(secret_phrase)

    print(secret)

    #prepare parameters for router commands
    params = {"ssid":newssid, "password": newpass + secret}

    #prepare notification commands
    mailcmd = mailcmd_tpl.format(newssid, newpass)
    botcmd = botcmd_tpl.format(newssid, newpass)
    
    # trying to get router admin username and password from env
    Logger.out("Authenticating to router CLI", Logger.INFO)

    if not router_admin:
        router_admin = input("Login: ")
    else:
        Logger.out(f"Using pre-configured router username {Style.BRIGHT}{Fore.WHITE}{router_admin}{Style.RESET_ALL}", 
                   Logger.INFO)
    
    if not router_pass:
        router_pass = getpass()
    else:
        Logger.out(f"Using pre-configured router password {Style.BRIGHT}{Fore.WHITE}******{Style.RESET_ALL}", 
                   Logger.INFO)

    connected = False

    for cmd in commands:
        if not connected:
            try:
                terminal = connect(cmd,router_admin,router_pass)
                connected = True
            except Exception:
                Logger.out("An error occurred while connecting to router", Logger.ERROR)
                break
        else:
            execute(cmd["cmd"] + ((" " + params[cmd["append"]]) if "append" in cmd and cmd["append"] else ""), 
                    terminal, cmd["exp"])

    if connected:
        terminal.close()
        if not wifi_reconnect(newssid, newpass + secret):
            Logger.out(f"Please try to check new credentials manually: {Style.BRIGHT}{Fore.WHITE}SSID: {newssid}, Password: {newpass}{secret}{Style.RESET_ALL}", 
                       Logger.WARNING)
        else:
            Logger.out("Wi-Fi reconnection successful!")

            # Post-exection procedures 
            # send mail using pre-configured command
            if mailcmd and send_mail:
                Logger.out("Trying to send updated creds by email")
                os.system(mailcmd)

            # send message via a Telegram bot using pre-configured command
            if botcmd and send_bot:
                Logger.out("Trying to send updated creds to a Telegram bot")
                os.system(botcmd)

            if not (send_mail or send_bot):
                Logger.out("Neither --send-mail nor --send-bot parameter was given. Just output new creds to a terminal", 
                           Logger.INFO)
                Logger.out(f"{Style.BRIGHT}{Fore.WHITE}SSID: {newssid}, Password: {newpass}{secret}{Style.RESET_ALL}", 
                           Logger.INFO)
    else:
        Logger.out("Please check if your configuration is valid, router is accessible and try again...", 
                   Logger.WARNING)

if __name__ == "__main__":
    main()
