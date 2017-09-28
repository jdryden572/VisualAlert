  _    _         __      ___                 _          _           _   
 | |  | |        \ \    / (_)               | |   /\   | |         | |  
 | |__| |_   _  __\ \  / / _ ___ _   _  __ _| |  /  \  | | ___ _ __| |_ 
 |  __  | | | |/ _ \ \/ / | / __| | | |/ _` | | / /\ \ | |/ _ \ '__| __|
 | |  | | |_| |  __/\  /  | \__ \ |_| | (_| | |/ ____ \| |  __/ |  | |_ 
 |_|  |_|\__,_|\___| \/   |_|___/\__,_|\__,_|_/_/    \_\_|\___|_|   \__|
                                                                        
                                                                       
James Dryden & Brett Nelson
OSIsoft, LLC
July 2014
---------------------------

Last update: Sept. 2017 - JDryden

HueVisualAlert controls a Philips Hue system to serve as a visual alerting 
system for the Technical Support phone queue. 

Compatibility tested with Python 3.5.4.

Requires modules from pip:
 - requests
 - requests-negotiate-sspi

This program can be run directly by invoking "python HueVisualAlert.py" in 
the command line. For production, it can be compiled to a Windows executable
using PyInstaller: http://www.pyinstaller.org/

Invoke "pyinstaller HueVisualAlert.py --onefile" to compile to exe.

HueVisualAlert uses the phue module by Nathanaël Lécaudé. More info can be
found at https://github.com/studioimaginaire/phue

