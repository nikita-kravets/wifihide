# wifihide

Wi-Fi SSID and password change automation via router CLI.

#### Description

The main purpose of this package is to secure Wi-Fi routers by using automatic change of the SSIDs and passwords (could be configured using system scheduler), which could mitigate undesirable third-party actions like Wi-Fi SSID surveillance, any possible hacking attempts such as capturing Wi-Fi keys during connection negotiation process or bruteforcing passwords on a specific SSID. Additionally, since not all devices support connecting to a hidden SSIDs, there may be no option to secure your Wi-Fi other than changing its SSID periodically. 

#### Configuration instructions

1. All configuration files are stored into a platform-specific user directories. Basically it is '~/.config/wifihide' on Mac and Linux, for Windows it is 'C:/AppData/Local/wifihide'. Program needs three configuration files: settings.ini, .ssid\_prefixes and .ssid\_endings. All these files by default contain sample data which would be overwritten according to your own needs. 
    - Populate settings.ini with the actual data relying on your router CLI specific commands, current platform and system environment. Carefully read given comments and examples.
    - Populate two configuration files *.ssid\_prefixes* and *.ssid\_endings* with the lists of your own SSID prefixes and endings. Each item on a single line. Avoid using blank lines and spaces. In case when you want to keep your SSID unchanged you can either leave these two files empty and configure *ssid\_default* setting or avoid configuring SSID CLI command for automatic execution.
2. In order to notify a group of Wi-Fi users about newly generated credentials, you can either create a Telegram bot along with a group chat or email list. For this purpose *settings.ini* file has two pre-configured options in the \[POST\_EXEC\] block. More detailed instructions and examples could be found in the settings.ini file itself. Note, that in order to send emails you also need to have a proper configured mail tools and environment appropriate for sending emails (otherwise most of the mail platforms, such as Gmail, could block your emails or put them into a spam folder). If neither a Telegram bot nor mail were configured, after a successful execution program will print new credentials to the screen.
3. For security reasons, such things as router administrative credentials could be placed into the system environment variables. For Mac and Linux it could be done by using .bashrc or .profile configuration files, e.g. export ROUTER\_PASS="YOUR\_PASS" etc. For Windows use Advanced System Settings from within a Control Panel.

**SECURITY WARNING!** It is strongly recommended **not to store** plain-text credentials anywhere if it does not correspond to your security policy. By leaving credentials empty you will be able to run program manually and perform router CLI authentication during each startup. In case when your router supports SSH key-based CLI authentication, it would be the best option to configure program to login via SSH.

#### Usage

**wifihide** \[-h\] \[--version\] \[--config-file CONFIG\_FILE\] \[--ssid-prefix-list-file SSID\_PREFIX\_LIST\_FILE\] \[--ssid-ending-list-file SSID\_ENDING\_LIST\_FILE\] \[--send-mail\] \[--send-bot\]

options:
    -h, --help            show this help message and exit
    --version, -V         print installed version
    --config-file CONFIG\_FILE
                        path to program configuration
    --ssid-prefix-list-file SSID\_PREFIX\_LIST\_FILE
                        path to SSID prefix list file
    --ssid-ending-list-file SSID\_ENDING\_LIST\_FILE
                        path to SSID ending list file
    --send-mail           if given, program will try to send out new credentials by mail using pre-configured
                        command template from the settings.ini file
    --send-bot            if given, program will try to send out new credentials via a Telegram bot using pre-
                        configured command template from the settings.ini file.

#### Terms of use and licensing

This software is distributed "AS IS" under a MIT license. You can use, modify, redistribute it as a part of any software product. Use it at your own risk. Author is not responsible for any potential damage, data loss or other dire consequences caused by use of this project or its components. For detailed licensing information please refer to the LICENSE file.
