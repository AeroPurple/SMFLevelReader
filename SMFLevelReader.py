import tkinter as tk
from tkinter import filedialog
import sys
import os
from os import listdir
from os.path import dirname, basename, splitext, join
from struct import pack
import math
from multiprocessing.sharedctypes import Value
import traceback
import time
import re
import shutil
import builtins
win32gui_imported=False
try:
    import win32gui
    win32gui_imported=True
except:
    pass
    
from sys import exit
from subprocess import call
try:
    from strlib import str as strlib
    from strlib import date as release_date
    from strlib import smfe_background_names, smfe_music_names, smf2_background_names, smf2c_background_names, smf2c_music_names, smf2_powerup_names, smf2_entrance_types, smf2_entrance_powerups, smf2_exit_types, smf_tiles, smf2_tiles
except:
    print("Critical Error: string library not found")
    exit(1)

try:
    import colorscheme
    from colorscheme import colorScheme
except:
    colorScheme={
        "default":"",
        "bold":"",
        "error":"",
        "warning":"",
        "success":"",
        "link":"",
        "null":"",
        "typeerror":"",
        "command":"",
        "subcommand":"",
        "section":"",
        "value":"",
        "typeinvalid":""
    }

def get_application_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

curses_imported=False
try:
    import curses
    curses_imported=True
except:
    pass

keyboard_imported=False
try:
    import keyboard
    keyboard_imported=True
except:
    pass

titleScreenWaitTime=0
decorType=0
current_command=0
usedCommands=[]
        
def checkForeground():
    try:
        window_handle=win32gui.GetForegroundWindow()
        window_title=win32gui.GetWindowText(window_handle)
        return window_title
    except:
        return 0

current_window=checkForeground()

def isFocusedConsole():
    return checkForeground()==current_window

try:
    screenx,screeny=shutil.get_terminal_size()
except:
    screenx=80
    screeny=25
    
    output="┌"
    message="│ "+strlib["err_con_size_1"].center(screenx-4, " ")+" │"
    for i in range (screenx-2):
        output+="─"
    output+="┐"
    print(output)
    output="│"
    for i in range (screenx-2):
        output+=" "
    output+="│"
    print(output)
    print(message)
    message="│ "+strlib["err_con_size_2"].center(screenx-4, " ")+" │"
    print(output)
    print(message)
    message="│ "+strlib["err_con_size_3"].center(screenx-4, " ")+" │"
    print(output)
    print(message)
    message="│ "+strlib["err_con_size_4"].center(screenx-4, " ")+" │"
    print(output)
    print(message)
    for i in range (screeny-10):
        print(output)
    output="└"
    for i in range (screenx-2):
        output+="─"
    output+="┘"
    print(output)
    while True:
        event=keyboard.read_event()
        if event.event_type==keyboard.KEY_DOWN and isFocusedConsole():
            key=event.name
            if key=="enter":
                break

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    for i in range(screeny): # Windows Terminal force wipe
        output=""
        for j in range(screenx):
            output+="█"
        print(output)
    for i in range(screeny):
        output=""
        for j in range(screenx):
            output+=" "
        print(output)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

awaitInput_commands={
    "open": lambda arg: processFile(arg),
    "export": lambda arg, value: exportAll(arg, value),
    "import": lambda arg, value: importTiles(arg, value),
    "settings": lambda dummy: changeConfig(),
    "replace": lambda arg1, arg2: replace(arg1, arg2),
    "header": lambda arg: printInfo(),
    "help": lambda arg, dummy: generalHelp(arg),
    "exit": lambda dummy: (clear(),exit(0))[1],
}

# [accepted values,definition,cut latter text for use in argument,is next part a command,commands allowed,scan twice?...]
awaitInput_deabbreviator=[
    [["open ","o "],"open",True,False],
    [["open","o"],"open",False],
    [["export ","exp ","e "],"export",True,True,False,
        [
            [["csv "],"csv",True],
            [["csv"],"csv",False],
            [["txt "],"txt",True],
            [["txt"],"txt",False],
            [["map "],"map",True],
            [["map"],"map",False]
        ]
    ],
    [["exit","x"],"exit",True,False],
    [["export","exp","e"],"export",True,True,False,
        [
            [[""],"",False]
        ]
    ],
    [["import ","imp ","i "],"import",True,True,False,
        [
            [["level ","lvl ","l "],"lvl",True],
            [["level","lvl","l"],"lvl",False],
            [["bonus ","bns ","b "],"bns",True],
            [["bonus","bns","b"],"bns",False],
            [["layer 1 ","layer1 ","l1 "],"l1",True],
            [["layer 1","layer1","l1"],"l1",False],
            [["layer 2 ","layer2 ","l2 "],"l2",True],
            [["layer 2","layer2","l2"],"l2",False]
        ]
    ],
    [["import","imp"],"import",True,True,False,
        [
            [[""],"",False]
        ]
    ],
    [["i"],"import",True,True,False,
        [
            [["level ","lvl ","l "],"lvl",True],
            [["level","lvl","l"],"lvl",False],
            [["bonus ","bns ","b "],"bns",True],
            [["bonus","bns","b"],"bns",False],
            [["layer 1 ","layer1 ","l1 "],"l1",True],
            [["layer 1","layer1","l1"],"l1",False],
            [["layer 2 ","layer2 ","l2 "],"l2",True],
            [["layer 2","layer2","l2"],"l2",False]
        ]
    ],
    [["settings","set","s"],"settings",False],
    [["replace ","rep ","r "],"replace",True,True,True,
        [
            [["header","head"],"header",False],
            [["header ","head ","h ","h"],"header",True,
                [
                    
                ]
            ],
            [["warps"],"warps",False],
            [["warp ","warp","w ","w"],"warps",True,
                [
                    
                ]
            ],
            [["entrances"],"entrances",False],
            [["entrance ","entrance","entr ","entr","n ","n"],"entrances",True,
                [
                    
                ]
            ],
            [["exits"],"exits",False],
            [["exit ","exit","x ","x"],"exits",True,
                [
                    
                ]
            ],
            [["tiles ","tiles","t ","t"],"tiles",True,
                [
                    
                ]
            ],
        ]
    ],
    [["replace","rep"],"replace",True,True,False,
        [
            [[""],"",False]
        ]
    ],
    [["r"],"replace",True,True,True,
        [
            [["header","head"],"header",False],
            [["header ","head ","h ","h"],"header",True,
                [
                    
                ]
            ],
            [["warps"],"warps",False],
            [["warp ","warp","w ","w"],"warps",True,
                [
                    
                ]
            ],
            [["entrances"],"entrances",False],
            [["entrance ","entrance","entr ","entr","n ","n"],"entrances",True,
                [
                    
                ]
            ],
            [["exits"],"exits",False],
            [["exit ","exit","x ","x"],"exits",True,
                [
                    
                ]
            ],
            [["tiles ","tiles","t ","t"],"tiles",True,
                [
                    
                ]
            ],
        ]
    ],
    [["header","h"],"header",False],
    [["help ","? ","?"],"help",True,True,False,
        [
            [[""],"",False],
            [["open","o"],"open",False],
            [["export","exp","e"],"export",False],
            [["import","imp","i"],"import",False],
            [["settings","set","s"],"settings",False],
            [["replace","rep","r"],"replace",False],
            [["header","head","h"],"header",False],
            [["help","?"],"help",False],
            [["exit","x"],"exit",False]
        ]
    ],
    [["help"],"help",True,True,False,
        [
            [[""],"",False]
        ]
    ],
]

def testInputMatch(command, toExecute):
    for i in awaitInput_deabbreviator: # iterates through all entries of awaitInput_deabbreviator
        for j in range(len(i[0])): # iterates through all command versions (e.g. i[0])
            if i[2]: # check if the first boolean placed in each entry is true or false
                if command[:len(i[0][j])]==i[0][j]: # if typed command cut to length of command version matches
                    if i[3]: # if more commands are allowed
                        for k in i[5]: # iterate through subcommands
                            for l in range(len(k[0])): # iterate through versions
                                #print(k[0][l])
                                #print(command[len(i[0][j]):len(i[0][j])+len(k[0][l])],"compared to",k[0][l])
                                if i[4]: #subsubcommands allowed?
                                    if k[2]: #cropped match
                                        if command[len(i[0][j]):len(i[0][j])+len(k[0][l])]==k[0][l]:
                                            if toExecute:
                                                awaitInput_commands[i[1]](k[1],command[len(i[0][j])+len(k[0][l]):])
                                            return True,i[0][j],True,True,command[len(i[0][j]):len(i[0][j])+len(k[0][l])],True,command[len(i[0][j])+len(k[0][l]):]
                                    else: #explicit match
                                        if command[len(i[0][j]):]==k[0][l]:
                                            if toExecute:
                                                awaitInput_commands[i[1]](k[1],command[len(i[0][j])+len(k[0][l]):])
                                            return True,i[0][j],True,True,command[len(i[0][j]):len(i[0][j])+len(k[0][l])],True,command[len(i[0][j])+len(k[0][l]):]
                                else: #subsubcommand is a value
                                    if k[2]: #cropped match
                                        if command[len(i[0][j]):len(i[0][j])+len(k[0][l])]==k[0][l]:
                                            if toExecute:
                                                awaitInput_commands[i[1]](k[1],command[len(i[0][j])+len(k[0][l]):])
                                            return True,i[0][j],True,True,command[len(i[0][j]):len(i[0][j])+len(k[0][l])],False,command[len(i[0][j])+len(k[0][l]):]
                                    else: #explicit match
                                        if command[len(i[0][j]):]==k[0][l]:
                                            if toExecute:
                                                awaitInput_commands[i[1]](k[1],command[len(i[0][j])+len(k[0][l]):])
                                            return True,i[0][j],True,True,command[len(i[0][j]):len(i[0][j])+len(k[0][l])],False,command[len(i[0][j])+len(k[0][l]):]
                        return True,i[0][j],True,False,command[len(i[0][j]):] #matched/not, command, has subcommand, matched/not subcommand, subcommand
                    else:
                        if toExecute:
                            awaitInput_commands[i[1]](command[len(i[0][j]):]) # execute from command library with args
                        return True,i[0][j],False,command[len(i[0][j]):] # matched/not, command, is next part a command, argument
            else:
                if command==i[0][j]: # if typed command EXPLICITLY matches with command version, highlight
                    if toExecute:
                        awaitInput_commands[i[1]]("") # execute from command library with args
                    return True,i[0][j],False,"" # matched/not, command, is next part a command, dummy argument
    return False,command # matched/not, command
        
def input(prefaceString, failSafeCommand):
    global current_command
    global usedCommands
    
    command=""
    awaitInputMode=False
    print(prefaceString, end='', flush=True)
    
    if prefaceString=="→ ":
        awaitInputMode=True
    while True:
        erased=0
        event=keyboard.read_event()
        if event.event_type==keyboard.KEY_DOWN and isFocusedConsole():
            key=event.name
            if key=="enter":
                print("")
                break
            elif key=="esc" and not awaitInputMode:
                print(strlib["exit_input"])
                return failSafeCommand
            elif key=="backspace":
                erased=1
                command=command[:-1]
                current_command=len(usedCommands)
            elif key=="space":
                command+=" "
                current_command=len(usedCommands)
            elif key=="down" and awaitInputMode:
                if len(usedCommands)>0:
                    current_command=(current_command+1)%len(usedCommands)
                    command=usedCommands[current_command]
            elif key=="up" and awaitInputMode:
                if len(usedCommands)>0:
                    current_command=(current_command-1)%len(usedCommands)
                    command=usedCommands[current_command]
            elif len(key)<=1:
                if key=="&" and (game=="smf2" or game=="smf2c"):
                    command+="and"
                elif key=="(" and (game=="smf" or game=="smfe"):
                    command+="["
                elif key==")" and (game=="smf" or game=="smfe"):
                    command+="]"
                else:
                    command+=key
                current_command=len(usedCommands)
            output=""
            if awaitInputMode:
                if not testInputMatch(command, False)[0]:
                    output+=colorScheme["typeinvalid"]+command
                else:
                    output+=colorScheme["command"]+testInputMatch(command, False)[1]
                    if testInputMatch(command, False)[2]:
                        if testInputMatch(command, False)[3]:
                            if testInputMatch(command, False)[5]:
                                output+=colorScheme["subcommand"]+testInputMatch(command, False)[4]+colorScheme["section"]+testInputMatch(command, False)[6]
                            else:
                                output+=colorScheme["subcommand"]+testInputMatch(command, False)[4]+colorScheme["value"]+testInputMatch(command, False)[6]
                        else:
                            output+=colorScheme["typeinvalid"]+testInputMatch(command, False)[4]
                    else:
                        output+=colorScheme["value"]+testInputMatch(command, False)[3]
            else:
                output+=colorScheme["value"]+command
            output+=colorScheme["default"]
            
            print(u"\u001b["+str(math.ceil((len(prefaceString)+len(command)-1)/screenx))+"A")
            print(" "*(screenx*(math.ceil((len(prefaceString)+len(command)-1)/screenx))), end='', flush=True)
            print(u"\u001b["+str(math.ceil((len(prefaceString)+len(command)-1+erased*2)/screenx))+"A")
            print("\r"+prefaceString+output, end='', flush=True)
    return command.replace("\\n","\n")

versionNames=[0,"0.9","0.10 Beta"]
configVersion=0
programVersion=2
firstRun=False
colorschemeMissing=False

decorTypes=[" ","─","━","═"]

def convertToConfigData(versionIndex,waitTime,decorType,useANSI):
    return (((versionIndex<<8|waitTime)<<2|decorType)<<1|(useANSI))<<7
    
def configSave(versionIndex,waitTime,decorType,useANSI):
    configData=convertToConfigData(versionIndex,waitTime,decorType,useANSI)
    configData=configData.to_bytes(3,'big')
    configFile=open(os.path.join(get_application_path(), 'Settings.cfg'),mode='wb')
    configFile.write(configData)
    configFile.close()

def configLoad():
    global configVersion
    global titleScreenWaitTime
    global decorType
    global useANSI
    global firstRun
    
    try:
        configFile=open(os.path.join(get_application_path(), 'Settings.cfg'),mode='rb')
    except:
        configSave(programVersion,62,2,1)
        configFile=open(os.path.join(get_application_path(), 'Settings.cfg'),mode='rb')
        firstRun=True
    finally:
        try:
            configData=configFile.read()
            if int((bin(int.from_bytes(configData,'big'))[2:].zfill(16))[:6],2)==1:
                configVersion=1
                configData=bin(int.from_bytes(configData,'big'))[2:].zfill(16)
            else:
                configData=bin(int.from_bytes(configData,'big'))[2:].zfill(24)
                configVersion=int(configData[:6],2)
            if configVersion+1>len(versionNames) or versionNames[configVersion]==0:
                print(strlib["err_conf_load"])
            titleScreenWaitTime=int(configData[6:14],2)
            decorType=int(configData[14:16],2)
            useANSI=int(configData[16:17])
            configFile.close()
        except:
            configSave(programVersion,62,2,1)
        
def changeConfig():
    configLoad()
    
    global titleScreenWaitTime
    global decorType
    global useANSI
    
    try:
        console=curses.initscr()
    except:
        print(strlib["err_curses_load"])
        return
    curses.noecho()
    curses.cbreak()
    console.keypad(True)
    console.clear()
    if decorType!=0:
        console.addstr(0,0,f" {strlib['title_s']} ".center(screenx,decorTypes[decorType]))
    else:
        console.addstr(0,0,strlib["title_s"])
    if configVersion+1>len(versionNames):
        console.addstr(1,0,f"{strlib['conf_ver_title']}{strlib['conf_ver_hi']}[{configVersion}]")
    elif versionNames[configVersion]==0:
        console.addstr(1,0,f"{strlib['conf_ver_title']}{strlib['conf_ver_inv']}[{configVersion}]")
    else:
        console.addstr(1,0,f"{strlib['conf_ver_title']}"+versionNames[configVersion])
    console.addstr(2,0,f"{strlib['opt_conf_title_ms']}◄    ►")
    console.addstr(3,0,f"{strlib['opt_conf_title_pad']}◄    ►")
    console.addstr(4,0,f"{strlib['opt_conf_ansi']}◄   ►")
    console.addstr(6,0,f"[{strlib['opt_btn_reset']}]")
    console.addstr(7,0,f"[{strlib['opt_btn_cancel']}]")
    console.addstr(8,0,f"[{strlib['opt_btn_save']}]")
    current_item=0
    old_data=[titleScreenWaitTime,decorType,useANSI]
    temp_new=0
    while True:
        console.addstr(2,25,str(titleScreenWaitTime*16).rjust(4))
        if decorType==0:
            console.addstr(3,22,strlib["gen_none"])
        else:
            console.addstr(3,22,"".center(4,decorTypes[decorType]))
        if useANSI==0:
            console.addstr(4,24,strlib["gen_no"].rjust(3))
        elif useANSI==1:
            console.addstr(4,24,strlib["gen_yes"].rjust(3))
        console.addstr(6,1,strlib["opt_btn_reset"])
        console.addstr(7,1,strlib["opt_btn_cancel"])
        console.addstr(8,1,strlib["opt_btn_save"])
        if current_item==0:
            console.addstr(2,25,str(titleScreenWaitTime*16).rjust(4),curses.A_REVERSE)
        elif current_item==1:
            if decorType==0:
                console.addstr(3,22,strlib["gen_none"],curses.A_REVERSE)
            else:
                console.addstr(3,22,"".center(4,decorTypes[decorType]),curses.A_REVERSE)
        elif current_item==2:          
            if useANSI==0:
                console.addstr(4,24,strlib["gen_no"].rjust(3),curses.A_REVERSE)
            elif useANSI==1:
                console.addstr(4,24,strlib["gen_yes"].rjust(3),curses.A_REVERSE)
        elif current_item==3:
            console.addstr(6,1,strlib["opt_btn_reset"],curses.A_REVERSE)
        elif current_item==4:
            console.addstr(7,1,strlib["opt_btn_cancel"],curses.A_REVERSE)
        elif current_item==5:
            console.addstr(8,1,strlib["opt_btn_save"],curses.A_REVERSE)
        console.refresh()
        key=console.getch()
        #console.addstr(11,0,str(key)+"   ")
        console.refresh()
        if key==10: # Enter
            if current_item<3:
                current_item=(current_item+1)%6
            else:
                if current_item==3:
                    titleScreenWaitTime,decorType,useANSI=[62,2,1]
                    configSave(programVersion,titleScreenWaitTime,decorType,useANSI)
                elif current_item==4:
                    titleScreenWaitTime,decorType,useANSI=old_data
                elif current_item==5:
                    configSave(programVersion,titleScreenWaitTime,decorType,useANSI)
                try:
                    colorscheme.defineColors()
                except:
                    pass
                curses.endwin()
                print(strlib["exit_s"])
                return
        elif key==curses.KEY_DOWN:
            current_item=(current_item+1)%6
        elif key==curses.KEY_UP:
            current_item=(current_item-1)%6
        elif key==curses.KEY_LEFT:
            if current_item==0:
                if titleScreenWaitTime>0:
                    titleScreenWaitTime-=1
            elif current_item==1:
                if decorType>0:
                    decorType-=1
            elif current_item==2:
                useANSI=(useANSI-1)%2
        elif key==curses.KEY_RIGHT:
            if current_item==0:
                if titleScreenWaitTime<255:
                    titleScreenWaitTime+=1
            elif current_item==1:
                if decorType<3:
                    decorType+=1
            elif current_item==2:
                useANSI=(useANSI+1)%2

