# wifihide

Wi-Fi SSID and password change automation via router CLI

**Description**

The main purpose of this package is to secure Wi-Fi routers by using automatic change of the SSIDs and passwords (could be configured using cron scheduler), which could mitigate undesirable third-party actions like Wi-Fi SSID surveillance, any possible hacking attempts such as observing and capturing Wi-Fi keys during connection negotiation process or bruteforcing passwords on a specific SSID.

**Configuration instructions**

1. All configuration files are stored into a platform-specific user directories. Basically it is '~/.config/wifihide' on Mac and Linux, for Windows it is 'C:/AppData/Local/wifihide'. Program needs three configuration files: settings.ini, .ssid\_prefixes and .ssid\_endings. All these files by default contain sample data need to be overwritten.  
    1.1. Populate settings.ini with the actual data relying on your router CLI specific commands, current platform and system environment. Carefully read given comments and examples.
    1.2. Populate two configuration files *.ssid\_prefixes* and *.ssid\_endings* with the lists of your own SSID prefixes and endings. Each item on a single line. Avoid using blank lines and spaces.
2. In order to notify a group of Wi-Fi users with the new credentials, you can either create a Telegram bot along with a group chat or email list. Settings file has two pre-configured options for this purpose. More detailed instuctions and examples could be found in the settings.ini file itself. Note, that in order to send emails you also need to have a proper configured mail tools and environment appropriate for sending emails (otherwise most of the mail platforms, such as Gmail, could block your emails or put them into a spam folder). If neither a Telegram bot nor mail were configured, after a successfull execution program will print new credentials to the screen and a logfile.
3. For security reasons, such things as router administrative credentials could be placed into the system environment variables. For Mac and Linux it could be done by using .bashrc or .profile configuration files, e.g. export ROUTER\_PASS="YOUR\_PASS" etc. For Windows use Advanced System Settings from within a Control Panel.
It is strongly recommended not to store your router credentials anywhere if it does not correspond to your security policy. In that case you will be able to run program manually and credentials will be asked during its startup.

**Terms of use and licensing**

This software is distributed "AS IS" under a MIT license. You can use, modify, redistribute it as a part of any software product. Use it at your own risk. Author is not responsible for any potential damage, data loss or other dire consequences caused by use of this project or its components. For detailed licensing information please refer to the LICENSE file.