def generalHelp(command):
    if command=="":
        print(colorScheme["bold"]+"SMF Level Reader v"+versionNames[programVersion]+"\nReleased on "+release_date+" by AeroPurple"+colorScheme["default"]+"\n")
        print("Available commands:\n"+colorScheme["command"]+"open | o\nexport | exp | e\nimport | imp | i\nsettings | set | s\nreplace | rep | r\nheader | head | h\nhelp | ?\nexit | x"+colorScheme["default"])
        print("\nType in "+colorScheme["command"]+"help"+colorScheme["default"]+" "+colorScheme["bold"]+"[command]"+colorScheme["default"]+" | "+colorScheme["command"]+"?"+colorScheme["default"]+" "+colorScheme["bold"]+"[command]"+colorScheme["default"]+" to learn more about how each command works.")
    elif command=="open":
        print(colorScheme["bold"]+"Open Command"+colorScheme["default"])
        print("This command opens up a File Explorer dialogue and allows you to select a file. This file is then automatically parsed and can be edited.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"open"+colorScheme["default"])
        print(colorScheme["command"]+"o"+colorScheme["default"])
    elif command=="export":
        print(colorScheme["bold"]+"Export Command"+colorScheme["default"])
        print("This command exports an opened Super Mario Flash level to your desired format, such as Comma Separated Values (can be edited in Excel), the original SMF text format, or an experimental text format that contains a visual representation of level tiles.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"export"+colorScheme["default"]+" "+colorScheme["bold"]+"[format]"+colorScheme["default"])
        print(colorScheme["command"]+"exp"+colorScheme["default"]+" "+colorScheme["bold"]+"[format]"+colorScheme["default"])
        print(colorScheme["command"]+"e"+colorScheme["default"]+" "+colorScheme["bold"]+"[format]"+colorScheme["default"])
        print("\n"+colorScheme["bold"]+"Accepted Values"+colorScheme["default"])
        print("csv | txt | map")
    elif command=="import":
        print(colorScheme["bold"]+"Import Command"+colorScheme["default"])
        print("This command replaces specified tiles with a Comma Seperated Values (CSV) file.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"import"+colorScheme["default"]+" "+colorScheme["bold"]+"[type of tile data]"+colorScheme["default"])
        print(colorScheme["command"]+"imp"+colorScheme["default"]+" "+colorScheme["bold"]+"[type of tile data]"+colorScheme["default"])
        print(colorScheme["command"]+"i"+colorScheme["default"]+" "+colorScheme["bold"]+"[type of tile data]"+colorScheme["default"])
        print("\n"+colorScheme["bold"]+"Accepted Values"+colorScheme["default"])
        print("level | lvl | l\nbonus | bns | b\nlayer 1 | layer1 | l1\nlayer 2 | layer2 | l2")
    elif command=="settings":
        print(colorScheme["bold"]+"Settings Command"+colorScheme["default"])
        print("This command opens a Curses interface that allows you to customize how the program functions and looks.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"settings"+colorScheme["default"])
        print(colorScheme["command"]+"set"+colorScheme["default"])
        print(colorScheme["command"]+"s"+colorScheme["default"])
    elif command=="replace":
        print(colorScheme["bold"]+"Replace Command"+colorScheme["default"])
        print("This command replaces various variables in the current level.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"replace"+colorScheme["default"]+" "+colorScheme["bold"]+"header [variable or command] [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"replace"+colorScheme["default"]+" "+colorScheme["bold"]+"warp/entrance/exit [warp sublevel and number or command] [variable or command] [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"replace"+colorScheme["default"]+" "+colorScheme["bold"]+"tiles [type of tile data] [tile selection] [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"rep"+colorScheme["default"]+" "+colorScheme["bold"]+"header [variable or command]  [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"rep"+colorScheme["default"]+" "+colorScheme["bold"]+"warp/entrance/exit [warp sublevel and number or command] [variable or command] [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"rep"+colorScheme["default"]+" "+colorScheme["bold"]+"tiles [type of tile data] [tile selection] [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"r"+colorScheme["default"]+" "+colorScheme["bold"]+"header [variable or command]  [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"r"+colorScheme["default"]+" "+colorScheme["bold"]+"warp/entrance/exit [warp sublevel and number or command] [variable or command] [new value]"+colorScheme["default"])
        print(colorScheme["command"]+"r"+colorScheme["default"]+" "+colorScheme["bold"]+"tiles [type of tile data] [tile selection] [new value]"+colorScheme["default"])
        time.sleep(1)
        print("\n"+colorScheme["bold"]+"Accepted Values"+colorScheme["default"])
        print("Data Groups:")
        print("\theader | head | h\n\twarp | w\n\tentance | entr | n\n\texit | x\n\ttiles | t")
        time.sleep(1)
        print("\n"+colorScheme["bold"]+"Commands/Variables"+colorScheme["default"])
        print("Header:\n\tname | n\n\tlevel width | lvlwidth | lvlw | lw\n\tlevel background | lvlbg | lb\n\tlevel music | lvlmus | lm\n\tbonus background | bnsbg | bb\n\tbonus music | bnsmus | bm\n\tstart x | startx | sx\n\tstart y | starty | sy\n\tstart sublevel | start at | startat | sa\n\tdescription | desc | d\n\tbackground | bg | b\n\tmusic | mus |m\n\tstartstate | powerup | p\n\turl1 | u1\n\turl2 | u2\n\tlayer priority 1 | lpri 1 | lp1\n\tlayer priority 2 | lpri 2 | lp2\n\tlayer2 xpos | layer2 x | l2x\n\tlayer2 ypos | layer2 y | l2y")
        time.sleep(1)
        print("Warps:\n\tadd | +\n\tremove | rem | -\n\txpos | x\n\typos | y\n\tsublevel | sublvl | s\n\txposto | xt\n\typosto | yt\n\tdirection | dir | d\n\tanimation | anim | type | t")
        time.sleep(1)
        print("Entrances/Exits:\n\tadd | +\n\tremove | rem | -\n\tswap | s\n\txpos | x\n\typos | y\n\ttype | t\n\tstate | s\n\tlinkto | l")
        time.sleep(1)
        print("Tile Ranges:\n\tThe colon signifies a range. As in, 90:100 would select 10 columns/rows.\n\tThe comma separates the X range/columns from the Y range/rows.\n\tThe space separates the tile selection from the specified replacement value.\n\tSome examples:\n\t'4:5,8:9 100' selects tiles from x4y8 to x5y9 and replaces them with tile ID 100.\n\t'4:5,8' selects tiles 4 through 5 in the 8th column.\n\t'4,8' selects tile in position x4y8.")
        time.sleep(1)
        print("\n"+colorScheme["bold"]+"Examples"+colorScheme["default"])
        print("replace header name Hi! -- this will replace the current level name with \"Hi!\".")
        print("replace header music 5 -- this will replace the current level music with Underwater.")
        print("replace warp level add -- this will add a new warp to the list of level warps.")
        print("replace warp level 2 remove -- this will remove warp no.3 from the list of level warps.")
        print("replace warp bonus 3 xpos -- this will changes bonus warp no.4's X position.")
        print("replace entrance 5 swap 6 -- this will swap entrances ID 5 and ID 6.")
        print("replace tiles layer1 0:10,0:10 241 -- this will replace a 10x10 square in the upper left corner of the level with coins.")
        print("\nIf no value is specified, like in 'replace header name', you will be prompted to assign a value.")
        print("If no variable is specified, like in 'replace header', a Curses user interface containing all of the variables for that data group will appear.")
    elif command=="header":
        print(colorScheme["bold"]+"Header Command"+colorScheme["default"])
        print("This command will print formatted header data, similar to what happens when you open a file.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"header"+colorScheme["default"])
        print(colorScheme["command"]+"head"+colorScheme["default"])
        print(colorScheme["command"]+"h"+colorScheme["default"])
    elif command=="help":
        print(colorScheme["bold"]+"Help Command"+colorScheme["default"])
        print("This command prints useful info on how to use this program.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"help"+colorScheme["default"]+" "+colorScheme["bold"]+"[command]"+colorScheme["default"])
        print(colorScheme["command"]+"?"+colorScheme["default"]+" "+colorScheme["bold"]+"[command]"+colorScheme["default"])
    elif command=="exit":
        print(colorScheme["bold"]+"Exit Command"+colorScheme["default"])
        print("This command exits this program.")
        print("\n"+colorScheme["bold"]+"Syntax"+colorScheme["default"])
        print(colorScheme["command"]+"exit"+colorScheme["default"])
        print(colorScheme["command"]+"x"+colorScheme["default"])

#print(smf2_tiles[406][0]+" - Tile 406 - "+smf2_tiles[406][1])
#print(smf2c_background_names[42])

game=""

level_name=""
level_background=""
level_music=""
start_xpos=""
start_ypos=""
start_at=""
level_width=""
bonus_background=""
bonus_music=""
bonus_width=""
level=[]
bonus=[]
level_warps=[]
bonus_warps=[]

level_description=""
level_author=""
level_message=""
level_url1=""
level_bg_url2=""
level_powerup=""
level_width=""
level_height=""
level_variable_1=""
level_variable_2=""
level_layer_priority=""
level_layer2_width=""
level_layer2_height=""
level_layer2_xpos=""
level_layer2_ypos=""
level_layer_priority_2=""
level_variable_3=""
all_entrances=[]
all_exits=[]
layer_1=[]
layer_2=[]

def printInfo():
    if game=="smf" or game=="smfe":
        if game=="smf":
            print(strlib["info_game"]+strlib["info_smf"])
        elif game=="smfe":
            print(strlib["info_game"]+strlib["info_smfe"])
        print(strlib["info_name"]+level_name) if level_name!="" else print(strlib["gen_none_f"])
        try:
            print(strlib["info_level_bg"]+level_background+" ("+smfe_background_names[int(level_background)]+")")
        except:
            print(strlib["info_level_bg"]+level_background+" ("+smfe_background_names[0]+")")
        try:
            print(strlib["info_level_mus"]+level_music+" ("+smfe_music_names[int(level_music)]+")")
        except:
            print(strlib["info_level_mus"]+level_music+" ("+smfe_music_names[0]+")")
            
        #### THE FOLLOWING IS SOME REAL MESSY CODE. FIX RIGHT NOW ####################################################
        
        if int(level_width)/20!=math.floor(int(level_width)/20) and (int(level_width)<320 or int(level_width)>4500):
            print(strlib["info_level_x"]+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles, no right border, unintended size)")
        elif int(level_width)/20!=math.floor(int(level_width)/20):
            print(strlib["info_level_x"]+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles, no right border)")
        elif (int(level_width)<320 or int(level_width)>4500):
            print(strlib["info_level_x"]+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles, unintended size)")
        else:
            print(strlib["info_level_x"]+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles)")
        try:
            print(strlib["info_bonus_bg"]+bonus_background+" ("+smfe_background_names[int(bonus_background)]+")")
        except:
            print(strlib["info_bonus_bg"]+bonus_background+" ("+smfe_background_names[0]+")")
        try:
            print(strlib["info_bonus_mus"]+bonus_music+" ("+smfe_music_names[int(bonus_music)]+")")
        except:
            print(strlib["info_bonus_mus"]+bonus_music+" ("+smfe_music_names[0]+")")
        if int(bonus_width)/20!=math.floor(int(bonus_width)/20) and (int(bonus_width)<320 or int(bonus_width)>4500):
            print(strlib["info_bonus_x"]+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles, no right border, unintended size)")
        elif int(bonus_width)/20!=math.floor(int(bonus_width)/20):
            print(strlib["info_bonus_x"]+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles, no right border)")
        elif (int(bonus_width)<320 or int(bonus_width)>4500):
            print(strlib["info_bonus_x"]+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles, unintended size)")
        else:
            print(strlib["info_bonus_x"]+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles)")    
        print(strlib["info_start"]+f"{start_at} @ xPos {start_xpos} yPos {start_ypos} ({int(start_xpos)/20}{strlib['info_gen_tx']}{int(start_ypos)/20}{strlib['info_gen_ty']})")
        print(strlib["info_level_warps"])
        for i in range(len(level_warps)):
            if level_warps[i][2]=="Level" or level_warps[i][2]=="Bonus":
                warp_end_sublevel_print=level_warps[i][2]
            else:
                warp_end_sublevel_print=level_warps[i][2]+f" ({strlib['gen_inv']}"+strlib["gen_softlocker"]+")"
            if level_warps[i][5]=="right" or level_warps[i][5]=="left":
                warp_end_direction_print="facing "+level_warps[i][5]
            else:
                warp_end_direction_print=colorScheme["warning"]+"glitchy entrance ("+level_warps[i][5]+")"+colorScheme["default"]
            if level_warps[i][6]=="Up" or level_warps[i][6]=="Down" or level_warps[i][6]=="Left" or level_warps[i][6]=="Right":
                warp_end_type_print="Pipe "+level_warps[i][6]+" Animation"
            elif level_warps[i][6]=="Appear":
                warp_end_type_print=strlib["info_no_anim"]
            else:
                warp_end_type_print=colorScheme["warning"]+"invalid animation \""+level_warps[i][6]+"\" ("+strlib["gen_softlocker"]+")"
            warp_print=f"\tWarp from xPos {int(level_warps[i][1])*20} yPos {int(level_warps[i][0])*20} to xPos {level_warps[i][3]} yPos {level_warps[i][4]} in {warp_end_sublevel_print}, {warp_end_direction_print}, {warp_end_type_print}"
            
            print(warp_print)
        if level_warps==[]:
            warp_print=f"\t{strlib['gen_none_f']}"
            print(warp_print)
        print(colorScheme["bold"]+"Bonus Warps:"+colorScheme["default"])
        for i in range(len(bonus_warps)):
            if bonus_warps[i][2]=="Level" or bonus_warps[i][2]=="Bonus":
                warp_end_sublevel_print=bonus_warps[i][2]
            else:
                warp_end_sublevel_print=bonus_warps[i][2]+f" ({strlib['gen_inv']}"+strlib["gen_softlocker"]+")"
            if bonus_warps[i][5]=="right" or bonus_warps[i][5]=="left":
                warp_end_direction_print="facing "+bonus_warps[i][5]
            else:
                warp_end_direction_print=colorScheme["warning"]+"glitchy entrance ("+bonus_warps[i][5]+")"+colorScheme["default"]
            if bonus_warps[i][6]=="Up" or bonus_warps[i][6]=="Down" or bonus_warps[i][6]=="Left" or bonus_warps[i][6]=="Right":
                warp_end_type_print="Pipe "+bonus_warps[i][6]+" Animation"
            elif bonus_warps[i][6]=="Appear":
                warp_end_type_print=strlib["info_no_anim"]
            else:
                warp_end_type_print=colorScheme["null"]+"invalid animation \""+bonus_warps[i][6]+"\" (softlocks the game)"+colorScheme["default"]
            warp_print="\tWarp from xPos "+str(int(bonus_warps[i][1])*20)+" yPos "+str(int(bonus_warps[i][0])*20)+" to xPos "+bonus_warps[i][3]+" yPos "+bonus_warps[i][4]+" in "+warp_end_sublevel_print+", "+warp_end_direction_print+", "+warp_end_type_print
            
            print(warp_print)
        if bonus_warps==[]:
            warp_print=f"\t{strlib['gen_none_f']}"
            print(warp_print)
    elif game=="smf2" or game=="smf2c":
        if game=="smf2":
            print(strlib["info_game"]+strlib["info_smf2"])
        elif game=="smf2c":
            print(strlib["info_game"]+strlib["info_smf2c"])
        print(strlib["info_name"]+level_name) if level_name!="" else print(strlib["gen_none_f"])
        print(colorScheme["bold"]+"Description: "+colorScheme["default"]+level_description) if level_description!="" else print(strlib["gen_none_f"])
        print(colorScheme["bold"]+"Author: "+colorScheme["default"]+level_author) if level_author!="" else print(strlib["gen_none_f"])
        print(colorScheme["bold"]+"Message Block Text: «"+colorScheme["default"]+level_message+colorScheme["bold"]+"»"+colorScheme["default"])
        try:
            if game=="smf2":
                print(colorScheme["bold"]+"Background: "+colorScheme["default"]+level_background+" ("+smf2_background_names[int(level_background)]+")")
            elif game=="smf2c":
                print(colorScheme["bold"]+"Background: "+colorScheme["default"]+level_background+" ("+smf2c_background_names[int(level_background)]+")")
        except:
            print(colorScheme["bold"]+"Background: "+colorScheme["default"]+level_background+" ("+smf2_background_names[0]+")")
        if level_background=="11":
            print(colorScheme["bold"]+"Background URL 1: "+colorScheme["default"]+colorScheme["link"]+level_url1+colorScheme["default"]) if level_url1!="" else print(colorScheme["bold"]+"Background URL 1: "+colorScheme["default"]+strlib["gen_none_f"])
            print(colorScheme["bold"]+"Background URL 2: "+colorScheme["default"]+colorScheme["link"]+level_bg_url2+colorScheme["default"]) if level_bg_url2!="" else print(colorScheme["bold"]+"Background URL 2: "+colorScheme["default"]+strlib["gen_none_f"])
        try:
            print(colorScheme["bold"]+"Music: "+colorScheme["default"]+level_music+" ("+smf2c_music_names[int(level_music)]+")")
        except:
            print(colorScheme["bold"]+"Music: "+colorScheme["default"]+level_music+" ("+smf2c_music_names[0]+")")
        try:
            print(colorScheme["bold"]+"Mario's State: "+colorScheme["default"]+level_powerup+" ("+smf2_powerup_names[int(level_powerup)]+")")
        except:
            print(colorScheme["bold"]+"Mario's State: "+colorScheme["default"]+level_powerup+" ("+smf2_powerup_names[0]+")")
        print(colorScheme["bold"]+"Level Dimensions: "+colorScheme["default"]+level_width+"x"+level_height+" ("+str(int(level_height)/20)+" Rows by "+str(int(level_width)/20)+" Columns)")
        print(colorScheme["bold"]+"Unknown Variable="+colorScheme["default"]+level_variable_1)
        print(colorScheme["bold"]+"Unknown Variable="+colorScheme["default"]+level_variable_2)
        try:
            print(colorScheme["bold"]+"Layer 1 Priority: "+colorScheme["default"]+level_layer_priority+" (On Top)") if int(level_layer_priority)>=3 else print(colorScheme["bold"]+"Layer 1 Priority: "+colorScheme["default"]+level_layer_priority+" (On Bottom)")
        except:
            print(colorScheme["bold"]+"Layer 1 Priority: "+colorScheme["default"]+level_layer_priority+" (Invalid)")
        print(colorScheme["bold"]+"Layer 2 Dimensions: "+colorScheme["default"]+level_layer2_width+"x"+level_layer2_height+" ("+str(int(level_layer2_height)/20)+" Rows by "+str(int(level_layer2_width)/20)+" Columns)")
        print(colorScheme["bold"]+"Layer 2 X Offset: "+colorScheme["default"]+level_layer2_xpos)
        print(colorScheme["bold"]+"Layer 2 Y Offset: "+colorScheme["default"]+level_layer2_ypos)
        try:
            print(colorScheme["bold"]+"Layer 2 Priority: "+colorScheme["default"]+level_layer_priority_2+" (On Bottom)") if int(level_layer_priority_2)<=2 else print(colorScheme["bold"]+"Layer 2 Priority: "+colorScheme["default"]+level_layer_priority_2+" (On Top)")
        except:
            print(colorScheme["bold"]+"Layer 2 Priority: "+colorScheme["default"]+level_layer_priority_2+" (Invalid)")
        print(colorScheme["bold"]+"Unknown Variable="+colorScheme["default"]+level_variable_3)
        print(colorScheme["bold"]+"Entrances:"+colorScheme["default"])
        for i in range(len(all_entrances)):
            if i==0:
                entrance_print="\t"+colorScheme["bold"]+"ID "+str(i+1)+" (Starting Point):"+colorScheme["default"]+" "
            else:
                entrance_print="\t"+colorScheme["bold"]+"ID "+str(i+1)+":"+colorScheme["default"]+" "
            try:
                entrance_type_print=smf2_entrance_types[int(all_entrances[i][0])]
            except:
                entrance_type_print=smf2_entrance_types[10]
            
            try:
                if int(all_entrances[i][3])>0:
                    if int(all_entrances[i][3])>15:
                        entrance_mario_status_print=smf2_entrance_powerups[16]
                    else:
                        entrance_mario_status_print=smf2_entrance_powerups[int(all_entrances[i][3])]
                else:
                    entrance_mario_status_print=all_entrances[i][3]+" - "+smf2_entrance_powerups[17]
            except:
                entrance_mario_status_print=all_entrances[i][3]+" - "+smf2_entrance_powerups[17]
            
            entrance_print=entrance_print+entrance_type_print+" ["+all_entrances[i][0]+"], "+entrance_mario_status_print+" ["+all_entrances[i][3]+"] @ xPos "+all_entrances[i][1]+" yPos "+all_entrances[i][2]+" ("+str(int(all_entrances[i][1])/20)+strlib["info_gen_tx"]+str(int(all_entrances[i][2])/20)+f"{strlib['info_gen_ty']})"

            print(entrance_print)
        print(colorScheme["bold"]+"Exits:"+colorScheme["default"])
        exit_print=""
        for i in range(len(all_exits)):
            exit_print="\t"
            try: 
                exit_type_print=smf2_exit_types[int(all_exits[i][2])]
            except:
                exit_type_print=smf2_exit_types[0]

            exit_print=exit_print+exit_type_print+" ["+all_exits[i][2]+"] to "+colorScheme["bold"]+"ID "+str(int(all_exits[i][3])+1)+colorScheme["default"]+" @ xPos "+str(int(all_exits[i][0])*20)+" yPos "+str(int(all_exits[i][1])*20)+" ("+all_exits[i][0]+strlib["info_gen_tx"]+all_exits[i][1]+f"{strlib['info_gen_ty']})"
            print(exit_print)
            
        if exit_print=="":
            print(f"\t{strlib['gen_none_f']}")
    else:
        print(strlib["te_no_level"])

def openFile(filePath):
    if filePath=="":
        filePath=filedialog.askopenfilename(title=strlib["title_file_open_request"], initialdir=filePath)
        if filePath=="":
            print(strlib["te_file_open_decline"])
            return filePath, ""
    else:
        filePath=os.path.normpath(filePath)
        if os.path.isdir(filePath):
            root = tk.Tk()
            root.withdraw()

            filePath=filedialog.askopenfilename(title=strlib["title_file_open_request"], initialdir=filePath)
            if filePath=="":
                print(strlib["te_file_open_decline"])
                return filePath, ""
    try:
        file=open(filePath,mode='r', encoding="utf-8")
        return filePath, file.read()
    except UnicodeDecodeError:
        print(strlib["err_file_unicode"])
        return "", ""
    except FileNotFoundError:
        print(strlib["te_file_name"])
        return "", ""

    #print(level_code) # useful for debugging

def processFile(filePath):
    filePath, level_code=openFile(filePath)
    if filePath=="":
        return
    counter=0
    global game
    while True:
        if level_code[counter]=="(":
            game="smf"
            break
        elif level_code[counter]=="&":
            game="smf2"
            break
        elif len(level_code)-1==counter:
            break
        else:
            counter+=1

    if game=="smf":
        try:
            global level_name
            global level_background
            global level_music
            global start_xpos
            global start_ypos
            global start_at
            global level_width
            global bonus_background
            global bonus_music
            global bonus_width
            global level
            global bonus
            current_row=[]
            current_tile=""
            tiles_processed=0
            rows_processed=0
            warp_begin_xpos=""
            warp_begin_ypos=""
            warp_end_sublevel=""
            warp_end_xpos=""
            warp_end_ypos=""
            warp_end_direction=""
            warp_end_type=""
            onewarp=[]
            global level_warps
            global bonus_warps
            
            level_name=""
            level_background=""
            level_music=""
            start_xpos=""
            start_ypos=""
            start_at=""
            level_width=""
            bonus_background=""
            bonus_music=""
            bonus_width=""
            level.clear()
            bonus.clear()
            level_warps.clear()
            bonus_warps.clear()
            
            while True: # Level Data
                counter+=1
                if rows_processed<12:
                    counter-=1
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            current_tile+=level_code[counter]
                        else:
                            tiles_processed+=1
                            current_row.append(current_tile)
                            if current_tile!="":
                                if int(current_tile)>194:
                                    game="smfe"
                            if tiles_processed % 225==0:
                                frozen_row=tuple(current_row)
                                level.append(frozen_row)
                                current_row.clear()
                                rows_processed+=1
                            current_tile=""
                            break
                else:
                    break
            counter-=1
            while True: # Level Name
                counter+=1
                if level_code[counter]!=",":
                    if level_code[counter]=="&":
                        level_name+="\n"
                    else:
                        level_name+=level_code[counter]
                else:
                    break
            while True: # Background Number
                counter+=1
                if level_code[counter]!=",":
                    level_background+=level_code[counter]
                else:
                    break
            try:
                if int(level_background)>=1 and int(level_background)<=28:
                    if int(level_background)>6:
                        game="smfe"
            except:
                pass
            while True: # Mario's xPos
                counter+=1
                if level_code[counter]!=",":
                    start_xpos+=level_code[counter]
                else:
                    break
            while True: # Mario's yPos
                counter+=1
                if level_code[counter]!=",":
                    start_ypos+=level_code[counter]
                else:
                    break
            while True: # Music Number
                counter+=1
                if level_code[counter]!=",":
                    level_music+=level_code[counter]
                else:
                    break
            try:
                if int(level_music)>=1 and int(level_music)<=19:
                    if int(level_music)>11:
                        game="smfe"
            except:
                pass
            while True: # Level Width
                counter+=1
                if level_code[counter]!=",":
                    level_width+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]=="(":
                    break
            tiles_processed=0
            rows_processed=0
            while True: # Bonus Data
                counter+=1
                if rows_processed<12:
                    counter-=1
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            current_tile+=level_code[counter]
                        else:
                            tiles_processed+=1
                            current_row.append(current_tile)
                            if current_tile!="":
                                try:
                                    if int(current_tile)>194:
                                        game="smfe"
                                except:
                                    current_tile="NaN"
                            if tiles_processed % 225==0:
                                frozen_row=tuple(current_row)
                                bonus.append(frozen_row)
                                current_row.clear()
                                rows_processed+=1
                            current_tile=""
                            break
                else:
                    break
            counter-=1
            while True: # Mario Start Sublevel
                counter+=1
                if level_code[counter]!=",":
                    start_at+=level_code[counter]
                else:
                    break
            while True: # Background Number
                counter+=1
                if level_code[counter]!=",":
                    bonus_background+=level_code[counter]
                else:
                    break
            try:
                if int(bonus_background)>=1 and int(bonus_background)<=28:
                    if int(bonus_background)>6:
                        game="smfe"
            except:
                pass
            for i in range(2):
                while True:
                    counter+=1
                    if level_code[counter]==",":
                        break
            while True: # Music Number
                counter+=1
                if level_code[counter]!=",":
                    bonus_music+=level_code[counter]
                else:
                    break
            try:
                if int(bonus_music)>=1 and int(bonus_music)<=19:
                    if int(bonus_music)>11:
                        game="smfe"
            except:
                pass
            while True: # Bonus Width
                counter+=1
                if level_code[counter]!=",":
                    bonus_width+=level_code[counter]
                else:
                    break
            counter+=2
            while True: # Level Warps
                if level_code[counter]!=")":
                    counter-=1
                    if level_code[counter+1]==",":
                        counter+=1
                        if level_code[counter+1]==")":
                            break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            if level_code[counter]!="(":
                                warp_begin_ypos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_begin_xpos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_sublevel+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_xpos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_ypos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_direction+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_type+=level_code[counter]
                        else:
                            break
                    onewarp.extend([warp_begin_ypos,warp_begin_xpos,warp_end_sublevel,warp_end_xpos,warp_end_ypos,warp_end_direction,warp_end_type])
                    frozen_warp=tuple(onewarp)
                    level_warps.append(frozen_warp)
                    onewarp.clear()
                    warp_begin_xpos=""
                    warp_begin_ypos=""
                    warp_end_sublevel=""
                    warp_end_xpos=""
                    warp_end_ypos=""
                    warp_end_direction=""
                    warp_end_type=""
            counter+=2
            while True: # Bonus Warps
                if level_code[counter]!=")":
                    counter-=1
                    if level_code[counter+1]==",":
                        counter+=1
                        if level_code[counter+1]==")":
                            break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            if level_code[counter]!="(":
                                warp_begin_ypos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_begin_xpos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_sublevel+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_xpos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_ypos+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_direction+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]==")":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            warp_end_type+=level_code[counter]
                        else:
                            break
                    onewarp.extend([warp_begin_ypos,warp_begin_xpos,warp_end_sublevel,warp_end_xpos,warp_end_ypos,warp_end_direction,warp_end_type])
                    frozen_warp=tuple(onewarp)
                    bonus_warps.append(frozen_warp)
                    onewarp.clear()
                    warp_begin_xpos=""
                    warp_begin_ypos=""
                    warp_end_sublevel=""
                    warp_end_xpos=""
                    warp_end_ypos=""
                    warp_end_direction=""
                    warp_end_type=""
            printInfo()
            return
            
        except IndexError as e:
            errorString=str(e)+strlib["err_line"]+str(e.__traceback__.tb_lineno)
            print(strlib["err_parse_unterminated"]+errorString+colorScheme["default"])
            
            game=""
            
            level_name=""
            level_background=""
            level_music=""
            start_xpos=""
            start_ypos=""
            start_at=""
            level_width=""
            bonus_background=""
            bonus_music=""
            bonus_width=""
            level.clear()
            bonus.clear()
            level_warps.clear()
            bonus_warps.clear()
            
            return
        except ValueError as e:
            errorString=str(e)+strlib["err_line"]+str(e.__traceback__.tb_lineno)
            print(strlib["err_parse_tile_id"]+errorString+colorScheme["default"])
            
            game=""
            
            level_name=""
            level_background=""
            level_music=""
            start_xpos=""
            start_ypos=""
            start_at=""
            level_width=""
            bonus_background=""
            bonus_music=""
            bonus_width=""
            level.clear()
            bonus.clear()
            level_warps.clear()
            bonus_warps.clear()
            
            return
            

    elif game=="smf2":
        try:
            global level_description
            global level_author
            global level_message
            global level_url1
            global level_bg_url2
            global level_powerup
            global level_height
            global level_variable_1
            global level_variable_2
            global level_layer_priority
            global level_layer2_width
            global level_layer2_height
            global level_layer2_xpos
            global level_layer2_ypos
            global level_layer_priority_2
            global level_variable_3
            entrance_type=""
            entrance_x=""
            entrance_y=""
            entrance_mario_status=""
            oneentrance=[]
            global all_entrances
            exit_x=""
            exit_y=""
            exit_type=""
            exit_link_to=""
            oneexit=[]
            global all_exits
            global layer_1
            global layer_2
            current_row=[]
            
            tiles_processed=0
            
            level_name=""
            level_background=""
            level_music=""
            level_width=""
            level_description=""
            level_author=""
            level_message=""
            level_url1=""
            level_bg_url2=""
            level_powerup=""
            level_height=""
            level_variable_1=""
            level_variable_2=""
            level_layer_priority=""
            level_layer2_width=""
            level_layer2_height=""
            level_layer2_xpos=""
            level_layer2_ypos=""
            level_layer_priority_2=""
            level_variable_3=""
            all_entrances.clear()
            all_exits.clear()
            layer_1.clear()
            layer_2.clear()
            
            while True: # Level Name
                counter+=1
                if level_code[counter]!="&":
                    level_name+=level_code[counter]
                else:
                    break
            while True: # Level Description
                counter+=1
                if level_code[counter]!="&":
                    level_description+=level_code[counter]
                else:
                    break
            while True: # Level Author
                counter+=1
                if level_code[counter]!="&":
                    level_author+=level_code[counter]
                else:
                    break
            while True: # Message Block Text
                counter+=1
                if level_code[counter]!="&":
                    level_message+=level_code[counter]
                else:
                    break
            counter+=1
            if level_code[counter].isalpha(): # Background/Music URLs
                counter-=1
                while True:
                    counter+=1
                    if level_code[counter]!="&":
                        if level_code[counter]==" ":
                            level_url1+="%20"
                        else:
                            level_url1+=level_code[counter]
                    else:
                        break
                while True:
                    counter+=1
                    if level_code[counter]!="&":
                        if level_code[counter]==" ":
                            level_bg_url2+="%20"
                        else:
                            level_bg_url2+=level_code[counter]
                    else:
                        break
            while True: # Background Number
                if level_code[counter]=="&":
                    counter+=1
                if level_code[counter]!=",":
                    level_background+=level_code[counter]
                    counter+=1
                else:
                    break
            try:
                if int(level_background)>=1:
                    if int(level_background)>11:
                        game="smf2c"
            except:
                pass
            while True: # Music Number
                counter+=1
                if level_code[counter]!=",":
                    level_music+=level_code[counter]
                else:
                    break
            try:
                if int(level_music)>=1:
                    if int(level_music)==19:
                        game="smf2c"
            except:
                pass
            while True: # Mario's State
                counter+=1
                if level_code[counter]!=",":
                    level_powerup+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_width+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_height+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_variable_1+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_variable_2+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_layer_priority+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_layer2_width+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_layer2_height+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_layer2_xpos+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_layer2_ypos+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_layer_priority_2+=level_code[counter]
                else:
                    break
            while True:
                counter+=1
                if level_code[counter]!=",":
                    level_variable_3+=level_code[counter]
                else:
                    counter+=1
                    break
            while True:
                counter+=1
                if level_code[counter]!="&":
                    counter-=1
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            entrance_type+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]=="&":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            entrance_x+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]=="&":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            entrance_y+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]=="&":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            entrance_mario_status+=level_code[counter]
                        else:
                            break
                    oneentrance.extend([entrance_type, entrance_x, entrance_y, entrance_mario_status])
                    frozen_entrance=tuple(oneentrance)
                    all_entrances.append(frozen_entrance)
                    oneentrance.clear()
                    entrance_type=""
                    entrance_x=""
                    entrance_y=""
                    entrance_mario_status=""
                else:
                    break
            ###            ADD A PATCH FOR "smf2 - Out of The Box.txt" ##############################################
            while True:
                counter+=1
                if level_code[counter]!="&":
                    counter-=1
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            exit_x+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]=="&":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            exit_y+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]=="&":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            exit_type+=level_code[counter]
                        else:
                            break
                    if level_code[counter+1]=="&":
                        break
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            exit_link_to+=level_code[counter]
                        else:
                            break
                    oneexit.extend([exit_x, exit_y, exit_type, exit_link_to])
                    frozen_exit=tuple(oneexit)
                    all_exits.append(frozen_exit)
                    oneexit.clear()
                    exit_x=""
                    exit_y=""
                    exit_type=""
                    exit_link_to=""
                else:
                    break
            current_tile=""
            if level_code[counter+1]=="&":
                counter+=1
            while True:
                counter+=1
                if level_code[counter]!="&":
                    counter-=1
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            current_tile+=level_code[counter]
                        else:
                            tiles_processed+=1
                            current_row.append(current_tile)
                            if current_tile!="":
                                try:
                                    if int(current_tile)>406:
                                        game="smf2c"
                                except:
                                    current_tile="NaN"
                            if tiles_processed % math.floor(int(level_width)/20)==0:
                                frozen_row=tuple(current_row)
                                layer_1.append(frozen_row)
                                current_row.clear()
                            current_tile=""
                            break
                else:
                    break
            #print("Layer 1 Data")
            #for i in layer_1:
            #    print(i)
            while True:
                counter+=1
                if level_code[counter]!="&":
                    counter-=1
                    while True:
                        counter+=1
                        if level_code[counter]!=",":
                            current_tile+=level_code[counter]
                        else:
                            tiles_processed+=1
                            current_row.append(current_tile)
                            if tiles_processed % math.floor(int(level_width)/20)==0:
                                frozen_row=tuple(current_row)
                                layer_2.append(frozen_row)
                                current_row.clear()
                            current_tile=""
                            break
                else:
                    break
            #print("Layer 2 Data")
            #for i in layer_2:
            #    print(i)
            printInfo()
            return
            
        except Exception as e:
            print(strlib["err_parse_gen"]+"\nlevel_name: "+level_name+"\nlevel_description: "+level_description+"\nlevel_author: "+level_author+"\nlevel_message: "+level_message+"\nlevel_background: "+level_background+"\nlevel_url1: "+level_url1+"\nlevel_bg_url2: "+level_bg_url2+"\nlevel_music: "+level_music+"\nlevel_powerup: "+level_powerup+"\nlevel_width: "+level_width+"\nlevel_height: "+level_height+"\nlevel_variable_1: "+level_variable_1+"\nlevel_variable_2: "+level_variable_2+"\nlevel_layer_priority: "+level_layer_priority+"\nlevel_layer2_width: "+level_layer2_width+"\nlevel_layer2_height: "+level_layer2_height+"\nlevel_layer2_xpos: "+level_layer2_xpos+"\nlevel_layer2_ypos: "+level_layer2_ypos+"\nlevel_layer_priority_2: "+level_layer_priority_2+"\nlevel_variable_3: "+level_variable_3+"\noneentrance: "+str(oneentrance)+"\nall_entrances: "+str(all_entrances)+"\noneexit: "+str(oneexit)+"\nall_exits: "+str(all_exits)+"\nlayer_1: "+str(layer_1)+"\nlayer_2: "+str(layer_2)+"\ncurrent_row: "+str(current_row)+"\ntiles_processed: "+str(tiles_processed)+"\n\n"+str(e)+strlib["err_line"]+str(e.__traceback__.tb_lineno)+colorScheme["default"])
            
            game=""
            
            level_name=""
            level_background=""
            level_music=""
            level_width=""
            level_description=""
            level_author=""
            level_message=""
            level_url1=""
            level_bg_url2=""
            level_powerup=""
            level_height=""
            level_variable_1=""
            level_variable_2=""
            level_layer_priority=""
            level_layer2_width=""
            level_layer2_height=""
            level_layer2_xpos=""
            level_layer2_ypos=""
            level_layer_priority_2=""
            level_variable_3=""
            all_entrances.clear()
            all_exits.clear()
            layer_1.clear()
            layer_2.clear()
            
            return
        
    else:
        print(strlib["err_parse_no_delimiters"])
        return
        
def exportAll(fileFormat, filePath):
    if game=="smf" or game=="smfe":
        if fileFormat=="csv" or fileFormat=="txt" or fileFormat=="map": # this should be put elsewhere ###############
            if filePath=="":
                filePath=filedialog.askdirectory()
        else:
            print(strlib["te_file_type"])
            return
        if filePath=="":
            print(strlib["te_file_save_decline"])
            return
        if fileFormat=="csv":
            output=""
            print("Processing Level tiles...")
            for i in level:
                for j in i:
                    output+=j+","
                if output[-1:]==",":
                    output=output[:-1]
                output+="\n"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_level.csv"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
            output=""
            print("Processing Bonus tiles...")
            for i in bonus:
                for j in i:
                    output+=j+","
                if output[-1:]==",":
                    output=output[:-1]
                output+="\n"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_bonus.csv"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
        elif fileFormat=="txt":
            output="("
            for i in level:
                for j in i:
                    try:
                        int(j)
                        output+=j+","
                    except:
                        output+="NaN,"
            try:
                output+=level_name+","+level_background+","+start_xpos+","+start_ypos+","+level_music+","+str(int(level_width)-320)+",)("
            except:
                output+=level_name+","+level_background+","+start_xpos+","+start_ypos+","+level_music+","+level_width+",)("
            for i in bonus:
                for j in i:
                    try:
                        int(j)
                        output+=j+","
                    except:
                        output+="NaN,"
            try:
                output+=start_at+","+bonus_background+","+start_xpos+","+start_ypos+","+bonus_music+","+str(int(bonus_width)-320)+",)("
            except:
                output+=start_at+","+bonus_background+","+start_xpos+","+start_ypos+","+bonus_music+","+bonus_width+",)("
            if len(level_warps)>0:
                for i in level_warps:
                    for j in i:
                        output+=j+","
            else:
                output+=","
            output+=")("
            if len(bonus_warps)>0:
                for i in bonus_warps:
                    for j in i:
                        output+=j+","
            else:
                output+=","
            output+=")"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+".txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
        elif fileFormat=="map":
            output=""
            for i in level:
                for j in i:
                    try:
                        output+=smf_tiles[int(j)][0]
                    except:
                        output+=smf_tiles[0][0]
                output+="\n"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_level_map.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
            output=""
            for i in bonus:
                for j in i:
                    try:
                        output+=smf_tiles[int(j)][0]
                    except:
                        output+=smf_tiles[0][0]
                output+="\n"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_bonus_map.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
        print(strlib["success"])
        return
    elif game=="smf2" or game=="smf2c":
        filePath=filedialog.askdirectory()
        if filePath=="":
            print(strlib["te_file_save_decline"])
            return
        if fileFormat=="csv":
            output=""
            tiles_read=0
            for i in layer_1:
                for j in i:
                    print("Processed "+str(tiles_read)+"/"+str(int((int(level_height)/20)*(int(level_width)/20)))+" Layer 1 tiles ("+str(math.floor(tiles_read/((int(level_height)/20)*(int(level_width)/20))*100))+"% done)", end='\r')
                    output+=j+","
                    tiles_read+=1
                if output[-1:]==",":
                    output=output[:-1]
                output+="\n"
            print("Processed all "+str(tiles_read)+" tiles in Layer 1.            ")
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_layer1.csv"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
            output=""
            tiles_read=0
            for i in layer_2:
                for j in i:
                    print("Processed "+str(tiles_read)+"/"+str(int((int(level_layer2_height)/20)*(int(level_layer2_width)/20)))+" Layer 2 tiles ("+str(math.floor(tiles_read/((int(level_layer2_height)/20)*(int(level_layer2_width)/20))*100))+"% done)", end='\r')
                    output+=j+","
                    tiles_read+=1
                if output[-1:]==",":
                    output=output[:-1]
                output+="\n"
            print("Processed all "+str(tiles_read)+" tiles in Layer 2.            ")
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_layer2.csv"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
        elif fileFormat=="txt":
            output="&"+level_name+"&"+level_description+"&"+level_author+"&"+level_message+"&"
            if level_background==11:
                output+=level_url1+"&"+level_bg_url2+"&"
            output+=str(level_background)+","+str(level_music)+","+str(level_powerup)+","+str(level_width)+","+str(level_height)+","+str(level_variable_1)+","+str(level_variable_2)+","+str(level_layer_priority)+","+str(level_layer2_width)+","+str(level_layer2_height)+","+str(level_layer2_xpos)+","+str(level_layer2_ypos)+","+str(level_layer_priority_2)+","+str(level_variable_3)+",&"
            for i in all_entrances:
                for j in i:
                    output+=j+","
            output+="&"
            if len(all_exits)>0:
                for i in all_exits:
                    for j in i:
                        output+=j+","
            else:
                output+=","
            output+="&"
            for i in layer_1:
                for j in i:
                    try:
                        int(j)
                        output+=j+","
                    except:
                        output+="NaN,"
            output+="&"
            for i in layer_2:
                for j in i:
                    try:
                        int(j)
                        output+=j+","
                    except:
                        output+="NaN,"
            output+="&"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+".txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
        elif fileFormat=="map":
            output=""
            for i in layer_1:
                for j in i:
                    try:
                        output+=smf2_tiles[int(j)][0]
                    except:
                        output+=smf2_tiles[0][0]
                output+="\n"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_layer1_map.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
            output=""
            for i in layer_2:
                for j in i:
                    try:
                        output+=smf2_tiles[int(j)][0]
                    except:
                        output+=smf2_tiles[0][0]
                output+="\n"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_layer2_map.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print(strlib["te_file_busy"])
        else:
            print(strlib["te_file_type"])
            return
        print(strlib["success"])
        return
    else:
        print(strlib["te_no_level"])
        return

def importTiles(toModify, filePath):
    if toModify=="":
        print(strlib["te_import_unspecified"])
        return
    
    global level
    global bonus
    
    global layer_1
    global layer_2
    
    global level_width
    global level_layer2_width
    global level_height
    global level_layer2_height
    
    if game!="":
        if toModify=="level" or toModify=="lvl" or toModify=="l":
            if game=="smf" or game=="smfe":
                level.clear()
            elif game=="smf2" or game=="smf2c":
                print(colorScheme["typeerror"]+"Incorrect game mode - level is an SMF-only property!"+colorScheme["default"])
                return
        elif toModify=="bonus" or toModify=="bns" or toModify=="b":
            if game=="smf" or game=="smfe":
                bonus.clear()
            elif game=="smf2" or game=="smf2c":
                print(colorScheme["typeerror"]+"Incorrect game mode - bonus is an SMF-only property!"+colorScheme["default"])
                return
        elif toModify=="layer 1" or toModify=="layer1" or toModify=="l1":
            if game=="smf2" or game=="smf2c":
                layer_1.clear()
            elif game=="smf" or game=="smfe":
                print(colorScheme["typeerror"]+"Incorrect game mode - layer 1 is an SMF2-only property!"+colorScheme["default"])
                return
        elif toModify=="layer 2" or toModify=="layer2" or toModify=="l2":
            if game=="smf2" or game=="smf2c":
                layer_2.clear()
            elif game=="smf" or game=="smfe":
                print(colorScheme["typeerror"]+"Incorrect game mode - layer 2 is an SMF2-only property!"+colorScheme["default"])
                return
        else:
            print(colorScheme["typeerror"]+"Invalid Property!"+colorScheme["default"])
            return
        
        filePath, file_data=openFile(filePath)
        if filePath=="":
            return
        tile=""
        row=[]
        print("Tile import in progress...")
        for i in range(len(file_data)):
            if file_data[i]==",":
                row.append(tile)
                tile=""
            elif file_data[i]=="\n":
                if toModify=="level" or toModify=="lvl" or toModify=="l":
                    row.append(tile)
                    frozen_row=tuple(row)
                    level.append(frozen_row)
                    row.clear()
                    tile=""
                    levelSize=0
                    for i in level:
                        for j in i:
                            levelSize+=1
                    if levelSize>=2700:
                        return
                elif toModify=="bonus" or toModify=="bns" or toModify=="b":
                    row.append(tile)
                    frozen_row=tuple(row)
                    bonus.append(frozen_row)
                    row.clear()
                    tile=""
                    levelSize=0
                    for i in bonus:
                        for j in i:
                            levelSize+=1
                    if levelSize>=2700:
                        return
                elif toModify=="layer 1" or toModify=="layer1" or toModify=="l1":
                    row.append(tile)
                    frozen_row=tuple(row)
                    layer_1.append(frozen_row)
                    if int(level_width)!=len(row)*20:
                        level_width=str(len(row)*20)
                    row.clear()
                    tile=""
                elif toModify=="layer 2" or toModify=="layer2" or toModify=="l2":
                    row.append(tile)
                    frozen_row=tuple(row)
                    layer_2.append(frozen_row)
                    if int(level_layer2_width)!=len(row)*20:
                        level_layer2_width=str(len(row)*20)
                    row.clear()
                    tile=""
            else:
                tile+=file_data[i]
        if toModify=="layer 1" or toModify=="layer1" or toModify=="l1":
            if int(level_height)!=len(layer_1)*20:
                level_height=str(len(layer_1)*20)
        elif toModify=="layer 2" or toModify=="layer2" or toModify=="l2":
            if int(level_layer2_height)!=len(layer_2)*20:
                level_layer2_height=str(len(layer_2)*20)
        print(strlib["success"])
    else:
        print(strlib["te_no_level"])
        return

def smfWarpModifier(yPos,xPos,sublevel,xPosTo,yPosTo,playerDir,animation):
    sublevel_names=["Level","Bonus"]
    sublevel_num=2
    for i in range(len(sublevel_names)):
        if sublevel==sublevel_names[i]:
            sublevel_num=i
    dir_names=["right","left"]
    dir_num=2
    for i in range(len(dir_names)):
        if playerDir==dir_names[i]:
            dir_num=i
    anim_names=["Appear","Up","Down","Left","Right"]
    anim_num=5
    for i in range(len(anim_names)):
        if animation==anim_names[i]:
            anim_num=i
    try:
        console=curses.initscr()
    except:
        print(strlib["err_curses_load"])
        return [yPos,xPos,sublevel,xPosTo,yPosTo,playerDir,animation]
    curses.noecho()
    curses.cbreak()
    console.keypad(True)
    console.clear()
    if decorType!=0:
        console.addstr(0,0," Warps ".center(screenx,decorTypes[decorType]))
    else:
        console.addstr(0,0,"Warps")
    console.addstr(1,0,"Position: ◄   ► ◄  ►")
    console.addstr(2,0,"Warp to: ◄    ► ◄   ►")
    console.addstr(3,0,"In sublevel: ")
    console.addstr(4,0,"Facing: ")
    console.addstr(5,0,"Animation: ")
    console.addstr(7,0,f"[{strlib['opt_btn_cancel']}]")
    console.addstr(8,0,f"[{strlib['opt_btn_save']}]")
    current_item=0
    old_data=[yPos,xPos,sublevel,xPosTo,yPosTo,playerDir,animation]
    temp_new=0
    while True:
        console.addstr(1,11,xPos.rjust(3))
        console.addstr(1,17,yPos.rjust(2))
        console.addstr(2,10,xPosTo.rjust(4))
        console.addstr(2,17,yPosTo.rjust(2))
        console.addstr(3,13,"Level Bonus")
        console.addstr(4,8,"right left")
        console.addstr(5,11,"Appear Up Down Left Right")
        console.addstr(7,1,strlib["opt_btn_cancel"])
        console.addstr(8,1,strlib["opt_btn_save"])
        
        if sublevel=="Level":
            console.addstr(3,13,"Level",curses.A_REVERSE)
        elif sublevel=="Bonus":
            console.addstr(3,19,"Bonus",curses.A_REVERSE)
        
        if playerDir=="right":
            console.addstr(4,8,"right",curses.A_REVERSE)
        elif playerDir=="left":
            console.addstr(4,14,"left",curses.A_REVERSE)
        
        if animation=="Appear":
            console.addstr(5,11,"Appear",curses.A_REVERSE)
        elif animation=="Up":
            console.addstr(5,18,"Up",curses.A_REVERSE)
        elif animation=="Down":
            console.addstr(5,21,"Down",curses.A_REVERSE)
        elif animation=="Left":
            console.addstr(5,26,"Left",curses.A_REVERSE)
        elif animation=="Right":
            console.addstr(5,31,"Right",curses.A_REVERSE)
        
        if current_item==0:
            console.addstr(1,11,xPos.rjust(3),curses.A_REVERSE)
        elif current_item==1:
            console.addstr(1,17,yPos.rjust(2),curses.A_REVERSE)
        elif current_item==2:
            console.addstr(2,10,xPosTo.rjust(4),curses.A_REVERSE)
        elif current_item==3:
            console.addstr(2,17,yPosTo.rjust(3),curses.A_REVERSE)
        elif current_item==7:
            console.addstr(7,1,strlib["opt_btn_cancel"],curses.A_REVERSE)
        elif current_item==8:
            console.addstr(8,1,strlib["opt_btn_save"],curses.A_REVERSE)
        console.refresh()
        key=console.getch()
        console.refresh()
        if key==10: # Enter
            if current_item<7:
                current_item=(current_item+1)%9
            else:
                if current_item==7:
                    curses.endwin()
                    print("Exited warp editor.")
                    return old_data
                elif current_item==8:
                    curses.endwin()
                    print("Exited warp editor.")
                    return [yPos,xPos,sublevel,xPosTo,yPosTo,playerDir,animation]
        elif key==curses.KEY_DOWN:
            current_item=(current_item+1)%9
        elif key==curses.KEY_UP:
            current_item=(current_item-1)%9
        elif key==curses.KEY_LEFT:
            if current_item==0:
                if int(xPos)>0:
                    xPos=str(int(xPos)-1)
            elif current_item==1:
                if int(yPos)>0:
                    yPos=str(int(yPos)-1)
            elif current_item==2:
                if int(xPosTo)>0:
                    xPosTo=str(int(xPosTo)-20)
            elif current_item==3:
                if int(yPosTo)>0:
                    yPosTo=str(int(yPosTo)-20)
            elif current_item==4:
                sublevel_num=(sublevel_num-1)%2
                sublevel=sublevel_names[sublevel_num]
            elif current_item==5:
                dir_num=(dir_num-1)%2
                playerDir=dir_names[dir_num]
            elif current_item==6:
                anim_num=(anim_num-1)%5
                animation=anim_names[anim_num]
        elif key==curses.KEY_RIGHT:
            if current_item==0:
                if int(xPos)<225:
                    xPos=str(int(xPos)+1)
            elif current_item==1:
                if int(yPos)<12:
                    yPos=str(int(yPos)+1)
            elif current_item==2:
                if int(xPosTo)<4500:
                    xPosTo=str(int(xPosTo)+20)
            elif current_item==3:
                if int(yPosTo)<240:
                    yPosTo=str(int(yPosTo)+20)
            elif current_item==4:
                sublevel_num=(sublevel_num+1)%2
                sublevel=sublevel_names[sublevel_num]
            elif current_item==5:
                dir_num=(dir_num+1)%2
                playerDir=dir_names[dir_num]
            elif current_item==6:
                anim_num=(anim_num+1)%5
                animation=anim_names[anim_num]

def smf2WarpModifier(mode,xPos,yPos,warpType,extraVar):
    try:
        console=curses.initscr()
    except:
        print(strlib["err_curses_load"])
        return
    curses.noecho()
    curses.cbreak()
    console.keypad(True)
    console.clear()
    if decorType!=0:
        console.addstr(0,0,(" "+mode+" ").center(screenx,decorTypes[decorType]))
    else:
        console.addstr(0,0,mode)
    console.addstr(1,0,"Position: ◄      ► ◄      ►")
    console.addstr(2,0,"Type: ◄  ►")
    if mode=="Entrances":
        console.addstr(3,0,"Player Status: ◄  ►")
    elif mode=="Exits":
        console.addstr(3,0,"Linked to ID # ◄  ►")
    console.addstr(5,0,f"[{strlib['opt_btn_cancel']}]")
    console.addstr(6,0,f"[{strlib['opt_btn_save']}]")
    current_item=0
    old_data=[xPos,yPos,warpType,extraVar]
    temp_new=0
    while True:
        console.addstr(1,11,xPos.rjust(6))
        console.addstr(1,20,yPos.rjust(6))
        console.addstr(2,7,warpType.rjust(2))
        if mode=="Entrances":
            console.addstr(3,16,extraVar.rjust(2))
        else:
            console.addstr(3,16,str(int(extraVar)+1).rjust(2))
        console.addstr(5,1,strlib["opt_btn_cancel"])
        console.addstr(6,1,strlib["opt_btn_save"])
        
        if current_item==0:
            console.addstr(1,11,xPos.rjust(6),curses.A_REVERSE)
        elif current_item==1:
            console.addstr(1,20,yPos.rjust(6),curses.A_REVERSE)
        elif current_item==2:
            console.addstr(2,7,warpType.rjust(2),curses.A_REVERSE)
        elif current_item==3:
            if mode=="Entrances":
                console.addstr(3,16,extraVar.rjust(2),curses.A_REVERSE)
            else:
                console.addstr(3,16,str(int(extraVar)+1).rjust(2),curses.A_REVERSE)
        elif current_item==4:
            console.addstr(5,1,strlib["opt_btn_cancel"],curses.A_REVERSE)
        elif current_item==5:
            console.addstr(6,1,strlib["opt_btn_save"],curses.A_REVERSE)
        console.refresh()
        key=console.getch()
        console.refresh()
        if key==10: # Enter
            if current_item<4:
                current_item=(current_item+1)%6
            else:
                if current_item==4:
                    curses.endwin()
                    print("Exited "+mode.lower()+" editor.")
                    if mode=="Exits":
                        return old_data
                    else:
                        return [old_data[2],old_data[0],old_data[1],old_data[3]]
                elif current_item==5:
                    curses.endwin()
                    print("Exited "+mode.lower()+" editor.")
                    if mode=="Exits":
                        return [xPos,yPos,warpType,extraVar]
                    else:
                        return [warpType,xPos,yPos,extraVar]
        elif key==curses.KEY_DOWN:
            current_item=(current_item+1)%6
        elif key==curses.KEY_UP:
            current_item=(current_item-1)%6
        elif key==curses.KEY_LEFT:
            if current_item==0:
                if mode=="Entrances":
                    if int(xPos)>0:
                        xPos=str(int(xPos)-20)
                else:
                    if int(xPos)>0:
                        xPos=str(int(xPos)-1)
            elif current_item==1:
                if mode=="Entrances":
                    if int(yPos)>0:
                        yPos=str(int(yPos)-20)
                else:
                    if int(yPos)>0:
                        yPos=str(int(yPos)-1)
            elif current_item==2:
                if int(warpType)>0:
                    warpType=str(int(warpType)-1)
            elif current_item==3:
                if int(extraVar)>0:
                    extraVar=str(int(extraVar)-1)
        elif key==curses.KEY_RIGHT:
            if current_item==0:
                if mode=="Entrances":
                    if int(xPos)<999980:
                        xPos=str(int(xPos)+20)
                else:
                    if int(xPos)<49999:
                        xPos=str(int(xPos)+1)
            elif current_item==1:
                if mode=="Entrances":
                    if int(yPos)<999980:
                        yPos=str(int(yPos)+20)
                else:
                    if int(yPos)<49999:
                        yPos=str(int(yPos)+1)
            elif current_item==2:
                if mode=="Entrances":
                    if int(warpType)<10:
                        warpType=str(int(warpType)+1)
                else:
                    if int(warpType)<7:
                        warpType=str(int(warpType)+1)
            elif current_item==3:
                if mode=="Entrances":
                    if int(extraVar)<16:
                        extraVar=str(int(extraVar)+1)
                else:
                    if int(extraVar)<len(all_entrances)-1:
                        extraVar=str(int(extraVar)+1)

def replace(toModify, data):
    toModifySub=""
    
    global game
    
    global level_name
    global level_background
    global level_music
    global start_xpos
    global start_ypos
    global start_at
    global level_width
    global bonus_background
    global bonus_music
    global bonus_width
    global level
    global bonus
    global level_warps
    global bonus_warps
    
    global level_description
    global level_author
    global level_message
    global level_url1
    global level_bg_url2
    global level_powerup
    global level_height
    global level_variable_1
    global level_variable_2
    global level_layer_priority
    global level_layer2_width
    global level_layer2_height
    global level_layer2_xpos
    global level_layer2_ypos
    global level_layer_priority_2
    global level_variable_3
    global all_entrances
    global all_exits
    global layer_1
    global layer_2
    
    if game!="":
        if toModify=="header":
            if data[:5]=="name ":
                toModifySub="name"
                data=data[5:]
            elif data=="name":
                toModifySub="name"
                data=""
            elif data[:2]=="n ":
                toModifySub="name"
                data=data[2:]
            elif data=="n":
                toModifySub="name"
                data=""
            elif data[:12]=="level width ":
                toModifySub="lvlwidth"
                data=data[12:]
            elif data=="level width":
                toModifySub="lvlwidth"
                data=""
            elif data[:9]=="lvlwidth ":
                toModifySub="lvlwidth"
                data=data[9:]
            elif data[:8]=="lvlwidth":
                toModifySub="lvlwidth"
                data=data[8:]
            elif data[:5]=="lvlw ":
                toModifySub="lvlwidth"
                data=data[5:]
            elif data[:4]=="lvlw":
                toModifySub="lvlwidth"
                data=data[4:]
            elif data[:3]=="lw ":
                toModifySub="lvlwidth"
                data=data[3:]
            elif data[:2]=="lw":
                toModifySub="lvlwidth"
                data=data[2:]
            elif data[:17]=="level background ":
                toModifySub="lvlbg"
                data=data[17:]
            elif data=="level background":
                toModifySub="lvlbg"
                data=""
            elif data[:6]=="lvlbg ":
                toModifySub="lvlbg"
                data=data[6:]
            elif data[:5]=="lvlbg":
                toModifySub="lvlbg"
                data=data[5:]
            elif data[:3]=="lb ":
                toModifySub="lvlbg"
                data=data[3:]
            elif data[:2]=="lb":
                toModifySub="lvlbg"
                data=data[2:]
            elif data[:12]=="level music ":
                toModifySub="lvlmus"
                data=data[12:]
            elif data=="level music":
                toModifySub="lvlmus"
                data=""
            elif data[:7]=="lvlmus ":
                toModifySub="lvlmus"
                data=data[6:]
            elif data[:6]=="lvlmus":
                toModifySub="lvlmus"
                data=data[5:]
            elif data[:3]=="lm ":
                toModifySub="lvlmus"
                data=data[3:]
            elif data[:2]=="lm":
                toModifySub="lvlmus"
                data=data[2:]
            elif data[:17]=="bonus background ":
                toModifySub="bnsbg"
                data=data[17:]
            elif data=="bonus background":
                toModifySub="bnsbg"
                data=""
            elif data[:6]=="bnsbg ":
                toModifySub="bnsbg"
                data=data[6:]
            elif data[:5]=="bnsbg":
                toModifySub="bnsbg"
                data=data[5:]
            elif data[:3]=="bb ":
                toModifySub="bnsbg"
                data=data[3:]
            elif data[:2]=="bb":
                toModifySub="bnsbg"
                data=data[2:]
            elif data[:12]=="bonus music ":
                toModifySub="bnsmus"
                data=data[12:]
            elif data=="bonus music":
                toModifySub="bnsmus"
                data=""
            elif data[:7]=="bnsmus ":
                toModifySub="bnsmus"
                data=data[6:]
            elif data[:6]=="bnsmus":
                toModifySub="bnsmus"
                data=data[5:]
            elif data[:3]=="bm ":
                toModifySub="bnsmus"
                data=data[3:]
            elif data[:2]=="bm":
                toModifySub="bnsmus"
                data=data[2:]
            elif data[:8]=="start x ":
                toModifySub="startx"
                data=data[8:]
            elif data[:7]=="start x":
                toModifySub="startx"
                data=data[7:]
            elif data[:7]=="startx ":
                toModifySub="startx"
                data=data[7:]
            elif data[:6]=="startx":
                toModifySub="startx"
                data=data[6:]
            elif data[:3]=="sx ":
                toModifySub="startx"
                data=data[3:]
            elif data[:2]=="sx":
                toModifySub="startx"
                data=data[2:]
            elif data[:8]=="start y ":
                toModifySub="starty"
                data=data[8:]
            elif data[:7]=="start y":
                toModifySub="starty"
                data=data[7:]
            elif data[:7]=="starty ":
                toModifySub="starty"
                data=data[7:]
            elif data[:6]=="starty":
                toModifySub="starty"
                data=data[6:]
            elif data[:3]=="sy ":
                toModifySub="starty"
                data=data[3:]
            elif data[:2]=="sy":
                toModifySub="starty"
                data=data[2:]
            elif data[:15]=="start sublevel ":
                toModifySub="startat"
                data=data[15:]
            elif data=="start sublevel":
                toModifySub="startat"
                data=""
            elif data[:8]=="start at ":
                toModifySub="startat"
                data=data[8:]
            elif data=="start at":
                toModifySub="startat"
                data=""
            elif data[:7]=="startat ":
                toModifySub="startat"
                data=data[7:]
            elif data=="startat":
                toModifySub="startat"
                data=""
            elif data[:3]=="sa ":
                toModifySub="startat"
                data=data[3:]
            elif data[:2]=="sa":
                toModifySub="startat"
                data=""
            elif data[:12]=="description ":
                toModifySub="desc"
                data=data[12:]
            elif data=="description":
                toModifySub="desc"
                data=""
            elif data[:5]=="desc ":
                toModifySub="desc"
                data=data[5:]
            elif data=="desc":
                toModifySub="desc"
                data=""
            elif data[:2]=="d ":
                toModifySub="desc"
                data=data[2:]
            elif data=="d":
                toModifySub="desc"
                data=""
            elif data[:11]=="background ":
                toModifySub="bg"
                data=data[11:]
            elif data[:10]=="background":
                toModifySub="bg"
                data=data[10:]
            elif data[:3]=="bg ":
                toModifySub="bg"
                data=data[3:]
            elif data[:2]=="bg":
                toModifySub="bg"
                data=data[2:]
            elif data[:2]=="b ":
                toModifySub="bg"
                data=data[2:]
            elif data[:1]=="b":
                toModifySub="bg"
                data=data[1:]
            elif data[:6]=="music ":
                toModifySub="mus"
                data=data[6:]
            elif data[:5]=="music":
                toModifySub="mus"
                data=data[5:]
            elif data[:4]=="mus ":
                toModifySub="mus"
                data=data[4:]
            elif data[:3]=="mus":
                toModifySub="mus"
                data=data[3:]
            elif data[:2]=="m ":
                toModifySub="mus"
                data=data[2:]
            elif data[:1]=="m":
                toModifySub="mus"
                data=data[1:]
            elif data[:11]=="startstate ":
                toModifySub="powerup"
                data=data[11:]
            elif data=="startstate":
                toModifySub="powerup"
                data=""
            elif data[:8]=="powerup ":
                toModifySub="powerup"
                data=data[8:]
            elif data=="powerup":
                toModifySub="powerup"
                data=""
            elif data[:2]=="p ":
                toModifySub="powerup"
                data=data[2:]
            elif data[:1]=="p":
                toModifySub="powerup"
                data=data[1:]
            elif data[:5]=="url1 ":
                toModifySub="url1"
                data=data[5:]
            elif data=="url1":
                toModifySub="url1"
                data=""
            elif data[:3]=="u1 ":
                toModifySub="url1"
                data=data[3:]
            elif data=="u1":
                toModifySub="url1"
                data=""
            elif data[:5]=="url2 ":
                toModifySub="url2"
                data=data[5:]
            elif data=="url2":
                toModifySub="url2"
                data=""
            elif data[:3]=="u2 ":
                toModifySub="url2"
                data=data[2:]
            elif data=="u2":
                toModifySub="url2"
                data=""
            elif data[:17]=="layer priority 1 ":
                toModifySub="layerpri1"
                data=data[17:]
            elif data=="layer priority 1":
                toModifySub="layerpri1"
                data=""
            elif data[:7]=="lpri 1 ":
                toModifySub="layerpri1"
                data=data[7:]
            elif data=="lpri 1":
                toModifySub="layerpri1"
                data=""
            elif data[:4]=="lp1 ":
                toModifySub="layerpri1"
                data=data[4:]
            elif data=="lp1":
                toModifySub="layerpri1"
                data=""
            elif data[:17]=="layer priority 2 ":
                toModifySub="layerpri2"
                data=data[17:]
            elif data=="layer priority 2":
                toModifySub="layerpri2"
                data=""
            elif data[:7]=="lpri 2 ":
                toModifySub="layerpri2"
                data=data[7:]
            elif data=="lpri 2":
                toModifySub="layerpri2"
                data=""
            elif data[:4]=="lp2 ":
                toModifySub="layerpri2"
                data=data[4:]
            elif data=="lp2":
                toModifySub="layerpri2"
                data=""
            elif data[:12]=="layer2 xpos ":
                toModifySub="layer2x"
                data=data[12:]
            elif data=="layer2 xpos":
                toModifySub="layer2x"
                data=""
            elif data[:9]=="layer2 x ":
                toModifySub="layer2x"
                data=data[9:]
            elif data=="layer2 x":
                toModifySub="layer2x"
                data=""
            elif data[:4]=="l2x ":
                toModifySub="layer2x"
                data=data[4:]
            elif data=="l2x":
                toModifySub="layer2x"
                data=""
            elif data[:12]=="layer2 ypos ":
                toModifySub="layer2y"
                data=data[12:]
            elif data=="layer2 ypos":
                toModifySub="layer2y"
                data=""
            elif data[:9]=="layer2 y ":
                toModifySub="layer2y"
                data=data[9:]
            elif data=="layer2 y":
                toModifySub="layer2y"
                data=""
            elif data[:4]=="l2y ":
                toModifySub="layer2y"
                data=data[4:]
            elif data=="l2y":
                toModifySub="layer2y"
                data=""
            elif data=="":
                toModifySub=""
            else:
                print(strlib["te_attribute"])
                return
        elif toModify=="warps":
            if data[:6].lower()=="level ":
                sublevel="Level"
                data=data[6:]
            elif data[:5].lower()=="level":
                sublevel="Level"
                data=data[5:]
            elif data[:4]=="lvl ":
                sublevel="Level"
                data=data[4:]
            elif data[:3]=="lvl":
                sublevel="Level"
                data=data[3:]
            elif data[:2]=="l ":
                sublevel="Level"
                data=data[2:]
            elif data[:1]=="l":
                sublevel="Level"
                data=data[1:]
            elif data[:6].lower()=="bonus ":
                sublevel="Bonus"
                data=data[6:]
            elif data[:5].lower()=="bonus":
                sublevel="Bonus"
                data=data[5:]
            elif data[:4]=="bns ":
                sublevel="Bonus"
                data=data[4:]
            elif data[:3]=="bns":
                sublevel="Bonus"
                data=data[3:]
            elif data[:2]=="b ":
                sublevel="Bonus"
                data=data[2:]
            elif data[:1]=="b":
                sublevel="Bonus"
                data=data[1:]
            elif data=="+":
                toModifySub="add"
            else:
                warpNum=""
                for i in data:
                    if i==" " or not i.isnumeric():
                        break
                    else:
                        warpNum+=i
                if warpNum=="":
                    print(colorScheme["typeerror"]+"Please specify a warp number."+colorScheme["default"])
                    return
                data=data[len(warpNum):]
                try:
                    if data[0]==" ":
                        data=data[1:]
                except:
                    pass
                if data=="-" or data=="rem" or data=="remove":
                    toModifySub="remove"
                elif data[:5]=="xpos ":
                    toModifySub="xpos"
                    data=data[5:]
                elif data[:4]=="xpos":
                    toModifySub="xpos"
                    data=data[4:]
                elif data[:2]=="x ":
                    toModifySub="xpos"
                    data=data[2:]
                elif data[:1]=="x":
                    toModifySub="xpos"
                    data=data[1:]
                elif data[:5]=="ypos ":
                    toModifySub="ypos"
                    data=data[5:]
                elif data[:4]=="ypos":
                    toModifySub="ypos"
                    data=data[4:]
                elif data[:2]=="y ":
                    toModifySub="ypos"
                    data=data[2:]
                elif data[:1]=="y":
                    toModifySub="ypos"
                    data=data[1:]
                elif data[:9]=="sublevel ":
                    toModifySub="sublvl"
                    data=data[9:]
                elif data[:8]=="sublevel":
                    toModifySub="sublvl"
                    data=""
                elif data[:7]=="sublvl ":
                    toModifySub="sublvl"
                    data=data[7:]
                elif data[:6]=="sublvl":
                    toModifySub="sublvl"
                    data=""
                elif data[:2]=="s ":
                    toModifySub="sublvl"
                    data=data[2:]
                elif data[:1]=="s":
                    toModifySub="sublvl"
                    data=""
                elif data[:7]=="xposto ":
                    toModifySub="xposto"
                    data=data[7:]
                elif data[:6]=="xposto":
                    toModifySub="xposto"
                    data=data[6:]
                elif data[:3]=="xt ":
                    toModifySub="xposto"
                    data=data[3:]
                elif data[:2]=="xt":
                    toModifySub="xposto"
                    data=data[2:]
                elif data[:7]=="yposto ":
                    toModifySub="yposto"
                    data=data[7:]
                elif data[:6]=="yposto":
                    toModifySub="yposto"
                    data=data[6:]
                elif data[:3]=="yt ":
                    toModifySub="yposto"
                    data=data[3:]
                elif data[:2]=="yt":
                    toModifySub="yposto"
                    data=data[2:]
                elif data[:10]=="direction ":
                    toModifySub="dir"
                    data=data[10:]
                elif data[:9]=="direction":
                    toModifySub="dir"
                    data=""
                elif data[:4]=="dir ":
                    toModifySub="dir"
                    data=data[4:]
                elif data[:3]=="dir":
                    toModifySub="dir"
                    data=""
                elif data[:2]=="d ":
                    toModifySub="dir"
                    data=data[2:]
                elif data[:1]=="d":
                    toModifySub="dir"
                    data=""
                elif data[:10]=="animation ":
                    toModifySub="type"
                    data=data[10:]
                elif data[:9]=="animation":
                    toModifySub="type"
                    data=""
                elif data[:5]=="anim ":
                    toModifySub="type"
                    data=data[5:]
                elif data[:4]=="anim":
                    toModifySub="type"
                    data=""
                elif data[:5]=="type ":
                    toModifySub="type"
                    data=data[5:]
                elif data[:4]=="type":
                    toModifySub="type"
                    data=""
                elif data[:2]=="t ":
                    toModifySub="type"
                    data=data[2:]
                elif data[:1]=="t":
                    toModifySub="type"
                    data=""
                elif data!="":
                    print(strlib["te_attribute"])
                    return
        elif toModify=="entrances" or toModify=="exits":
            if data=="+" or data=="add":
                toModifySub="add"
            elif data[:7]=="insert ":
                toModifySub="insert"
                data=data[7:]
            elif data[:6]=="insert":
                toModifySub="insert"
                data=data[6:]
            elif data[:2]=="i ":
                toModifySub="insert"
                data=data[2:]
            elif data[:1]=="i":
                toModifySub="insert"
                data=data[1:]
            else:
                warpNum=""
                for i in data:
                    if i==" " or not i.isnumeric():
                        break
                    else:
                        warpNum+=i
                if warpNum=="":
                    if toModify=="entrances":
                        print(colorScheme["typeerror"]+"Please specify an entrance ID between 1 and "+str(len(all_entrances))+""+colorScheme["default"])
                    else:
                        print(colorScheme["typeerror"]+"Please specify an exit number between 0 and "+str(len(all_exits)-1)+""+colorScheme["default"])
                    return
                data=data[len(warpNum):]
                try:
                    if data[0]==" ":
                        data=data[1:]
                except:
                    pass
                if data=="-" or data=="rem" or data=="remove":
                    toModifySub="remove"
                elif data[:5]=="swap ":
                    toModifySub="swap"
                    data=data[5:]
                elif data[:4]=="swap":
                    toModifySub="swap"
                    data=data[4:]
                elif data[:2]=="s ":
                    toModifySub="swap"
                    data=data[2:]
                elif data[:1]=="s":
                    toModifySub="swap"
                    data=data[1:]
                elif data[:5]=="xpos ":
                    toModifySub="xpos"
                    data=data[5:]
                elif data[:4]=="xpos":
                    toModifySub="xpos"
                    data=data[4:]
                elif data[:2]=="x ":
                    toModifySub="xpos"
                    data=data[2:]
                elif data[:1]=="x":
                    toModifySub="xpos"
                    data=data[1:]
                elif data[:5]=="ypos ":
                    toModifySub="ypos"
                    data=data[5:]
                elif data[:4]=="ypos":
                    toModifySub="ypos"
                    data=data[4:]
                elif data[:2]=="y ":
                    toModifySub="ypos"
                    data=data[2:]
                elif data[:1]=="y":
                    toModifySub="ypos"
                    data=data[1:]
                elif data[:5]=="type ":
                    toModifySub="type"
                    data=data[5:]
                elif data[:4]=="type":
                    toModifySub="type"
                    data=data[4:]
                elif data[:2]=="t ":
                    toModifySub="type"
                    data=data[2:]
                elif data[:1]=="t":
                    toModifySub="type"
                    data=data[1:]
                elif data[:6]=="state " and toModify=="entrances":
                    toModifySub="state"
                    data=data[6:]
                elif data[:5]=="state" and toModify=="entrances":
                    toModifySub="state"
                    data=""
                elif data[:2]=="s " and toModify=="entrances":
                    toModifySub="state"
                    data=data[2:]
                elif data[:1]=="s" and toModify=="entrances":
                    toModifySub="state"
                    data=""
                elif data[:7]=="linkto " and toModify=="exits":
                    toModifySub="linkto"
                    data=data[7:]
                elif data[:6]=="linkto" and toModify=="exits":
                    toModifySub="linkto"
                    data=""
                elif data[:2]=="l " and toModify=="exits":
                    toModifySub="linkto"
                    data=data[2:]
                elif data[:1]=="l" and toModify=="exits":
                    toModifySub="linkto"
                    data=""
                elif data!="":
                    print(strlib["te_attribute"])
                    return
        elif toModify=="tiles":
            if data[:8]=="layer 1 ":
                sublevel="lay1"
                data=data[8:]
            elif data[:7]=="layer 1":
                sublevel="lay1"
                data=""
            elif data[:7]=="layer1 ":
                sublevel="lay1"
                data=data[7:]
            elif data[:6]=="layer1":
                sublevel="lay1"
                data=""
            elif data[:3]=="l1 ":
                sublevel="lay1"
                data=data[3:]
            elif data[:2]=="l1":
                sublevel="lay1"
                data=""
            elif data[:8]=="layer 2 ":
                sublevel="lay2"
                data=data[8:]
            elif data[:7]=="layer 2":
                sublevel="lay2"
                data=""
            elif data[:7]=="layer2 ":
                sublevel="lay2"
                data=data[7:]
            elif data[:6]=="layer2":
                sublevel="lay2"
                data=""
            elif data[:3]=="l2 ":
                sublevel="lay2"
                data=data[3:]
            elif data[:2]=="l2":
                sublevel="lay2"
                data=""
            elif data[:6].lower()=="level ":
                sublevel="lvl"
                data=data[6:]
            elif data[:5].lower()=="level":
                sublevel="lvl"
                data=data[5:]
            elif data[:4]=="lvl ":
                sublevel="lvl"
                data=data[4:]
            elif data[:3]=="lvl":
                sublevel="lvl"
                data=data[3:]
            elif data[:2]=="l ":
                sublevel="lvl"
                data=data[2:]
            elif data[:1]=="l":
                sublevel="lvl"
                data=data[1:]
            elif data[:6].lower()=="bonus ":
                sublevel="bns"
                data=data[6:]
            elif data[:5].lower()=="bonus":
                sublevel="bns"
                data=data[5:]
            elif data[:4]=="bns ":
                sublevel="bns"
                data=data[4:]
            elif data[:3]=="bns":
                sublevel="bns"
                data=data[3:]
            elif data[:2]=="b ":
                sublevel="bns"
                data=data[2:]
            elif data[:1]=="b":
                sublevel="bns"
                data=data[1:]
            else:
                print(strlib["te_attribute"])
                return
            tileReplacerValues=["","","","",""]
            tileReplacerIndex=0
            for i in data:
                if i==" ":
                    tileReplacerIndex=4
                elif i==":":
                    if tileReplacerIndex==0 or tileReplacerIndex==2:
                        tileReplacerIndex+=1
                elif i==",":
                    if tileReplacerIndex==1 or tileReplacerIndex==3:
                        tileReplacerIndex+=1
                    elif tileReplacerIndex==0 or tileReplacerIndex==2:
                        tileReplacerIndex+=2
                else:
                    tileReplacerValues[tileReplacerIndex]+=i
        
        if game=="smf" or game=="smfe":
            data=data.replace("(","[").replace(")","]")
        elif game=="smf2" or game=="smf2c":
            data=data.replace("&","and")
        
        if toModify=="header":
            if toModifySub=="name":
                if data!="":
                    level_name=data
                else:
                    level_name=input(f"Change level name from «{level_name}» to: ", level_name)
                print("Successfully changed level name!")
            elif toModifySub=="lvlwidth":
                if game=="smf" or game=="smfe":
                    if data!="":
                        level_width=data
                    else:
                        level_width=input(f"Change level width from {level_width} to: ", level_width)
                    try:
                        print(f"Successfully changed level width to {level_width} ({int(level_width)/20} tiles)")
                    except:
                        print(f"Successfully changed level width to {level_width} (not an integer - issues may occur)")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_width"])
            elif toModifySub=="lvlbg":
                if game=="smf" or game=="smfe":
                    if data!="":
                        level_background=data
                    else:
                        level_background=input(f"Change level background from {level_background} to: ", level_background)
                    try:
                        if int(level_background)>6:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print(f"Successfully changed level background to {level_background} ({smfe_background_names[int(level_background)]})")
                    except:
                        print(f"Successfully changed level background to {level_background} ({smfe_background_names[0]})")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_sublvl"])
            elif toModifySub=="lvlmus":
                if game=="smf" or game=="smfe":
                    if data!="":
                        level_music=data
                    else:
                        level_music=input(f"Change level music from {level_music} to: ",level_music)
                    try:
                        if int(level_music)>11:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print(f"Successfully changed level music to {level_music} ({smfe_music_names[int(level_music)]})")
                    except:
                        print(f"Successfully changed level music to {level_music} ({smfe_music_names[0]})")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_sublvl"])
            elif toModifySub=="bnsbg":
                if game=="smf" or game=="smfe":
                    if data!="":
                        bonus_background=data
                    else:
                        bonus_background=input(f"Change bonus background from {bonus_background} to: ", bonus_background)
                    try:
                        if int(bonus_background)>6:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print(f"Successfully changed bonus background to {bonus_background} ({smfe_background_names[int(bonus_background)]})")
                    except:
                        print(f"Successfully changed bonus background to {bonus_background} ({smfe_background_names[0]})")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_sublvl"])
            elif toModifySub=="bnsmus":
                if game=="smf" or game=="smfe":
                    if data!="":
                        bonus_music=data
                    else:
                        bonus_music=input(f"Change bonus music from {bonus_music} to: ", bonus_music)
                    try:
                        if int(bonus_music)>11:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print(f"Successfully changed bonus music to {bonus_music} ({smfe_music_names[int(bonus_music)]})")
                    except:
                        print(f"Successfully changed bonus music to {bonus_music} ({smfe_music_names[0]})")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_sublvl"])
            elif toModifySub=="startx":
                if game=="smf" or game=="smfe":
                    if data!="":
                        start_xpos=data
                    else:
                        start_xpos=input(f"Change start xPos from {start_xpos} to: ", start_xpos)
                    try:
                        print(f"Successfully changed start xPos to {start_xpos} ({int(start_xpos)/20} tiles)")
                    except:
                        print(f"Successfully changed start xPos to {start_xpos} (0 tiles)")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_start"])
            elif toModifySub=="starty":
                if game=="smf" or game=="smfe":
                    if data!="":
                        start_ypos=data
                    else:
                        start_ypos=input(f"Change start yPos from {start_ypos} to: ", start_ypos)
                    try:
                        print(f"Successfully changed start yPos to {start_ypos} ({int(start_ypos)/20} tiles)")
                    except:
                        print(f"Successfully changed start yPos to {start_ypos} (0 tiles)")
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_start"])
            elif toModifySub=="startat":
                if game=="smf" or game=="smfe":
                    if data=="":
                        start_at=input(f"Change start sublevel from {start_at} to: ", start_at)
                    if data.lower()=="level" or data.lower()=="lvl" or data.lower()=="l":
                        start_at="Level"
                    elif data.lower()=="bonus" or data.lower()=="bns" or data.lower()=="b":
                        start_at="Bonus"
                    else:
                        print(strlib["te_rep_sublvl"])
                        return
                    print("Successfully changed start sublevel to "+start_at)
                elif game=="smf2" or game=="smf2c":
                    print(strlib["te_rep_smf2_sublvl"])
            elif toModifySub=="desc":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_description=data
                    else:
                        level_description=input("Change level description to: ", level_description)
                    print("Successfully changed level description!")
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_desc"])
            elif toModifySub=="bg":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_background=data
                    else:
                        level_background==input(f"Change background from {level_background} to: ", level_background)
                    if game=="smf2c":
                        try:
                            print(f"Successfully changed background to {level_background} ({smf2c_background_names[int(level_background)]})")
                        except:
                            print(f"Successfully changed background to {level_background} ({smf2c_background_names[0]})")
                    else:
                        try:
                            if int(level_background)>11:
                                print("Game forced to switch to SMF2 C")
                                game="smf2c"
                                print(f"Successfully changed background to {level_background} ({smf2c_background_names[int(level_background)]})")
                            else:
                                print(f"Successfully changed background to {level_background} ({smf2_background_names[int(level_background)]})")
                        except:
                            print(f"Successfully changed background to {level_background} ({smf2_background_names[0]})")
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_bg"])
            elif toModifySub=="mus":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_music=data
                    else:
                        level_music=input(f"Change music from {level_music} to: ", level_music)
                    if game=="smf2c":
                        try:
                            print(f"Successfully changed music to {level_music} ({smf2c_music_names[int(level_music)]})")
                        except:
                            print(f"Successfully changed music to {level_music} ({smf2c_music_names[0]})")
                    else:
                        try:
                            if int(level_music)==19:
                                print("Game forced to switch to SMF2 C")
                                game="smf2c"
                            print(f"Successfully changed music to {level_music} ({smf2c_music_names[int(level_music)]})")
                        except:
                            print(f"Successfully changed music to {level_music} ({smf2c_music_names[0]})")
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_mus"])
            elif toModifySub=="powerup":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_powerup=data
                    else:
                        level_powerup=input(f"Change start state from {level_powerup} to: ", level_powerup)
                    try:
                        print(f"Successfully changed start state to {level_powerup} ({smf2_powerup_names[int(level_powerup)]})")
                    except:
                        print(f"Successfully changed start state to {level_powerup} ({smf2_powerup_names[29]})")
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_powerup"])
            elif toModifySub=="url1":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_url1=data
                    else:
                        level_url1=input("Change background url 1 to: ", level_url1)
                    print(f"Game forced to switch to background 11 ({smf2_background_names[11]})")
                    level_background=11
                    print("Successfully changed background url 1 to "+level_url1)
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_url"])
            elif toModifySub=="url2":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_bg_url2=data
                    else:
                        level_bg_url2=input("Change background url 2 to: ", level_bg_url2)
                    print(f"Game forced to switch to background 11 ({smf2_background_names[11]})")
                    level_background=11
                    print("Successfully changed background url 2 to "+level_bg_url2)
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_url"])
            elif toModifySub=="layerpri1":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer_priority=data
                    else:
                        level_layer_priority=input(f"Change layer priority 1 from {level_layer_priority} to: ")
                    print("Successfully changed layer priority 1 to "+level_layer_priority)
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_layer"])
            elif toModifySub=="layerpri2":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer_priority_2=data
                    else:
                        level_layer_priority_2=input(f"Change layer priority 2 from {level_layer_priority_2} to: ")
                    print("Successfully changed layer priority 2 to "+level_layer_priority_2)
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_layer"])
            elif toModifySub=="layer2x":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer2_xpos=data
                    else:
                        level_layer2_xpos=input(f"Change layer 2 xPos from {level_layer2_xpos} to: ")
                    print("Successfully changed layer 2 xPos to "+level_layer2_xpos)
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_layer"])
            elif toModifySub=="layer2y":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer2_ypos=data
                    else:
                        level_layer2_ypos=input(f"Change layer 2 yPos from {level_layer2_ypos} to: ")
                    print("Successfully changed layer 2 yPos to "+level_layer2_ypos)
                elif game=="smf" or game=="smfe":
                    print(strlib["te_rep_smf_layer"])
            elif toModifySub=="":
                global decorType
                
                try:
                    console=curses.initscr()
                except:
                    print(strlib["err_curses_load"])
                    return
                curses.noecho()
                curses.cbreak()
                console.keypad(True)
                console.clear()
                if decorType!=0:
                    console.addstr(0,0,f" {strlib['title_r_h']} ".center(screenx,decorTypes[decorType]))
                else:
                    console.addstr(0,0,strlib["title_r_h"])
                if game=="smf":
                    console.addstr(1,0,"Game version: Super Mario Flash")
                elif game=="smfe":
                    console.addstr(1,0,"Game version: Super Mario Flash ver. E")
                elif game=="smf2":
                    console.addstr(1,0,"Game version: Super Mario Flash 2")
                elif game=="smf2c":
                    console.addstr(1,0,"Game version: Super Mario Flash 2 ver. C")
                else:
                    console.addstr(1,0,"Game version: Unknown")
                console.addstr(2,0,"Name: "+level_name[:(screenx-6)])
                if game=="smf" or game=="smfe":
                    console.addstr(3,0,"Level Background: ◄  ►")
                    console.addstr(4,0,"Level Music: ◄  ►")
                    console.addstr(5,0,"Level Width: ◄    ►")
                    console.addstr(6,0,"Bonus Background: ◄  ►")
                    console.addstr(7,0,"Bonus Music: ◄  ►")
                    console.addstr(8,0,"Bonus Width: ◄    ►")
                    console.addstr(10,0,f"[{strlib['opt_btn_cancel']}]")
                    console.addstr(11,0,f"[{strlib['opt_btn_save']}]")
                    current_item=0
                    old_data=[level_background,level_music,level_width,bonus_background,bonus_music,bonus_width]
                    temp_new=0
                    while True:
                        console.addstr(3,19,str(level_background).rjust(2))
                        console.addstr(4,14,str(level_music).rjust(2))
                        console.addstr(5,14,str(level_width).rjust(4))
                        console.addstr(6,19,str(bonus_background).rjust(2))
                        console.addstr(7,14,str(bonus_music).rjust(2))
                        console.addstr(8,14,str(bonus_width).rjust(4))
                        console.addstr(10,1,strlib["opt_btn_cancel"])
                        console.addstr(11,1,strlib["opt_btn_save"])
                        if current_item==0:
                            console.addstr(3,19,str(level_background).rjust(2),curses.A_REVERSE)
                        elif current_item==1:
                            console.addstr(4,14,str(level_music).rjust(2),curses.A_REVERSE)
                        elif current_item==2:
                            console.addstr(5,14,str(level_width).rjust(4),curses.A_REVERSE)
                        if current_item==3:
                            console.addstr(6,19,str(bonus_background).rjust(2),curses.A_REVERSE)
                        elif current_item==4:
                            console.addstr(7,14,str(bonus_music).rjust(2),curses.A_REVERSE)
                        elif current_item==5:
                            console.addstr(8,14,str(bonus_width).rjust(4),curses.A_REVERSE)
                        elif current_item==6:
                            console.addstr(10,1,strlib["opt_btn_cancel"],curses.A_REVERSE)
                        elif current_item==7:
                            console.addstr(11,1,strlib["opt_btn_save"],curses.A_REVERSE)
                        console.refresh()
                        key=console.getch()
                        console.refresh()
                        if key==10: # Enter
                            if current_item<6:
                                current_item=(current_item+1)%8
                                if current_item==6:
                                    level_background,level_music,level_width,bonus_background,bonus_music,bonus_width=old_data
                                curses.endwin()
                                print(strlib["exit_r_h"])
                                return
                        elif key==curses.KEY_DOWN:
                            current_item=(current_item+1)%8
                        elif key==curses.KEY_UP:
                            current_item=(current_item-1)%8
                        elif key==curses.KEY_LEFT:
                            if current_item==0:
                                if int(level_background)>0:
                                    level_background=str(int(level_background)-1)
                            elif current_item==1:
                                if int(level_music)>0:
                                    level_music=str(int(level_music)-1)
                            elif current_item==2:
                                if int(level_width)>0:
                                    level_width=str(int(level_width)-20)
                            elif current_item==3:
                                if int(bonus_background)>0:
                                    bonus_background=str(int(bonus_background)-1)
                            elif current_item==4:
                                if int(bonus_music)>0:
                                    bonus_music=str(int(bonus_music)-1)
                            elif current_item==5:
                                if int(bonus_width)>0:
                                    bonus_width=str(int(bonus_width)-20)
                        elif key==curses.KEY_RIGHT:
                            if current_item==0:
                                if game=="smfe":
                                    if int(level_background)<28:
                                        level_background=str(int(level_background)+1)
                                else:
                                    if int(level_background)<6:
                                        level_background=str(int(level_background)+1)
                            elif current_item==1:
                                if game=="smfe":
                                    if int(level_music)<19:
                                        level_music=str(int(level_music)+1)
                                else:
                                    if int(level_music)<11:
                                        level_music=str(int(level_music)+1)
                            elif current_item==2:
                                if int(level_width)<4500:
                                    level_width=str(int(level_width)+20)
                            elif current_item==3:
                                if game=="smfe":
                                    if int(bonus_background)<28:
                                        bonus_background=str(int(bonus_background)+1)
                                else:
                                    if int(bonus_background)<6:
                                        bonus_background=str(int(bonus_background)+1)
                            elif current_item==4:
                                if game=="smfe":
                                    if int(bonus_music)<19:
                                        bonus_music=str(int(bonus_music)+1)
                                else:
                                    if int(bonus_music)<11:
                                        bonus_music=str(int(bonus_music)+1)
                            elif current_item==5:
                                if int(bonus_width)<4500:
                                    bonus_width=str(int(bonus_width)+20)
                elif game=="smf2" or game=="smf2c":
                    console.addstr(3,0,"Background: ◄   ►")
                    console.addstr(4,0,"Background URL 1: ")
                    console.addstr(5,0,"Background URL 2: ")
                    console.addstr(6,0,"Music: ◄  ►")
                    console.addstr(7,0,"Start Status: ◄  ►")
                    console.addstr(8,0,"Layer Priority 1: ◄ ►")
                    console.addstr(9,0,"Layer Priority 2: ◄ ►")
                    console.addstr(10,0,"Layer 2 Position: X ◄    ► Y ◄    ►")
                    console.addstr(11,0,"Variable 1: ◄ ►")
                    console.addstr(12,0,"Variable 2: ◄ ►")
                    console.addstr(13,0,"Variable 3: ◄ ►")
                    console.addstr(15,0,f"[{strlib['opt_btn_cancel']}]")
                    console.addstr(16,0,f"[{strlib['opt_btn_save']}]")
                    current_item=0
                    old_data=[level_background,level_url1,level_bg_url2,level_music,level_powerup,level_layer_priority,level_layer_priority_2,level_layer2_xpos,level_layer2_ypos,level_variable_1,level_variable_2,level_variable_3]
                    temp_new=0
                    while True:
                        console.addstr(3,13,level_background.rjust(3))
                        console.addstr(4,18,level_url1[:(screenx-18)])
                        console.addstr(5,18,level_bg_url2[:(screenx-18)])
                        console.addstr(6,8,level_music.rjust(2))
                        console.addstr(7,15,level_powerup.rjust(2))
                        console.addstr(8,19,level_layer_priority)
                        console.addstr(9,19,level_layer_priority_2)
                        console.addstr(10,21,level_layer2_xpos.rjust(4))
                        console.addstr(10,30,level_layer2_ypos.rjust(4))
                        console.addstr(11,13,level_variable_1)
                        console.addstr(12,13,level_variable_2)
                        console.addstr(13,13,level_variable_3)
                        console.addstr(15,1,strlib["opt_btn_cancel"])
                        console.addstr(16,1,strlib["opt_btn_save"])
                        if current_item==0:
                            console.addstr(3,13,level_background.rjust(3),curses.A_REVERSE)
                        elif current_item==1:
                            console.addstr(6,8,level_music.rjust(2),curses.A_REVERSE)
                        elif current_item==2:
                            console.addstr(7,15,level_powerup.rjust(2),curses.A_REVERSE)
                        elif current_item==3:
                            console.addstr(8,19,level_layer_priority,curses.A_REVERSE)
                        elif current_item==4:
                            console.addstr(9,19,level_layer_priority_2,curses.A_REVERSE)
                        elif current_item==5:
                            console.addstr(10,21,level_layer2_xpos.rjust(4),curses.A_REVERSE)
                        elif current_item==6:
                            console.addstr(10,30,level_layer2_ypos.rjust(4),curses.A_REVERSE)
                        elif current_item==7:
                            console.addstr(11,13,level_variable_1,curses.A_REVERSE)
                        elif current_item==8:
                            console.addstr(12,13,level_variable_2,curses.A_REVERSE)
                        elif current_item==9:
                            console.addstr(13,13,level_variable_3,curses.A_REVERSE)
                        elif current_item==10:
                            console.addstr(15,1,strlib["opt_btn_cancel"],curses.A_REVERSE)
                        elif current_item==11:
                            console.addstr(16,1,strlib["opt_btn_save"],curses.A_REVERSE)
                        console.refresh()
                        key=console.getch()
                        console.refresh()
                        if key==10: # Enter
                            if current_item<10:
                                current_item=(current_item+1)%12
                            else:
                                if current_item==10:
                                    level_background,level_url1,level_bg_url2,level_music,level_powerup,level_layer_priority,level_layer_priority_2,level_layer2_xpos,level_layer2_ypos,level_variable_1,level_variable_2,level_variable_3=old_data
                                curses.endwin()
                                print(strlib["exit_r_h"])
                                return
                        elif key==curses.KEY_DOWN:
                            current_item=(current_item+1)%12
                        elif key==curses.KEY_UP:
                            current_item=(current_item-1)%12
                        elif key==curses.KEY_LEFT:
                            if current_item==0:
                                if int(level_background)>0:
                                    level_background=str(int(level_background)-1)
                            elif current_item==1:
                                if int(level_music)>0:
                                    level_music=str(int(level_music)-1)
                            elif current_item==2:
                                if int(level_powerup)>0:
                                    level_powerup=str(int(level_powerup)-1)
                            elif current_item==3:
                                if int(level_layer_priority)>0:
                                    level_layer_priority=str(int(level_layer_priority)-1)
                            elif current_item==4:
                                if int(level_layer_priority_2)>0:
                                    level_layer_priority_2=str(int(level_layer_priority_2)-1)
                            elif current_item==5:
                                if int(level_layer2_xpos)>-999:
                                    level_layer2_xpos=str(int(level_layer2_xpos)-1)
                            elif current_item==6:
                                if int(level_layer2_ypos)>-999:
                                    level_layer2_ypos=str(int(level_layer2_ypos)-1)
                            elif current_item==7:
                                if int(level_variable_1)>0:
                                    level_variable_1=str(int(level_variable_1)-1)
                            elif current_item==8:
                                if int(level_variable_2)>0:
                                    level_variable_2=str(int(level_variable_2)-1)
                            elif current_item==9:
                                if int(level_variable_3)>0:
                                    level_variable_3=str(int(level_variable_3)-1)
                        elif key==curses.KEY_RIGHT:
                            if current_item==0:
                                if game=="smf2c":
                                    if int(level_background)<999: ### DETERMINE MAX VALUE ##########################
                                        level_background=str(int(level_background)+1)
                                else:
                                    if int(level_background)<11:
                                        level_background=str(int(level_background)+1)
                            elif current_item==1:
                                if game=="smf2c":
                                    if int(level_music)<19:
                                        level_music=str(int(level_music)+1)
                                else:
                                    if int(level_music)<18:
                                        level_music=str(int(level_music)+1)
                            elif current_item==2:
                                if int(level_powerup)<28:
                                    level_powerup=str(int(level_powerup)+1)
                            elif current_item==3:
                                if int(level_layer_priority)<9:
                                    level_layer_priority=str(int(level_layer_priority)+1)
                            elif current_item==4:
                                if int(level_layer_priority_2)<9:
                                    level_layer_priority_2=str(int(level_layer_priority_2)+1)
                            elif current_item==5:
                                if int(level_layer2_xpos)<999:
                                    level_layer2_xpos=str(int(level_layer2_xpos)+1)
                            elif current_item==6:
                                if int(level_layer2_ypos)<999:
                                    level_layer2_ypos=str(int(level_layer2_ypos)+1)
                            elif current_item==7:
                                if int(level_variable_1)<0:
                                    level_variable_1=str(int(level_variable_1)+1)
                            elif current_item==8:
                                if int(level_variable_2)<0:
                                    level_variable_2=str(int(level_variable_2)+1)
                            elif current_item==9:
                                if int(level_variable_3)<0:
                                    level_variable_3=str(int(level_variable_3)+1)
            else:
                print(strlib["te_attribute"])
        elif toModify=="warps":
            if game=="smf" or game=="smfe":
                if toModifySub=="add":
                    if sublevel=="Level":
                        level_warps.append(tuple(smfWarpModifier("0","0","Level","0","0","right","Appear")))
                    elif sublevel=="Bonus":
                        bonus_warps.append(tuple(smfWarpModifier("0","0","Level","0","0","right","Appear")))
                elif warpNum!="":
                    if sublevel=="Level":
                        if int(warpNum)>len(level_warps)-1:
                            print(colorScheme["typeerror"]+"Warp number too high!"+colorScheme["default"])
                        elif len(level_warps)==0:
                            print(colorScheme["typeerror"]+"No warps exist for this sublevel. Please create a new one."+colorScheme["default"])
                        else:
                            modified=list(level_warps[int(warpNum)])
                            if toModifySub=="remove":
                                level_warps.pop(int(warpNum))
                                print("Removed Warp "+warpNum+".")
                            elif toModifySub=="xpos":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[1]=data
                                    else:
                                        modified[1]=input("Change xPos of warp from "+modified[1]+" to: ")
                                    print("Successfully changed xPos of warp to "+modified[1])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            elif toModifySub=="ypos":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[0]=data
                                    else:
                                        modified[0]=input("Change yPos of warp from "+modified[0]+" to: ")
                                    print("Successfully changed yPos of warp to "+modified[0])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            elif toModifySub=="xposto":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[3]=data
                                    else:
                                        modified[3]=input("Change xPos of warp's exit from "+modified[3]+" to: ")
                                    print("Successfully changed xPos of warp's exit to "+modified[3])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            elif toModifySub=="yposto":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[4]=data
                                    else:
                                        modified[4]=input("Change yPos of warp's exit from "+modified[4]+" to: ")
                                    print("Successfully changed yPos of warp's exit to "+modified[4])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            elif toModifySub=="sublvl":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        if data.lower()=="level" or data.lower()=="lvl" or data.lower()=="l":
                                            modified[2]="Level"
                                        elif data.lower()=="bonus" or data.lower()=="bns" or data.lower()=="b":
                                            modified[2]="Bonus"
                                        else:
                                            modified[2]=data
                                    else:
                                        modified[2]=input("Change sublevel of warp from "+modified[2]+" to: ")
                                    print("Successfully changed sublevel of warp to "+modified[2])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            elif toModifySub=="dir":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[5]=data
                                    else:
                                        modified[5]=input("Change direction of warp from "+modified[5]+" to: ")
                                    print("Successfully changed direction of warp to "+modified[5])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            elif toModifySub=="type":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[6]=data
                                    else:
                                        modified[6]=input("Change animation of warp from "+modified[6]+" to: ")
                                    print("Successfully changed animation of warp to "+modified[6])
                                elif game=="smf2" or game=="smf2c":
                                    print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
                            else:
                                modified=smfWarpModifier(modified[0],modified[1],modified[2],modified[3],modified[4],modified[5],modified[6])
                            level_warps[int(warpNum)]=tuple(modified)
                    elif sublevel=="Bonus":
                        if int(warpNum)>len(bonus_warps)-1:
                            print(colorScheme["typeerror"]+"Warp number too high!"+colorScheme["default"])
                        elif len(bonus_warps)==0:
                            print(colorScheme["typeerror"]+"No warps exist for this sublevel. Please create a new one."+colorScheme["default"])
                        else:
                            modified=list(bonus_warps[int(warpNum)])
                            if game=="smf" or game=="smfe":
                                if toModifySub=="remove":
                                    bonus_warps.pop(int(warpNum))
                                    print("Removed Warp "+warpNum+".")
                                elif toModifySub=="xpos":
                                    if data!="":
                                        modified[1]=data
                                    else:
                                        modified[1]=input("Change xPos of warp from "+modified[1]+" to: ")
                                    print("Successfully changed xPos of warp to "+modified[1])
                                elif toModifySub=="ypos":
                                    if data!="":
                                        modified[0]=data
                                    else:
                                        modified[0]=input("Change yPos of warp from "+modified[0]+" to: ")
                                    print("Successfully changed yPos of warp to "+modified[0])
                                elif toModifySub=="xposto":
                                    if data!="":
                                        modified[3]=data
                                    else:
                                        modified[3]=input("Change xPos of warp's exit from "+modified[3]+" to: ")
                                    print("Successfully changed xPos of warp's exit to "+modified[3])
                                elif toModifySub=="yposto":
                                    if data!="":
                                        modified[4]=data
                                    else:
                                        modified[4]=input("Change yPos of warp's exit from "+modified[4]+" to: ")
                                    print("Successfully changed yPos of warp's exit to "+modified[4])
                                elif toModifySub=="sublvl":
                                    if data!="":
                                        if data.lower()=="level" or data.lower()=="lvl" or data.lower()=="l":
                                            modified[2]="Level"
                                        elif data.lower()=="bonus" or data.lower()=="bns" or data.lower()=="b":
                                            modified[2]="Bonus"
                                        else:
                                            modified[2]=data
                                    else:
                                        modified[2]=input("Change sublevel of warp from "+modified[2]+" to: ")
                                    print("Successfully changed sublevel of warp to "+modified[2])
                                elif toModifySub=="dir":
                                    if data!="":
                                        modified[5]=data
                                    else:
                                        modified[5]=input("Change direction of warp from "+modified[5]+" to: ")
                                    print("Successfully changed direction of warp to "+modified[5])
                                elif toModifySub=="type":
                                    if data!="":
                                        modified[6]=data
                                    else:
                                        modified[6]=input("Change animation of warp from "+modified[6]+" to: ")
                                    print("Successfully changed animation of warp to "+modified[6])
                                else:
                                    modified=smfWarpModifier(modified[0],modified[1],modified[2],modified[3],modified[4],modified[5],modified[6])
                                bonus_warps[int(warpNum)]=tuple(modified)
                else:
                    print(strlib["te_attribute"])
            elif game=="smf2" or game=="smf2c":
                print(colorScheme["typeerror"]+"Warps are an SMF-only property. Please refer to Entrances or Exits."+colorScheme["default"])
        elif toModify=="entrances":
            if game=="smf2" or game=="smf2c":
                if toModifySub=="add":
                    all_entrances.append(tuple(smf2WarpModifier("Entrances","0","0","0","1")))
                elif warpNum!="":
                    if int(warpNum)>len(all_entrances):
                        print(colorScheme["typeerror"]+"Entrance number too high!"+colorScheme["default"])
                    elif len(all_entrances)==0:
                        print(colorScheme["typeerror"]+"No entrances exist for this sublevel. Please create a new one, otherwise the level will be unplayable."+colorScheme["default"])
                    else:
                        modified=list(all_entrances[int(warpNum)-1])
                        if toModifySub=="remove":
                            all_entrances.pop(int(warpNum)-1)
                            print("Removed Entrance "+str(int(warpNum)-1)+".")
                        elif toModifySub=="swap":
                            if data=="":
                                data=input("Swap Entrance ID "+warpNum+" with Entrance ID: ")
                            try:
                                if int(data)>len(all_entrances):
                                    print(colorScheme["typeerror"]+"Entrance number too high!"+colorScheme["default"])
                                else:
                                    modified2=list(all_entrances[int(data)-1])
                                    all_entrances[int(data)-1]=tuple(modified)
                                    modified=modified2
                                    print("Successfully swapped Entrance "+warpNum+" and Entrance "+data)
                            except:
                                print(colorScheme["typeerror"]+"Entrance number not an integer!"+colorScheme["default"])
                        elif toModifySub=="xpos":
                            if data!="":
                                modified[1]=data
                            else:
                                modified[1]=input("Change xPos of entrance from "+modified[1]+" to: ")
                            print("Successfully changed xPos of entrance to "+modified[1])
                        elif toModifySub=="ypos":
                            if data!="":
                                modified[2]=data
                            else:
                                modified[2]=input("Change yPos of entrance from "+modified[2]+" to: ")
                            print("Successfully changed yPos of entrance to "+modified[2])
                        elif toModifySub=="type":
                            if data!="":
                                modified[0]=data
                            else:
                                modified[0]=input("Change type of entrance from "+modified[0]+" to: ")
                            try:
                                print("Successfully changed type of entrance to "+modified[0]+" ("+smf2_entrance_types[modified[0]]+")")
                            except:
                                print("Successfully changed type of entrance to "+modified[0]+" ("+smf2_entrance_types[9]+")")
                        elif toModifySub=="state":
                            if data!="":
                                modified[3]=data
                            else:
                                modified[3]=input("Change entrance state from "+modified[3]+" to: ")
                            try:
                                print("Successfully changed entrance state to "+modified[3]+" ("+smf2_entrance_powerups[modified[3]]+")")
                            except:
                                print("Successfully changed entrance state to "+modified[3]+" ("+smf2_entrance_powerups[17]+")")
                        else:
                            modified=smf2WarpModifier("Entrances",modified[1],modified[2],modified[0],modified[3])
                        all_entrances[int(warpNum)-1]=tuple(modified)
            elif game=="smf" or game=="smfe":
                print(colorScheme["typeerror"]+"Entrances are an SMF2-only property. Please refer to Warps."+colorScheme["default"])
        elif toModify=="exits":
            if game=="smf2" or game=="smf2c":
                if toModifySub=="add":
                    all_exits.append(tuple(smf2WarpModifier("Exits","0","0","1","1")))
                elif warpNum!="":
                    if int(warpNum)>len(all_exits)-1:
                        print(colorScheme["typeerror"]+"Exit number too high!"+colorScheme["default"])
                    elif len(all_exits)==0:
                        print(colorScheme["typeerror"]+"No exits exist for this sublevel. Please create a new one."+colorScheme["default"])
                    else:
                        modified=list(all_exits[int(warpNum)])
                        if toModifySub=="remove":
                            all_exits.pop(int(warpNum))
                            print("Removed Exit "+warpNum+".")
                        elif toModifySub=="xpos":
                            if data!="":
                                modified[0]=data
                            else:
                                modified[0]=input("Change xPos of exit from "+modified[0]+" to: ")
                            print("Successfully changed xPos of exit to "+modified[0])
                        elif toModifySub=="ypos":
                            if data!="":
                                modified[1]=data
                            else:
                                modified[1]=input("Change yPos of exit from "+modified[1]+" to: ")
                            print("Successfully changed yPos of exit to "+modified[1])
                        elif toModifySub=="type":
                            if data!="":
                                modified[2]=data
                            else:
                                modified[2]=input("Change type of exit from "+modified[2]+" to: ")
                            try:
                                print("Successfully changed type of exit to "+modified[2]+" ("+smf2_exit_types[modified[2]]+")")
                            except:
                                print("Successfully changed type of exit to "+modified[2]+" ("+smf2_exit_types[0]+")")
                        elif toModifySub=="linkto":
                            if data!="":
                                modified[3]=data
                            else:
                                modified[3]=input("Change exit's linked entrance from "+modified[3]+" to: ")
                            print("Successfully changed exit's linked entrance to "+modified[3])
                        else:
                            modified=smf2WarpModifier("Exits",modified[0],modified[1],modified[2],modified[3])
                        all_exits[int(warpNum)]=tuple(modified)
            elif game=="smf" or game=="smfe":
                print(colorScheme["typeerror"]+"Exits are an SMF2-only property. Please refer to Warps."+colorScheme["default"])
        elif toModify=="tiles":
            if tileReplacerValues[0]=="" and tileReplacerValues[1]!="":
                print(colorScheme["typeerror"]+"Beginning of X range was not specified."+colorScheme["default"])
                return
            if tileReplacerValues[2]=="" and tileReplacerValues[3]!="":
                print(colorScheme["typeerror"]+"Beginning of Y range was not specified."+colorScheme["default"])
                return
            if tileReplacerValues[0]=="":
                tileReplacerValues[0]=0
                if tileReplacerValues[1]=="":
                    try:
                        if sublevel=="lvl":
                            tileReplacerValues[1]=len(level[0])-1
                        elif sublevel=="bns":
                            tileReplacerValues[1]=len(bonus[0])-1
                        elif sublevel=="lay1":
                            tileReplacerValues[1]=len(layer_1[0])-1
                        elif sublevel=="lay2":
                            tileReplacerValues[1]=len(layer_2[0])-1
                    except:
                        pass
            if tileReplacerValues[2]=="":
                tileReplacerValues[2]=0
                if tileReplacerValues[3]=="":
                    try:
                        if sublevel=="lvl":
                            tileReplacerValues[3]=len(level)-1
                        elif sublevel=="bns":
                            tileReplacerValues[3]=len(bonus)-1
                        elif sublevel=="lay1":
                            tileReplacerValues[3]=len(layer_1)-1
                        elif sublevel=="lay2":
                            tileReplacerValues[3]=len(layer_2)-1
                    except:
                        pass
            if tileReplacerValues[1]=="":
                tileReplacerValues[1]=tileReplacerValues[0]
            if tileReplacerValues[3]=="":
                tileReplacerValues[3]=tileReplacerValues[2]
            try:
                for i in range(len(tileReplacerValues)-1):
                    tileReplacerValues[i]=int(tileReplacerValues[i])
            except:
                print(colorScheme["typeerror"]+"X and Y ranges are not integers."+colorScheme["default"])
                return
            if tileReplacerValues[0]>tileReplacerValues[1]:
                print(colorScheme["typeerror"]+"X range out of order - the beginning of the range should come first."+colorScheme["default"])
                return
            if tileReplacerValues[2]>tileReplacerValues[3]:
                if tileReplacerValues[3]==-1:
                    if game=="smf" or game=="smfe":
                        print(strlib["te_rep_smf2_sublvl"])
                    elif game=="smf2" or game=="smf2c":
                        print(strlib["te_rep_smf_layer"])
                else:
                    print(colorScheme["typeerror"]+"Y range out of order - the beginning of the range should come first."+colorScheme["default"])
                return
            output=""
            length=0
            for loopCount in range(2):
                tilesReplaced=0
                if sublevel=="lvl":
                    if game=="smf" or game=="smfe":
                        for i in range(len(level)):
                            if  i>=tileReplacerValues[2] and i<=tileReplacerValues[3]:
                                modified=list(level[i])
                                for j in range(len(level[i])):
                                    if j>=tileReplacerValues[0] and j<=tileReplacerValues[1]:
                                        if loopCount==0:
                                            if screenx==length+1:
                                                output+="►"
                                                length=0
                                                break
                                            try:
                                                output+=smf_tiles[int(level[i][j])][0]
                                            except:
                                                output+=smf_tiles[0][0]
                                            length+=1
                                        else:
                                            modified[j]=tileReplacerValues[4]
                                            tilesReplaced+=1
                                if i<tileReplacerValues[3]:
                                    if loopCount==0:
                                        output+="\n"
                                        length=0
                                level[i]=tuple(modified)
                    else:
                        print(strlib["te_rep_smf2_sublvl"])
                        return
                elif sublevel=="bns":
                    if game=="smf" or game=="smfe":
                        for i in range(len(bonus)):
                            if  i>=tileReplacerValues[2] and i<=tileReplacerValues[3]:
                                modified=list(bonus[i])
                                for j in range(len(bonus[i])):
                                    if j>=tileReplacerValues[0] and j<=tileReplacerValues[1]:
                                        if loopCount==0:
                                            if screenx==length+1:
                                                output+="►"
                                                length=0
                                                break
                                            try:
                                                output+=smf_tiles[int(bonus[i][j])][0]
                                            except:
                                                output+=smf_tiles[0][0]
                                            length+=1
                                        else:
                                            modified[j]=tileReplacerValues[4]
                                            tilesReplaced+=1
                                if i<tileReplacerValues[3]:
                                    if loopCount==0:
                                        output+="\n"
                                        length=0
                                bonus[i]=tuple(modified)
                    else:
                        print(strlib["te_rep_smf2_sublvl"])
                        return
                elif sublevel=="lay1":
                    if game=="smf2" or game=="smf2c":
                        for i in range(len(layer_1)):
                            if  i>=tileReplacerValues[2] and i<=tileReplacerValues[3]:
                                modified=list(layer_1[i])
                                for j in range(len(layer_1[i])):
                                    if j>=tileReplacerValues[0] and j<=tileReplacerValues[1]:
                                        if loopCount==0:
                                            if screenx==length+1:
                                                output+="►"
                                                length=0
                                                break
                                            try:
                                                output+=smf2_tiles[int(layer_1[i][j])][0]
                                            except:
                                                output+=smf2_tiles[0][0]
                                            length+=1
                                        else:
                                            modified[j]=tileReplacerValues[4]
                                            tilesReplaced+=1
                                if i<tileReplacerValues[3]:
                                    if loopCount==0:
                                        output+="\n"
                                        length=0
                                layer_1[i]=tuple(modified)
                    else:
                        print(strlib["te_rep_smf_layer"])
                        return
                elif sublevel=="lay2":
                    if game=="smf2" or game=="smf2c":
                        for i in range(len(layer_2)):
                            if  i>=tileReplacerValues[2] and i<=tileReplacerValues[3]:
                                modified=list(layer_2[i])
                                for j in range(len(layer_2[i])):
                                    if j>=tileReplacerValues[0] and j<=tileReplacerValues[1]:
                                        if loopCount==0:
                                            if screenx==length+1:
                                                output+="►"
                                                length=0
                                                break
                                            try:
                                                output+=smf2_tiles[int(layer_2[i][j])][0]
                                            except:
                                                output+=smf2_tiles[0][0]
                                            length+=1
                                        else:
                                            modified[j]=tileReplacerValues[4]
                                            tilesReplaced+=1
                                if i<tileReplacerValues[3]:
                                    if loopCount==0:
                                        output+="\n"
                                        length=0
                                layer_2[i]=tuple(modified)
                    else:
                        print(strlib["te_rep_smf_layer"])
                        return
                if loopCount==0:
                    print(output)
                    if tileReplacerValues[4]=="":
                        tileReplacerValues[4]=input("Replace this selection with tile ID: ")
                else:
                    try:
                        if game=="smf" or game=="smfe":
                            print("Replaced "+str(tilesReplaced)+" tiles with tile ID "+tileReplacerValues[4]+" ("+smf_tiles[int(tileReplacerValues[4])][1]+")")
                        else:
                            print("Replaced "+str(tilesReplaced)+" tiles with tile ID "+tileReplacerValues[4]+" ("+smf2_tiles[int(tileReplacerValues[4])][1]+")")
                    except:
                        print("Replaced "+str(tilesReplaced)+" tiles with tile ID "+tileReplacerValues[4]+" ("+smf_tiles[0][1]+")")
        return
    else:
        print(strlib["te_no_level"])
        return

def awaitInput():
    global current_command
    global usedCommands

    while True:
        command=input("→ ", "")
        
        usedCommands.append(command)
        if len(usedCommands)>10: ### MAKE THIS NUMBER MODIFIABLE VIA SETTINGS ###
            usedCommands.pop(0)
        current_command=len(usedCommands)
        
        if not testInputMatch(command, True)[0] or not testInputMatch(command, False)[3]:
            if not testInputMatch(command, False)[0]:
                print(strlib["te_comm"])
            elif testInputMatch(command, False)[2] and not testInputMatch(command, False)[3]:
                print(strlib["te_attribute"])

configLoad()
try:
    colorscheme.defineColors()
except:
    colorschemeMissing=True
clear()
if decorType!=0:
    title=" SMF Level Reader v"+versionNames[programVersion]+" "
    length=len(title)
    padding=(screenx-length)//2
    centered_text=decorTypes[decorType]*padding+colorScheme["bold"]+title+colorScheme["default"]+decorTypes[decorType]*padding
    print(centered_text)
else:
    print(colorScheme["bold"]+"SMF Level Reader v"+versionNames[programVersion]+colorScheme["default"])
if colorschemeMissing:
    print(strlib["err_color_load"])
print(strlib["greet_info"])
if firstRun:
    print(strlib["greet_intro"])

if not win32gui_imported:
    print(strlib["err_mod_win32gui"]+"\n")
if not curses_imported:
    print(strlib["err_mod_curses"]+"\n")
if not keyboard_imported:
    print(strlib["err_mod_keyboard"]+"\n")

time.sleep(titleScreenWaitTime/1000*16)
print(strlib["greet_ask"])
usedCommands=[]
current_command=0
current_window=checkForeground() # fix for Windows Powershell
awaitInput()