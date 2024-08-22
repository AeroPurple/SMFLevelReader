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
from sys import exit
try:
    import curses
except:
    print("\033[31mNo Curses module installed.\033[0m\nPlease install it using the \033[1mpip install curses\033[0m command.")

titleScreenWaitTime=0
decorType=0

try:
    screenx,screeny=shutil.get_terminal_size()
except:
    screenx=80
    screeny=25
    
    try:
        console=curses.initscr()
        console.clear()
        console.addstr(0,0,"".center(screenx,"─"))
        console.addstr(screeny-1,0,"".center(screenx,"─"))
        for i in range (screeny-2):
            console.addstr(i+1,0,"│")
        for i in range (screeny-2):
            console.addstr(i+1,screenx-1,"│")
        console.addstr(0,0,"┌")
        console.addstr(0,screenx-1,"┐")
        console.addstr(screeny-1,0,"└")
        console.addstr(screeny-1,screenx-1,"┘")
        console.addstr(2,2,"Console size was not detected.")
        console.addstr(4,2,"A default size of 80x25 will be used, as represented by this box.")
        console.addstr(6,2,"Please resize your console so that this box fits neatly in it.")
        console.addstr(8,2,"Press any key when you're ready.")
        console.refresh()
        console.getch()
        curses.endwin()
    except:
        print("\033[31mCurrent console environment does not support Curses.\nAlong with this, the console size was not detected and was set to the default 80x25 size.\033[0m")

versionNames=[0,"0.9"]
configVersion=0
programVersion=1

decorTypes=[" ","─","━","═"]

def convertToConfigData(versionIndex,waitTime,decorType):
    return (versionIndex<<8|waitTime)<<2|decorType
    
def configSave(versionIndex,waitTime,decorType):
    configData=convertToConfigData(versionIndex,waitTime,decorType)
    configData=configData.to_bytes(2,'big')
    configFile=open(os.path.join(sys.path[0], 'Settings.cfg'),mode='wb')
    configFile.write(configData)
    configFile.close()

def configLoad():
    global configVersion
    global titleScreenWaitTime
    global decorType
    
    try:
        configFile=open(os.path.join(sys.path[0], 'Settings.cfg'),mode='rb')
    except:
        configSave(programVersion,62,2)
        configFile=open(os.path.join(sys.path[0], 'Settings.cfg'),mode='rb')
    finally:
        try:
            configData=configFile.read()
            configData=bin(int.from_bytes(configData,'big'))[2:].zfill(16)
            configVersion=int(configData[:6],2)
            if configVersion+1>len(versionNames) or versionNames[configVersion]==0:
                print("Configuration file may be invalid.")
            titleScreenWaitTime=int(configData[6:14],2)
            decorType=int(configData[14:16],2)
            configFile.close()
        except:
            configSave(programVersion,62,2)
        
def changeConfig():
    global titleScreenWaitTime
    global decorType
    
    try:
        console=curses.initscr()
    except:
        print("\033[31mCurrent console environment does not support Curses.\033[0m")
        return
    console.keypad(True)
    console.clear()
    if decorType!=0:
        console.addstr(0,0," Settings ".center(screenx,decorTypes[decorType]))
    else:
        console.addstr(0,0,"Settings")
    if versionNames[configVersion]==0:
        console.addstr(1,0,"Reported config version: Invalid")
    elif configVersion+1>len(versionNames):
        console.addstr(1,0,"Reported config version: Unknown")
    else:
        console.addstr(1,0,"Reported config version: "+versionNames[configVersion])
    console.addstr(2,0,"Title screen halt (ms): ◄    ►")
    console.addstr(3,0,"Title padding style: ◄    ►")
    console.addstr(5,0,"[Reset All]")
    console.addstr(6,0,"[Cancel]")
    console.addstr(7,0,"[Save]")
    current_item=0
    old_data=[titleScreenWaitTime,decorType]
    temp_new=0
    while True:
        console.addstr(2,25,str(titleScreenWaitTime*16).rjust(4))
        if decorType==0:
            console.addstr(3,22,"None")
        else:
            console.addstr(3,22,"".center(4,decorTypes[decorType]))
        console.addstr(5,1,"Reset All")
        console.addstr(6,1,"Cancel")
        console.addstr(7,1,"Save")
        if current_item==0:
            console.addstr(2,25,str(titleScreenWaitTime*16).rjust(4),curses.A_REVERSE)
        elif current_item==1:
            if decorType==0:
                console.addstr(3,22,"None",curses.A_REVERSE)
            else:
                console.addstr(3,22,"".center(4,decorTypes[decorType]),curses.A_REVERSE)
        elif current_item==2:
            console.addstr(5,1,"Reset All",curses.A_REVERSE)
        elif current_item==3:
            console.addstr(6,1,"Cancel",curses.A_REVERSE)
        elif current_item==4:
            console.addstr(7,1,"Save",curses.A_REVERSE)
        console.refresh()
        key=console.getch()
        #console.addstr(11,0,str(key)+"   ")
        console.refresh()
        if key==10: # Enter
            if current_item<2:
                current_item=(current_item+1)%5
            else:
                if current_item==2:
                    titleScreenWaitTime,decorType=[62,2]
                    configSave(programVersion,titleScreenWaitTime,decorType)
                elif current_item==3:
                    titleScreenWaitTime,decorType=old_data
                elif current_item==4:
                    configSave(programVersion,titleScreenWaitTime,decorType)
                curses.endwin()
                print("Exited settings page.")
                return
        elif key==curses.KEY_DOWN:
            current_item=(current_item+1)%5
        elif key==curses.KEY_UP:
            current_item=(current_item-1)%5
        elif key==curses.KEY_LEFT:
            if current_item==0:
                if titleScreenWaitTime>0:
                    titleScreenWaitTime-=1
            elif current_item==1:
                if decorType>0:
                    decorType-=1
        elif key==curses.KEY_RIGHT:
            if current_item==0:
                if titleScreenWaitTime<255:
                    titleScreenWaitTime+=1
            elif current_item==1:
                if decorType<3:
                    decorType+=1

def generalHelp(command):
    if command=="":
        print("\033[1mSMF Level Reader v"+versionNames[programVersion]+"\nReleased on 22 Aug 2024 by AeroPurple\033[0m\n")
        print("Available commands:\n\u001b[33mopen | o\nexport | exp | e\nimport | imp | i\nsettings | set | s\nreplace | rep | r\nheader | head | h\nhelp | ?\nexit | x\033[0m")
    elif command[:4]=="open" or command[:1]=="o":
        print("\033[1mOpen Command\033[0m")
        print("This command opens up a File Explorer dialogue and allows you to select a file. This file is then automatically parsed and can be edited.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mopen\033[0m")
        print("\u001b[33mo\033[0m")
    elif command[:6]=="export" or command[:3]=="exp" or command[:1]=="e":
        print("\033[1mExport Command\033[0m")
        print("This command exports an opened Super Mario Flash level to your desired format, such as Comma Separated Values (can be edited in Excel), the original SMF text format, or an experimental text format that contains a visual representation of level tiles.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mexport\033[0m \033[1m[format]\033[0m")
        print("\u001b[33mexp\033[0m \033[1m[format]\033[0m")
        print("\u001b[33me\033[0m \033[1m[format]\033[0m")
        print("\n\033[1mAccepted Values\033[0m")
        print("csv | txt | map")
    elif command[:6]=="import" or command[:3]=="imp" or command[:1]=="i":
        print("\033[1mImport Command\033[0m")
        print("This command replaces specified tiles with a Comma Seperated Values (CSV) file.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mimport\033[0m \033[1m[type of tile data]\033[0m")
        print("\u001b[33mimp\033[0m \033[1m[type of tile data]\033[0m")
        print("\u001b[33mi\033[0m \033[1m[type of tile data]\033[0m")
        print("\n\033[1mAccepted Values\033[0m")
        print("level | lvl | l\nbonus | bns | b\nlayer 1 | layer1 | l1\nlayer 2 | layer2 | l2")
    elif command[:6]=="settings" or command[:3]=="set" or command[:1]=="s":
        print("\033[1mSettings Command\033[0m")
        print("This command opens a Curses interface that allows you to customize how the program functions and looks.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33msettings\033[0m")
        print("\u001b[33mset\033[0m")
        print("\u001b[33ms\033[0m")
    elif command[:7]=="replace" or command[:3]=="rep" or command[:1]=="r":
        print("\033[1mReplace Command\033[0m")
        print("This command replaces various variables in the current level.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mreplace\033[0m \033[1mheader [variable or command] [new value]\033[0m")
        print("\u001b[33mreplace\033[0m \033[1mwarp/entrance/exit [warp sublevel and number or command] [variable or command] [new value]\033[0m")
        print("\u001b[33mreplace\033[0m \033[1mtiles [type of tile data] [tile selection] [new value]\033[0m")
        print("\u001b[33mrep\033[0m \033[1mheader [variable or command]  [new value]\033[0m")
        print("\u001b[33mrep\033[0m \033[1mwarp/entrance/exit [warp sublevel and number or command] [variable or command] [new value]\033[0m")
        print("\u001b[33mrep\033[0m \033[1mtiles [type of tile data] [tile selection] [new value]\033[0m")
        print("\u001b[33mr\033[0m \033[1mheader [variable or command]  [new value]\033[0m")
        print("\u001b[33mr\033[0m \033[1mwarp/entrance/exit [warp sublevel and number or command] [variable or command] [new value]\033[0m")
        print("\u001b[33mr\033[0m \033[1mtiles [type of tile data] [tile selection] [new value]\033[0m")
        time.sleep(1)
        print("\n\033[1mAccepted Values\033[0m")
        print("Data Groups:")
        print("\theader | head | h\n\twarp | w\n\tentance | entr | n\n\texit | x\n\ttiles | t")
        time.sleep(1)
        print("\n\033[1mCommands/Variables\033[0m")
        print("Header:\n\tname | n\n\tlevel width | lvlwidth | lvlw | lw\n\tlevel background | lvlbg | lb\n\tlevel music | lvlmus | lm\n\tbonus background | bnsbg | bb\n\tbonus music | bnsmus | bm\n\tstart x | startx | sx\n\tstart y | starty | sy\n\tstart sublevel | start at | startat | sa\n\tdescription | desc | d\n\tbackground | bg | b\n\tmusic | mus |m\n\tstartstate | powerup | p\n\turl1 | u1\n\turl2 | u2\n\tlayer priority 1 | lpri 1 | lp1\n\tlayer priority 2 | lpri 2 | lp2\n\tlayer2 xpos | layer2 x | l2x\n\tlayer2 ypos | layer2 y | l2y")
        time.sleep(1)
        print("Warps:\n\tadd | +\n\tremove | rem | -\n\txpos | x\n\typos | y\n\tsublevel | sublvl | s\n\txposto | xt\n\typosto | yt\n\tdirection | dir | d\n\tanimation | anim | type | t")
        time.sleep(1)
        print("Entrances/Exits:\n\tadd | +\n\tremove | rem | -\n\tswap | s\n\txpos | x\n\typos | y\n\ttype | t\n\tstate | s\n\tlinkto | l")
        time.sleep(1)
        print("Tile Ranges:\n\tThe colon signifies a range. As in, 90:100 would select 10 columns/rows.\n\tThe comma separates the X range/columns from the Y range/rows.\n\tThe space separates the tile selection from the specified replacement value.\n\tSome examples:\n\t'4:5,8:9 100' selects tiles from x4y8 to x5y9 and replaces them with tile ID 100.\n\t'4:5,8' selects tiles 4 through 5 in the 8th column.\n\t'4,8' selects tile in position x4y8.")
        time.sleep(1)
        print("\n\033[1mExamples\033[0m")
        print("replace header name Hi! -- this will replace the current level name with \"Hi!\".")
        print("replace header music 5 -- this will replace the current level music with Underwater.")
        print("replace warp level add -- this will add a new warp to the list of level warps.")
        print("replace warp level 2 remove -- this will remove warp no.3 from the list of level warps.")
        print("replace warp bonus 3 xpos -- this will changes bonus warp no.4's X position.")
        print("replace entrance 5 swap 6 -- this will swap entrances ID 5 and ID 6.")
        print("replace tiles layer1 0:10,0:10 241 -- this will replace a 10x10 square in the upper left corner of the level with coins.")
        print("\nIf no value is specified, like in 'replace header name', you will be prompted to assign a value.")
        print("If no variable is specified, like in 'replace header', a Curses user interface containing all of the variables for that data group will appear.")
    elif command[:6]=="header" or command[:4]=="head" or command[:1]=="h":
        print("\033[1mHeader Command\033[0m")
        print("This command will print formatted header data, similar to what happens when you open a file.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mheader\033[0m")
        print("\u001b[33mhead\033[0m")
        print("\u001b[33mh\033[0m")
    elif command[:4]=="help" or command[:1]=="?":
        print("\033[1mHelp Command\033[0m")
        print("This command prints useful info on how to use this program.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mhelp\033[0m \033[1m[command]\033[0m")
        print("\u001b[33m?\033[0m \033[1m[command]\033[0m")
    elif command[:4]=="exit" or command[:1]=="x":
        print("\033[1mExit Command\033[0m")
        print("This command exits this program.")
        print("\n\033[1mSyntax\033[0m")
        print("\u001b[33mexit\033[0m")
        print("\u001b[33mx\033[0m")

smfe_background_names=[
    "\x1B[3mNone\x1B[0m",
    "Land",
    "Cave",
    "Forest",
    "Castle",
    "Snow",
    "Ghost", # 6 - SMF Limit #
    "Hills",
    "Snow 2",
    "Rock",
    "Castle 2",
    "Ghost 2",
    "Cave 2",
    "Autumn",
    "Night",
    "Dark",
    "Night 2",
    "Land 2",
    "Waterfall",
    "Ruins",
    "Sky",
    "Mountain",
    "Snow 3",
    "Castle Walls",
    "Castle 3",
    "Castle 4",
    "Desert",
    "Volcano",
    "Volcanic Cave"
]

smfe_music_names=[
    "\x1B[3mNone\x1B[0m",
    "Overworld",
    "Forest",
    "Athletic",
    "Map",
    "Underground",
    "Fortress",
    "Bowser",
    "Toad Shop/Level Builder",
    "Invincibile",
    "Level Complete",
    "World Complete", # 11 - SMF Limit #
    "Castle","Bonus",
    "Final Bowser",
    "Ghost House (SMW)",
    "Ghost House (SMB)",
    "Volcano",
    "Airship",
    "Desert"
]

smf2_background_names=[
    "\x1B[3mNone\x1B[0m",
    "Clouds",
    "Hills",
    "Forest",
    "Ghost House",
    "Underground",
    "Underwater",
    "Castle",
    "Bonus",
    "Night",
    "\x1B[3mNone\x1B[0m",
    "\x1B[3mCustom\x1B[0m"
]

smf2c_background_names=[
    "\x1B[3mNone\x1B[0m",
    "Clouds (Color 2)",
    "Hills (Colors 1/1)",
    "Forest (Color 3)",
    "Ghost House (Color 1)",
    "Underground",
    "Underwater (Color 1)",
    "Castle (Color 1)",
    "Bonus (Color 1)",
    "Night (Color 1)",
    "\x1B[3mNone\x1B[0m",
    "\x1B[3mCustom\x1B[0m",
    "Tall Hills (Color 4)",
    "Mountains (Colors 2/3)",
    "Forest (Color 4)",
    "Candle Castle (Color 1)",
    "Small Hills (Colors 1/5)",
    "Tall Mountains (Colors 3/1)",
    "Solid (Color 6)",
    "Clouds (Color 1)",
    "Clouds (Color 3)",
    "Clouds (Color 4)",
    "Clouds (Color 5)",
    "Hills (Colors 1/2)",
    "Hills (Colors 1/3)",
    "Hills (Colors 1/4)",
    "Hills (Colors 1/5)",
    "Hills (Colors 2/1)",
    "Hills (Colors 2/2)",
    "Hills (Colors 2/3)",
    "Hills (Colors 2/4)",
    "Hills (Colors 2/5)",
    "Hills (Colors 3/1)",
    "Hills (Colors 3/2)",
    "Hills (Colors 3/3)",
    "Hills (Colors 3/4)",
    "Hills (Colors 3/5)",
    "Hills (Colors 4/1)",
    "Hills (Colors 4/2)",
    "Hills (Colors 4/3)",
    "Hills (Colors 4/4)",
    "Hills (Colors 4/5)",
    "42" ########### Incomplete !!! ###########
]

smf2c_music_names=[
    "\x1B[3mNone\x1B[0m",
    "Overworld",
    "Athletic",
    "Castle",
    "Underground",
    "Underwater",
    "Ghost House",
    "Airship",
    "Bonus",
    "Bowser",
    "Invincibile",
    "P-Switch",
    "Minor Fanfare",
    "Major Fanfare",
    "Player Down",
    "Boom Boom",
    "Plains Map",
    "Underworld Map",
    "Key Exit",
    "\x1B[3mCustom\x1B[0m"
]

smf2_powerup_names=[
    "Small Mario",
    "Big Mario",
    "Fire Mario",
    "Cape Mario",
    "Frictionless Cape Mario (unintended)",
    "Yoshi-Riding Small Mario (unintended, \033[33munstable\033[0m)",
    "Yoshi-Riding Big Mario (unintended, \033[33munstable\033[0m)",
    "Yoshi-Riding Fire Mario (unintended, \033[33munstable\033[0m)",
    "Yoshi-Riding Cape Mario (unintended, \033[33munstable\033[0m)",
    "Door-Entering Mario (unintended, \033[31mcrashes the game\033[0m)",
    "Vine-Climbing Small Mario (unintended)",
    "Vine-Climbing Big Mario (unintended)",
    "Vine-Climbing Fire Mario (unintended)",
    "Vine-Climbing Cape Mario (unintended)",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "Carrying Small Mario (unintended)",
    "Carrying Big Mario (unintended)",
    "Carrying Fire Mario (unintended)",
    "Carrying Cape Mario (unintended)",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "\x1B[3mNo Mario (unintended)\x1B[0m",
    "Swimming Small Mario",
    "Swimming Big Mario",
    "Swimming Fire Mario",
    "Swimming Cape Mario",
    "\x1B[3mNo Mario (unintended)\x1B[0m"
]

smf2_entrance_types=[
    "Standard Entrance",
    "Repeating Door Animation (unintended, \033[33msoftlocks the game\033[0m)",
    "Upward Pipe Entrance",
    "Downward Pipe Entrance",
    "Repeating Downward Pipe Animation (unintended, \033[33msoftlocks the game\033[0m)",
    "Repeating Upward Pipe Animation (unintended, \033[33msoftlocks the game\033[0m)",
    "Pipe Entrance Right","Pipe Entrance Left",
    "Repeating Pipe Left Animation (unintended, \033[33msoftlocks the game\033[0m)",
    "Repeating Pipe Right Animation (unintended, \033[33msoftlocks the game\033[0m)",
    "No Mario (unintended, \033[33msoftlocks the game\033[0m)"
]

smf2_entrance_powerups=[
    "No Mario (unintended, \033[33munstable\033[0m)",
    "Facing Right",
    "Facing Left",
    "Running Right (unintended)",
    "Running Left (unintended)",
    "Skidding Right (unintended)",
    "Skidding Left (unintended)",
    "Jumping Right (unintended)",
    "Jumping Left (unintended)",
    "Falling Right (unintended)",
    "Falling Left (unintended)",
    "Crouching Right (unintended)",
    "Crouching Left (unintended)",
    "Sliding Right (unintended)",
    "Sliding Left (unintended)",
    "Kicking Right (unintended)",
    "Kicking Left (unintended)",
    "Superposition Mario (unintended)"
]

smf2_exit_types=[
    "\x1B[3mNone\x1B[0m",
    "Door",
    "P-Switch Door",
    "Downward Pipe",
    "Upward Pipe",
    "Pipe Right",
    "Pipe Left"
]

smf_tiles=[
    ["·","Empty"],
    ["█","Land Top Center"],
    ["█","Brown Block"],
    ["█","Blue Block"],
    ["█","Forest Top Center"],
    ["█","Forest Center"],
    ["█","Invisible"],
    ["█","Empty Brown ?"],
    ["█","Spin"],
    ["█","Bowser Bridge"],
    ["█","Cave Top Center"],
    ["█","Brown Brick"],
    ["█","Blue Brick"],
    ["█","Castle Top Center"],
    ["█","Castle Center"],
    ["█","Invisible"],
    ["█","Grass Platform Center"],
    ["█","Grass Platform Left"],
    ["█","Grass Platform Right"],
    ["▒","Grass Platform Stem Single"],
    ["▒","Grass Platform Stem Left"],
    ["▒","Grass Platform Stem Center"],
    ["▒","Grass Platform Stem Right"],
    ["█","Green Pipe Vert Top Left"],
    ["█","Green Pipe Vert Top Right"],
    ["█","Green Pipe Vert Stem Left"],
    ["█","Green Pipe Vert Stem Right"],
    ["█","Stone Brick Single"],
    ["█","Stone Brick Right"],
    ["█","Stone Brick Left"],
    ["█","Castle Right"],
    ["█","Castle Left"],
    ["█","Castle Top Left"],
    ["█","Castle Top Right"],
    ["█","Castle Left and Up Join"],
    ["█","Castle Right and Up Join"],
    ["█","Snow Top Center"],
    ["█","Grey Pipe Vert Top Left"],
    ["█","Grey Pipe Vert Top Right"],
    ["█","Grey Pipe Vert Stem Left"],
    ["█","Grey Pipe Vert Stem Right"],
    ["█","Forest Right and Up Join"],
    ["█","Forest Right"],
    ["█","Forest Top Right"],
    ["█","Forest Top Left"],
    ["█","Forest Left and Up Join"],
    ["█","Forest Left"],
    ["█","Star ?"],
    ["█","Powerup ?"],
    ["█","Coin ?"],
    ["≈","Lava"],
    ["=","Up Platform"],
    ["=","Down Platform"],
    ["=","Side 2 Platform"],
    ["=","Side 1 Platform"],
    ["=","Fall Platform"],
    ["0","Coin"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["×","Brown Goomba"],
    ["×","Blue Goomba"],
    ["×","Podoboo"],
    ["█","Bullet Bill Launcher Left"],
    ["×","Spiny"],
    ["×","Green Koopa Walking"],
    ["×","Hammer Bro"],
    ["×","Green Koopa Jumping"],
    ["█","Firebar"],
    ["×","Moving Piranha"],
    ["×","Lakitu"],
    ["×","Standing Piranha"],
    ["×","Green Koopa Flying"],
    ["█","Bullet Bill Launcher Right"],
    ["×","Red Koopa Walking"],
    ["×","Red Koopa Jumping"],
    ["×","Red Koopa Flying"],
    ["×","Buzzy Beetle"],
    ["×","Bowser"],
    ["×","Bullet Bill Left"],
    ["×","Bullet Bill Right"],
    ["×","Bowser Flame Right"],
    ["×","Bowser Flame Left"],
    ["█","Flagpole Blue Block"],
    ["█","Flagpole Brown Block"],
    ["×","Boo"],
    ["█","Green Pipe Horz Top Right"],
    ["█","Green Pipe Horz Bottom Right"],
    ["█","Green Pipe Vert Bottom Left"],
    ["█","Green Pipe Vert Bottom Right"],
    ["█","Green Pipe Horz Bottom Left"],
    ["█","Green Pipe Horz Top Left"],
    ["█","Green Pipe Horz Stem Bottom"],
    ["█","Green Pipe Horz Stem Top"],
    ["√","Win"],
    ["|","Flag Pole"],
    [">","Flag"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["▒","Castle Base Left Top"],
    ["▒","Castle Base Left"],
    ["▒","Castle Base Top"],
    ["▒","Castle Base"],
    ["▒","Castle Door Bottom"],
    ["▒","Castle Base Right Top"],
    ["▒","Castle Base Right"],
    ["▒","Castle Roof Right Edge"],
    ["▒","Castle Roof Medium 5"],
    ["▒","Castle Roof Medium 4"],
    ["▒","Castle Roof Medium 3"],
    ["▒","Castle Roof Medium 2"],
    ["▒","Castle Roof Medium 1"],
    ["▒","Castle Roof Left Edge"],
    ["▒","Castle Window Right"],
    ["▒","Castle Door Top"],
    ["▒","Castle Window Left"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["█","Land Top Left"],
    ["█","Land Top Right"],
    ["█","Castle Solid Brick"],
    ["█","Cave Top Left"],
    ["█","Cave Top Right"],
    ["█","Snow Top Left"],
    ["█","Snow Top Right"],
    ["▒","Mushroom Stem"],
    ["▒","Mushroom Stem Top"],
    ["█","Mushroom Platform Left"],
    ["█","Mushroom Platform Center"],
    ["█","Mushroom Platform Right"],
    ["█","Hidden Coin ?"],
    ["▒","Bush Left"],
    ["▒","Bush Center"],
    ["▒","Bush Right"],
    ["▒","Snowy Tree Top"],
    ["▒","Snowy Tree Bottom"],
    ["▒","Tree Top"],
    ["▒","Tree Bottom"],
    ["▒","Tree Stem"],
    ["▒","Snowy Tree Small"],
    ["▒","Tree Small"],
    ["▒","Snowy Fence"],
    ["▒","Fence"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["S","Start Point Top"],
    ["S","Start Point Bottom"],
    ["↕","Door Top"],
    ["↕","Door Bottom"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["↓","In Warp Down Left"],
    ["↓","In Warp Down Right"],
    ["→","In Warp Right Top"],
    ["→","In Warp Right Bottom"],
    ["←","In Warp Left Top"],
    ["←","In Warp Left Bottom"],
    ["↑","In Warp Up Left"],
    ["↑","In Warp Up Right"],
    ["↕","Castle Door Top"],
    ["↕","Castle Door Bottom"],
    ["↑","Out Warp Up Left"],
    ["↑","Out Warp Up Right"],
    ["←","Out Warp Left Top"],
    ["←","Out Warp Left Bottom"],
    ["→","Out Warp Right Top"],
    ["→","Out Warp Right Bottom"],
    ["↓","Out Warp Down Left"],
    ["↓","Out Warp Down Right"],
    ["O","Out Warp Appear Top"],
    ["O","Out Warp Appear Bottom"],
    ["█","Green Pipe Left and Up Join"],
    ["█","Green Pipe Left and Down Join"],
    ["█","Green Pipe Right and Up Join"],
    ["█","Green Pipe Right and Down Join"],
    ["█","Ghost Platform"],
    ["█","Ghost Pillar Top"],
    ["█","Ghost Pillar"],
    ["█","Ghost Block"],
    ["█","Ghost Bricks Left"],
    ["█","Ghost Bricks Right"],
    ["█","Grey Pipe Horz Bottom Left"],
    ["█","Grey Pipe Horz Top Left"],
    ["█","Grey Pipe Horz Stem Top"],
    ["█","Grey Pipe Horz Stem Bottom"],
    ["█","Grey Pipe Left and Up Join"],
    ["█","Grey Pipe Left and Down Join"],
    ["█","Grey Pipe Right and Up Join"],
    ["█","Grey Pipe Right and Down Join"],
    ["█","Grey Pipe Vert Bottom Left"],
    ["█","Grey Pipe Vert Bottom Right"],
    ["█","Grey Pipe Horz Top Left"],
    ["█","Grey Pipe Horz Bottom Left"],
    ["×","Dry Bones"],
    ["×","Thwomp"], # 194 - SMF tile limit #
    ["·","\x1B[3mNull\x1B[0m"],
]

smf2_tiles=[
    ["·","Empty"],
    ["█","Grey Rock"],
    ["═","Ground Top Center"],
    ["▒","Monty Mole Hole"],
    ["/","Ground 45° Slope Top Up"],
    ["╝","Ground Left and Up Join"],
    ["\\","Ground 45° Slope Top Down"],
    ["╚","Ground Right and Up Join"],
    ["/","Ground 22.5° Slope Top Up 1"],
    ["▒","Ground 22.5° Slope Top Up Extend 1"],
    ["/","Ground 22.5° Slope Top Up 2"],
    ["▒","Ground 22.5° Slope Top Up Extend 2"],
    ["▒","Ground Center"],
    ["\\","Ground 22.5° Slope Top Down 1"],
    ["▒","Ground 22.5° Slope Top Down Extend 1"],
    ["\\","Ground 22.5° Slope Top Down 2"],
    ["▒","Ground 22.5° Slope Top Down Extend 2"],
    ["/","Ground 11.25° Slope Top Up 1"],
    ["▒","Ground 11.25° Slope Top Up Extend 1"],
    ["/","Ground 11.25° Slope Top Up 2"],
    ["▒","Ground 11.25° Slope Top Up Extend 2"],
    ["/","Ground 11.25° Slope Top Up 3"],
    ["/","Ground 11.25° Slope Top Up 4"],
    ["\\","Ground 11.25° Slope Top Down 1"],
    ["▒","Ground 11.25° Slope Top Down Extend 1"],
    ["\\","Ground 11.25° Slope Top Down 2"],
    ["▒","Ground 11.25° Slope Top Down Extend 2"],
    ["\\","Ground 11.25° Slope Top Down 3"],
    ["\\","Ground 11.25° Slope Top Down 4"],
    ["/","Grey Underground 67.5° Slope Top Up 2"],
    ["/","Grey Underground 67.5° Slope Top Up 1"],
    ["▒","Grey Underground 67.5° Slope Top Up Extend"],
    ["\\","Grey Underground 67.5° Slope Top Down 2"],
    ["\\","Grey Underground 67.5° Slope Top Down 1"],
    ["▒","Grey Underground 67.5° Slope Top Down Extend"],
    ["≈","Opaque Water"],
    ["Y","Vine"],
    ["/","Pink Diagonal Right"],
    ["╒","Ground Top Left Semisolid"],
    ["\\","Pink Diagonal Left"],
    ["│","Ground Left Semisolid"],
    ["/","Grey Underground 45° Slope Bottom Up"],
    ["/","Grey Underground 45° Slope Bottom Up Extend"],
    ["\\","Grey Underground 45° Slope Bottom Down"],
    ["\\","Grey Underground 45° Slope Bottom Down Extend"],
    ["/","Grey Underground 22.5° Slope Bottom Up 2"],
    ["/","\x1B[3mNull\x1B[0m"], # 46 - teleports player downwards from left and right, and kills from top and bottom. May be a slope.
    ["/","Grey Underground 22.5° Slope Bottom Up 1"],
    ["/","Grey Underground 22.5° Slope Bottom Up Extend"],
    ["\\","Grey Underground 22.5° Slope Bottom Down 2"],
    ["\\","\x1B[3mNull\x1B[0m"], # 50 - teleports player downwards from left and right, and kills from top and bottom. May be a slope.
    ["\\","Grey Underground 22.5° Slope Bottom Down 1"],
    ["\\","Grey Underground 22.5° Slope Bottom Down Extend"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["·","\x1B[3mNull\x1B[0m"],
    ["█","Flip Block"],
    ["█","Coin ?"],
    ["█","Mushroom ?"],
    ["█","Flower ?"],
    ["█","Feather ?"],
    ["█","Star ?"],
    ["█","Yoshi ?"],
    ["█","Green !"],
    ["█","Yellow !"],
    ["█","Red !"],
    ["█","Blue !"],
    ["█","Disabled Flip Block"],
    ["█","Message Block"],
    ["█","Vine Flip Block"],
    ["║","Ground Left"],
    ["╗","Ground Top Right"],
    ["╚","Ground Right and Up Join"],
    ["╕","Ground Top Right Semisolid"],
    ["│","Ground Right Semisolid"],
    ["║","Ground Right"],
    ["\\","Ground 45° Slope Bottom Down Non-Solid"],
    ["\\","Ground 45° Slope Bottom Down Non-Solid and Top Up Join"],
    ["/","Ground 45° Slope Top Up"],
    ["\\","Ground 45° Slope Top Down Non-Solid and Top Up Join"],
    ["\\","Ground 45° Slope Top Down Non-Solid"],
    ["╔","Grey Underground Top Left"],
    ["═","Grey Underground Top Center"],
    ["▒","Grey Underground Center"],
    ["║","Grey Underground Left"],
    ["╒","Grey Underground Top Left Semisolid"],
    ["│","Grey Underground Left Semisolid"],
    ["╗","Grey Underground Top Right"],
    ["═","Grey Underground Bottom Center"],
    ["║","Grey Underground Right"],
    ["╕","Grey Underground Top Right Semisolid"],
    ["│","Grey Underground Right Semisolid"],
    ["╚","Grey Underground Right and Up Join"],
    ["╝","Grey Underground Left and Up Join"],
    ["/","Grey Underground 45° Slope Top Up"],
    ["╝","Grey Underground Left and Up Join"],
    ["/","Grey Underground 22.5° Slope Top Up 1"],
    ["▒","Grey Underground 22.5° Slope Top Up Extend 1"],
    ["/","Grey Underground 22.5° Slope Top Up 2"],
    ["▒","Grey Underground 22.5° Slope Top Up Extend 2"],
    ["/","Grey Underground 11.25° Slope Top Up 1"],
    ["▒","Grey Underground 11.25° Slope Top Up Extend 1"],
    ["/","Grey Underground 11.25° Slope Top Up 2"],
    ["▒","Grey Underground 11.25° Slope Top Up Extend 2"],
    ["/","Grey Underground 11.25° Slope Top Up 3"],
    ["/","Grey Underground 11.25° Slope Top Up 4"],
    ["\\","Grey Underground 45° Slope Top Down"],
    ["╚","Grey Underground Right and Up Join"],
    ["\\","Grey Underground 22.5° Slope Top Down 1"],
    ["▒","Grey Underground 22.5° Slope Top Down Extend 1"],
    ["\\","Grey Underground 22.5° Slope Top Down 2"],
    ["▒","Grey Underground 22.5° Slope Top Down Extend 2"],
    ["\\","Grey Underground 11.25° Slope Top Down 1"],
    ["▒","Grey Underground 11.25° Slope Top Down Extend 1"],
    ["\\","Grey Underground 11.25° Slope Top Down 2"],
    ["▒","Grey Underground 11.25° Slope Top Down Extend 2"],
    ["\\","Grey Underground 11.25° Slope Top Down 3"],
    ["\\","Grey Underground 11.25° Slope Top Down 4"],
    ["═","Rope Platform"],
    ["▒","Mushroom Stem Single"],
    ["╔","Castle Top Left"],
    ["═","Castle Top Center"],
    ["▒","Castle Center"],
    ["║","Castle Left"],
    ["╝","Castle Left and Up Join"],
    ["╒","Castle Top Left Semisolid"],
    ["│","Castle Left Semisolid"],
    ["╔","Castle Stone Top Left"],
    ["═","Castle Stone Top Center"],
    ["║","Castle Stone Left"],
    ["█","Castle Stone Center"],
    ["╚","Castle Stone Bottom Left"],
    ["═","Castle Stone Bottom Center"],
    ["╗","Castle Stone Top Right"],
    ["║","Castle Stone Right"],
    ["╝","Castle Stone Bottom Right"],
    ["╗","Castle Top Right"],
    ["║","Castle Right"],
    ["╚","Castle Right and Up Join"],
    ["╕","Castle Top Right Semisolid"],
    ["│","Castle Right Semisolid"],
    ["█","Ghost Wood"],
    ["M","Ghost Spikes"],
    ["\\","Ghost Stairs Down"],
    ["▒","Ghost Stairs Down Extend"],
    ["▒","Ghost Stem"],
    ["▒","Ghost Stem Top"],
    ["═","Ghost Platform"],
    ["╔","Ghost Box Top Left"],
    ["╠","Ghost Box Left and Horz Join"],
    ["═","Ghost Box Top"],
    ["║","Ghost Box Left"],
    ["═","Ghost Box Horz"],
    ["█","Ghost Box Center"],
    ["╗","Ghost Box Top Right"],
    ["╣","Ghost Box Right and Horz Join"],
    ["║","Ghost Box Right"],
    ["═","Ghost Box Bottom"],
    ["█","Ghost Bricks Left"],
    ["█","Ghost Bricks Right"],
    ["╚","Ghost Box Bottom Left"],
    ["╝","Ghost Box Bottom Right"],
    ["/","Ghost Stairs Up"],
    ["▒","Ghost Stairs Up Extend"],
    ["▒","Ghost Bricks Background"],
    ["╒","Mushroom Platform Left"],
    ["═","Mushroom Platform Center"],
    ["╕","Mushroom Platform Right"],
    ["│","Mushroom Stem Left"],
    ["▒","Mushroom Stem Center"],
    ["│","Mushroom Stem Right"],
    ["═","Bonus Bottom"],
    ["║","Bonus Right"],
    ["║","Bonus Left"],
    ["═","Bonus Top Center"],
    ["█","Bonus Center"],
    ["╝","Bonus Bottom Right"],
    ["═","Wooden Bridge"],
    ["▒","Wooden Bridge Extend"],
    ["╔","Yellow Underground Top Left"],
    ["═","Yellow Underground Top Center"],
    ["║","Yellow Underground Left"],
    ["╗","Yellow Underground Top Right"],
    ["║","Yellow Underground Right"],
    ["╝","Yellow Underground Left and Up Join"],
    ["╚","Yellow Underground Right and Up Join"],
    ["/","Yellow Underground 45° Slope Top Up"],
    ["╝","Yellow Underground Left and Up Join"],
    ["/","Yellow Underground 22.5° Slope Top Up 1"],
    ["▒","Yellow Underground 22.5° Slope Top Up Extend 1"],
    ["/","Yellow Underground 22.5° Slope Top Up 2"],
    ["▒","Yellow Underground 22.5° Slope Top Up Extend 2"],
    ["\\","Yellow Underground 45° Slope Top Down"],
    ["╚","Yellow Underground Right and Up Join"],
    ["\\","Yellow Underground 22.5° Slope Top Down 1"],
    ["▒","Yellow Underground 22.5° Slope Top Down Extend 1"],
    ["\\","Yellow Underground 22.5° Slope Top Down 2"],
    ["▒","Yellow Underground 22.5° Slope Top Down Extend 2"],
    ["\\","Yellow Underground 45° Slope Bottom Down"],
    ["╗","Yellow Underground Left and Down Join"],
    ["\\","Yellow Underground 22.5° Slope Bottom Down 1"],
    ["▒","Yellow Underground 22.5° Slope Bottom Down Extend 1"],
    ["\\","Yellow Underground 22.5° Slope Bottom Down 2"],
    ["▒","Yellow Underground 22.5° Slope Bottom Down Extend 2"],
    ["/","Yellow Underground 45° Slope Bottom Up"],
    ["╔","Yellow Underground Right and Down Join"],
    ["/","Yellow Underground 22.5° Slope Bottom Up 1"],
    ["▒","Yellow Underground 22.5° Slope Bottom Up Extend 1"],
    ["/","Yellow Underground 22.5° Slope Bottom Up 2"],
    ["▒","Yellow Underground 22.5° Slope Bottom Up Extend 2"],
    ["▒","Yellow Underground Center"],
    ["≈","Opaque Water Top"],
    ["█","Brown Block"],
    ["═","Cloud"],
    ["═","Yellow Bridge"],
    ["▒","Yellow Bridge Extend"],
    ["█","Yellow Small Pipe Left"],
    ["█","Yellow Pipe Center"],
    ["█","Yellow Pipe Right"],
    ["█","Green Small Pipe Top"],
    ["█","Green Small Pipe Center"],
    ["█","Green Small Pipe Bottom"],
    ["╔","Green Pipe Vert Top Left"],
    ["╗","Green Pipe Vert Top Right"],
    ["║","Green Pipe Vert Stem Left"],
    ["║","Green Pipe Vert Stem Right"],
    ["╚","Green Pipe Vert Bottom Left"],
    ["╝","Green Pipe Vert Bottom Right"],
    ["╔","Green Pipe Horz Top Left"],
    ["╚","Green Pipe Horz Bottom Left"],
    ["═","Green Pipe Horz Stem Top"],
    ["═","Green Pipe Horz Stem Bottom"],
    ["╗","Green Pipe Horz Top Right"],
    ["╝","Green Pipe Horz Bottom Right"],
    ["╔","Yellow Pipe Vert Top Left"],
    ["╗","Yellow Pipe Vert Top Right"],
    ["║","Yellow Pipe Vert Stem Left"],
    ["║","Yellow Pipe Vert Stem Right"],
    ["═","Yellow Underground Bottom Center"],
    ["█","Ghost Ground Top Center"],
    ["▒","Goal Pole Top"],
    ["▒","Goal Pole"],
    ["0","Coin"],
    ["╔","Ground Top Left"],
    ["╝","Ground Left and Up Join"],
    ["≈","Seethrough Water Top"],
    ["≈","Seethrough Water"],
    ["≈","Lava Top"],
    ["≈","Lava"],
    ["↕","Door"],
    ["↕","P-Switch Door"],
    ["ʌ","Castle Spike Up"],
    ["v","Castle Spike Down"],
    ["<","Castle Spike Left"],
    [">","Castle Spike Right"],
    ["▒","Dotted Green !"],
    ["▒","Dotted Yellow !"],
    ["▒","Dotted Red !"],
    ["▒","Dotted Blue !"],
    ["▒","Checkpoint Pole Light Top"],
    ["▒","Checkpoint Pole Light"],
    ["▒","Checkpoint Pole Top"],
    ["▒","Checkpoint Pole"],
    ["▒","Bush Left"],
    ["▒","Bush Center"],
    ["▒","Bush Right"],
    ["/","Sloped Green Pipe Top Up Edge"],
    ["/","Sloped Green Pipe Top Up"],
    ["▒","Sloped Green Pipe Top Up Extend"],
    ["▒","Sloped Green Pipe Center"],
    ["/","Sloped Green Pipe Bottom Up"],
    ["▒","Sloped Green Pipe Bottom Up Extend"],
    ["▒","Sloped Green Pipe Top Up Edge Extend"],
    ["▒","Sloped Green Pipe Bottom Up Edge Extend"],
    ["▒","Sloped Green Pipe Top Down Extend"],
    ["\\","Sloped Green Pipe Top Down Left"],
    ["\\","Sloped Green Pipe Top Down Right"],
    ["/","Sloped Green Pipe Bottom Up Edge"],
    ["█","Tank Tires Left"],
    ["█","Tank Tires Center"],
    ["█","Tank Tires Right"],
    ["█","Tank Wood Center 1"],
    ["Z","Tank Wood Left Edge Chipped With Platform"],
    ["█","Tank Wood Window"],
    ["[","Tank Wood Left Edge"],
    ["]","Tank Wood Right Edge"],
    ["█","Tank Wood Center 2"],
    ["\\","Tank Wood Left Edge Chipped Long 1"],
    ["\\","Tank Wood Left Edge Chipped Long 2"],
    ["/","Tank Wood Right Edge Chipped"],
    ["\\","Tank Wood Left Edge Chipped"],
    ["█","Bullet Bill Launcher Stem Top"],
    ["█","Bullet Bill Launcher Stem"],
    ["╔","Torpedo Ted Launcher Top Left"],
    ["╗","Torpedo Ted Launcher Top Right"],
    ["╚","Torpedo Ted Launcher Bottom Left"],
    ["╝","Torpedo Ted Launcher Bottom Right"],
    ["╝","Grey Underground Bottom Right"],
    ["╚","Grey Underground Bottom Left"],
    ["╝","Yellow Underground Bottom Right"],
    ["╚","Yellow Underground Bottom Left"],
    ["×","Yoshi"],
    ["×","Red Koopa Shell"],
    ["█","Triple Platform"],
    ["×","Mushroom"],
    ["×","Fire Flower"],
    ["×","Feather"],
    ["×","Star"],
    ["×","Green Koopa Shell"],
    ["×","Green Koopa"],
    ["×","Red Koopa"],
    ["×","Key"],
    ["×","Goomba"],
    ["×","Shellless Green Koopa"],
    ["×","Shellless Red Koopa"],
    ["×","Jumping Green Koopa"],
    ["×","Jumping Red Koopa"],
    ["×","Flying Green Koopa"],
    ["×","Flying Red Koopa"],
    ["×","Monty Mole"],
    ["×","Monty Mole Out 1 Background"],
    ["×","Monty Mole Out 2 Ground"],
    ["×","Chargin' Chuck"],
    ["×","Jumpin'/Clappin' Chuck"],
    ["×","Baseball/Football Chuck"],
    ["×","Piranha Plant 1 Jump"],
    ["×","Piranha Plant 2 Jump Fire"],
    ["×","Super Koopa 1 Walk"],
    ["×","Walk/Slide Blue Koopa"],
    ["×","Buzzy Beetle Shell"],
    ["×","Buzzy Beetle"],
    ["×","Piranha Plant 3 Attached Upside-Down"],
    ["×","Swooper"],
    ["×","Volcano Lotus"],
    ["×","Yoshi Egg"],
    ["×","Spike Top"],
    ["×","Rex"],
    ["×","Spiny"],
    ["×","Super Koopa 2 Fly"],
    ["×","Bullet Bill"],
    ["×","Boo"],
    ["×","Boo Clock"],
    ["×","Boo Trail"],
    ["×","Eerie"],
    ["×","Dry Bones"],
    ["×","Bony Beetle"],
    ["█","Chain Ball"],
    ["×","Podoboo"],
    ["×","Thwimp"],
    ["×","Fuzzy/Lil' Sparky"],
    ["×","Thwomp"],
    ["×","Cheep Cheep Type 1 Horz/Vert"],
    ["×","Blurp"],
    ["×","Urchin Horz/Vert"],
    ["×","Wall Urchin"],
    ["×","Rip Van Fish"], # 354 - sleeping fish
    ["×","Fish Bone"],
    ["█","Single Rotating Platform"],
    ["=","Moving Platform"],
    ["=","Falling Platform"],
    ["█","Long Platform"],
    ["=","Floating Platform"],
    ["×","Springboard"],
    ["=","Hammer Bro Platform"],
    ["×","Pipe Lakitu"],
    ["×","Cloud Lakitu"],
    ["×","Big Boo/Banzai Bill"],
    ["×","Spikeball/Porcupuffer"],
    ["×","Mega Mole"],
    ["×","Saw"],
    ["×","Torpedo Ted Hand"],
    ["H","Goal Point 1 Gate"],
    ["S","Special Tile"],
    ["×","P-Switch"],
    ["↕","P-Switch Door"],
    ["×","! Switch"],
    ["H","Checkpoint"],
    ["×","Keyhole"],
    ["█","Bullet Bill Launcher"],
    ["G","Sprite Generator Bullet Bill/Super Koopa/Cheep Cheep"],
    ["×","Cheep Cheep Type 2 Jump"],
    ["A","Autoscroll 1/2/3"],
    ["√","Goal Point 2 Ball"],
    ["×","Boom Boom"],
    ["×","Bowser"],
    ["A","Autoscroll 4/5/6"],
    ["█","Brick Block"],
    ["█","Coin Brick"],
    ["█","Mushroom Brick"],
    ["█","Flower Brick"],
    ["█","Feather Brick"],
    ["█","Star Brick"],
    ["█","Yoshi Brick"],
    ["█","Vine Brick"],
    ["V","Muncher"],
    ["┌","Climbing Net Top Left"],
    ["┐","Climbing Net Top Right"],
    ["└","Climbing Net Bottom Left"],
    ["┘","Climbing Net Bottom Right"],
    ["─","Climbing Net Top Center"],
    ["─","Climbing Net Bottom Center"],
    ["│","Climbing Net Left"],
    ["│","Climbing Net Right"],
    ["X","Climbing Net Center"],
    ["┐","Climbing Net Left and Down Join"],
    ["┌","Climbing Net Right and Down Join"],
    ["┘","Climbing Net Left and Up Join"],
    ["└","Climbing Net Right and Up Join"], # 406 - SMF2 tile limit #
    ["·","\x1B[3mNull\x1B[0m"],
]
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
            print("\033[1mGame: \033[0mSuper Mario Flash")
        elif game=="smfe":
            print("\033[1mGame: \033[0mSuper Mario Flash Ver. E")
        else:
            print("\033[31mYou messed with the source code, didn't you? \033[0m")
        print("\033[1mLevel Name: \033[0m"+level_name) if level_name!="" else print("\x1B[3mNone\x1B[0m")
        try:
            print("\033[1mLevel Background: \033[0m"+level_background+" ("+smfe_background_names[int(level_background)]+")")
        except:
            print("\033[1mLevel Background: \033[0m"+level_background+" ("+smfe_background_names[0]+")")
        try:
            print("\033[1mLevel Music: \033[0m"+level_music+" ("+smfe_music_names[int(level_music)]+")")
        except:
            print("\033[1mLevel Music: \033[0m"+level_music+" ("+smfe_music_names[0]+")")
        if int(level_width)/20!=math.floor(int(level_width)/20) and (int(level_width)<320 or int(level_width)>4500):
            print("\033[1mLevel Width: \033[0m"+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles, no right border, unintended size)")
        elif int(level_width)/20!=math.floor(int(level_width)/20):
            print("\033[1mLevel Width: \033[0m"+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles, no right border)")
        elif (int(level_width)<320 or int(level_width)>4500):
            print("\033[1mLevel Width: \033[0m"+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles, unintended size)")
        else:
            print("\033[1mLevel Width: \033[0m"+level_width+" ({:.0f}".format(int(level_width)/20)+" tiles)")
        try:
            print("\033[1mBonus Background: \033[0m"+bonus_background+" ("+smfe_background_names[int(bonus_background)]+")")
        except:
            print("\033[1mBonus Background: \033[0m"+bonus_background+" ("+smfe_background_names[0]+")")
        try:
            print("\033[1mBonus Music: \033[0m"+bonus_music+" ("+smfe_music_names[int(bonus_music)]+")")
        except:
            print("\033[1mBonus Music: \033[0m"+bonus_music+" ("+smfe_music_names[0]+")")
        if int(bonus_width)/20!=math.floor(int(bonus_width)/20) and (int(bonus_width)<320 or int(bonus_width)>4500):
            print("\033[1mBonus Width: \033[0m"+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles, no right border, unintended size)")
        elif int(bonus_width)/20!=math.floor(int(bonus_width)/20):
            print("\033[1mBonus Width: \033[0m"+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles, no right border)")
        elif (int(bonus_width)<320 or int(bonus_width)>4500):
            print("\033[1mBonus Width: \033[0m"+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles, unintended size)")
        else:
            print("\033[1mBonus Width: \033[0m"+bonus_width+" ({:.0f}".format(int(bonus_width)/20)+" tiles)")    
        print("\033[1mStart Point: \033[0m"+start_at+" @ xPos "+start_xpos+" yPos "+start_ypos+" ("+str(int(start_xpos)/20)+" tiles horz, "+str(int(start_ypos)/20)+" tiles vert)")
        print("\033[1mLevel Warps:\033[0m")
        for i in range(len(level_warps)):
            if level_warps[i][2]=="Level" or level_warps[i][2]=="Bonus":
                warp_end_sublevel_print=level_warps[i][2]
            else:
                warp_end_sublevel_print=level_warps[i][2]+" (invalid, \033[33msoftlocks the game\033[0m)"
            if level_warps[i][5]=="right" or level_warps[i][5]=="left":
                warp_end_direction_print="facing "+level_warps[i][5]
            else:
                warp_end_direction_print="\x1B[3mglitchy entrance ("+level_warps[i][5]+")\x1B[0m"
            if level_warps[i][6]=="Up" or level_warps[i][6]=="Down" or level_warps[i][6]=="Left" or level_warps[i][6]=="Right":
                warp_end_type_print="Pipe "+level_warps[i][6]+" Animation"
            elif level_warps[i][6]=="Appear":
                warp_end_type_print="No Animation"
            else:
                warp_end_type_print="\x1B[3minvalid animation \""+level_warps[i][6]+"\"\033[33msoftlocks the game\033[0m)"
            warp_print="\tWarp from xPos "+str(int(level_warps[i][1])*20)+" yPos "+str(int(level_warps[i][0])*20)+" to xPos "+level_warps[i][3]+" yPos "+level_warps[i][4]+" in "+warp_end_sublevel_print+", "+warp_end_direction_print+", "+warp_end_type_print
            
            print(warp_print)
        if level_warps==[]:
            warp_print="\x1B[3m\tNone\x1B[0m"
            print(warp_print)
        print("\033[1mBonus Warps:\033[0m")
        for i in range(len(bonus_warps)):
            if bonus_warps[i][2]=="Level" or bonus_warps[i][2]=="Bonus":
                warp_end_sublevel_print=bonus_warps[i][2]
            else:
                warp_end_sublevel_print=bonus_warps[i][2]+" (invalid, \033[33msoftlocks the game\033[0m)"
            if bonus_warps[i][5]=="right" or bonus_warps[i][5]=="left":
                warp_end_direction_print="facing "+bonus_warps[i][5]
            else:
                warp_end_direction_print="\x1B[3mglitchy entrance ("+bonus_warps[i][5]+")\x1B[0m"
            if bonus_warps[i][6]=="Up" or bonus_warps[i][6]=="Down" or bonus_warps[i][6]=="Left" or bonus_warps[i][6]=="Right":
                warp_end_type_print="Pipe "+bonus_warps[i][6]+" Animation"
            elif bonus_warps[i][6]=="Appear":
                warp_end_type_print="No Animation"
            else:
                warp_end_type_print="\x1B[3minvalid animation \""+bonus_warps[i][6]+"\"\033[33msoftlocks the game\033[0m)"
            warp_print="\tWarp from xPos "+str(int(bonus_warps[i][1])*20)+" yPos "+str(int(bonus_warps[i][0])*20)+" to xPos "+bonus_warps[i][3]+" yPos "+bonus_warps[i][4]+" in "+warp_end_sublevel_print+", "+warp_end_direction_print+", "+warp_end_type_print
            
            print(warp_print)
        if bonus_warps==[]:
            warp_print="\x1B[3m\tNone\x1B[0m"
            print(warp_print)
    elif game=="smf2" or game=="smf2c":
        if game=="smf2":
            print("\033[1mGame: \033[0mSuper Mario Flash 2")
        elif game=="smf2c":
            print("\033[1mGame: \033[0mSuper Mario Flash 2 Ver. C")
        else:
            print("\033[31mYou messed with the source code, didn't you? \033[0m")
        print("\033[1mLevel Name: \033[0m"+level_name) if level_name!="" else print("\x1B[3mNone\x1B[0m")
        print("\033[1mDescription: \033[0m"+level_description) if level_description!="" else print("\x1B[3mNone\x1B[0m")
        print("\033[1mAuthor: \033[0m"+level_author) if level_author!="" else print("\x1B[3mNone\x1B[0m")
        print("\033[1mMessage Block Text: «\033[0m"+level_message+"\033[1m»\033[0m")
        try:
            if game=="smf2":
                print("\033[1mBackground: \033[0m"+level_background+" ("+smf2_background_names[int(level_background)]+")")
            elif game=="smf2c":
                print("\033[1mBackground: \033[0m"+level_background+" ("+smf2c_background_names[int(level_background)]+")")
        except:
            print("\033[1mBackground: \033[0m"+level_background+" ("+smf2_background_names[0]+")")
        if level_background=="11":
            print("\033[1mBackground URL 1: \033[0m\u001b[36m\u001b[4m"+level_url1+"\033[0m") if level_url1!="" else print("\033[1mBackground URL 1: \033[0m\x1B[3mNone\x1B[0m")
            print("\033[1mBackground URL 2: \033[0m\u001b[36m\u001b[4m"+level_bg_url2+"\033[0m") if level_bg_url2!="" else print("\033[1mBackground URL 2: \033[0m\x1B[3mNone\x1B[0m")
        try:
            print("\033[1mMusic: \033[0m"+level_music+" ("+smf2c_music_names[int(level_music)]+")")
        except:
            print("\033[1mMusic: \033[0m"+level_music+" ("+smf2c_music_names[0]+")")
        try:
            print("\033[1mMario's State: \033[0m"+level_powerup+" ("+smf2_powerup_names[int(level_powerup)]+")")
        except:
            print("\033[1mMario's State: \033[0m"+level_powerup+" ("+smf2_powerup_names[0]+")")
        print("\033[1mLevel Dimensions: \033[0m"+level_width+"x"+level_height+" ("+str(int(level_height)/20)+" Rows by "+str(int(level_width)/20)+" Columns)")
        print("\033[1mUnknown Variable=\033[0m"+level_variable_1)
        print("\033[1mUnknown Variable=\033[0m"+level_variable_2)
        try:
            print("\033[1mLayer 1 Priority: \033[0m"+level_layer_priority+" (On Top)") if int(level_layer_priority)>=3 else print("\033[1mLayer 1 Priority: \033[0m"+level_layer_priority+" (On Bottom)")
        except:
            print("\033[1mLayer 1 Priority: \033[0m"+level_layer_priority+" (Invalid)")
        print("\033[1mLayer 2 Dimensions: \033[0m"+level_layer2_width+"x"+level_layer2_height+" ("+str(int(level_layer2_height)/20)+" Rows by "+str(int(level_layer2_width)/20)+" Columns)")
        print("\033[1mLayer 2 X Offset: \033[0m"+level_layer2_xpos)
        print("\033[1mLayer 2 Y Offset: \033[0m"+level_layer2_ypos)
        try:
            print("\033[1mLayer 2 Priority: \033[0m"+level_layer_priority_2+" (On Bottom)") if int(level_layer_priority_2)<=2 else print("\033[1mLayer 2 Priority: \033[0m"+level_layer_priority_2+" (On Top)")
        except:
            print("\033[1mLayer 2 Priority: \033[0m"+level_layer_priority_2+" (Invalid)")
        print("\033[1mUnknown Variable=\033[0m"+level_variable_3)
        print("\033[1mEntrances:\033[0m")
        for i in range(len(all_entrances)):
            if i==0:
                entrance_print="\t\033[1mID "+str(i+1)+" (Starting Point):\033[0m "
            else:
                entrance_print="\t\033[1mID "+str(i+1)+":\033[0m "
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
            
            entrance_print=entrance_print+entrance_type_print+" ["+all_entrances[i][0]+"], "+entrance_mario_status_print+" ["+all_entrances[i][3]+"] @ xPos "+all_entrances[i][1]+" yPos "+all_entrances[i][2]+" ("+str(int(all_entrances[i][1])/20)+" tiles horz, "+str(int(all_entrances[i][2])/20)+" tiles vert)"

            print(entrance_print)
        print("\033[1mExits:\033[0m")
        exit_print=""
        for i in range(len(all_exits)):
            exit_print="\t"
            try: 
                exit_type_print=smf2_exit_types[int(all_exits[i][2])]
            except:
                exit_type_print=smf2_exit_types[0]

            exit_print=exit_print+exit_type_print+" ["+all_exits[i][2]+"] to \033[1mID "+str(int(all_exits[i][3])+1)+"\033[0m @ xPos "+str(int(all_exits[i][0])*20)+" yPos "+str(int(all_exits[i][1])*20)+" ("+all_exits[i][0]+" tiles horz, "+all_exits[i][1]+" tiles vert)"
            print(exit_print)
            
        if exit_print=="":
            print("\x1B[3m\tNone\x1B[0m")
    else:
        print("\x1B[3mNo level in memory!\x1B[0m")

def openFile(filePath):
    if filePath=="":
        filePath=filedialog.askopenfilename(title="Please open a Super Mario Flash level file.", initialdir=filePath)
        if filePath=="":
            print("\x1B[3mNo File Opened!\x1B[0m")
            return
    else:
        filePath=os.path.normpath(filePath)
        if os.path.isdir(filePath):
            root = tk.Tk()
            root.withdraw()

            filePath=filedialog.askopenfilename(title="Please open a Super Mario Flash level file.", initialdir=filePath)
            if filePath=="":
                print("\x1B[3mNo File Opened!\x1B[0m")
                return
    try:
        file=open(filePath,mode='r', encoding="utf-8")
        level_code=file.read()
    except UnicodeDecodeError:
        print("\033[31mInvalid file!\nConsider converting your level data to txt or csv.\033[0m")
        return
    except FileNotFoundError:
        print("\x1B[3mNo such file or directory!\x1B[0m")
        return

    #print(level_code) # useful for debugging

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
            errorString=str(e)+" occured on line "+str(e.__traceback__.tb_lineno)
            print("\033[31m"+"Invalid or incomplete level code\n"+errorString+"\033[0m")
            return
        except ValueError as e:
            errorString=str(e)+" occured on line "+str(e.__traceback__.tb_lineno)
            print("\033[31m"+"Invalid tile data\n"+errorString+"\033[0m")
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
            print("\033[31m"+"exception encountered during parsing\ndata dump:\n\nlevel_name: "+level_name+"\nlevel_description: "+level_description+"\nlevel_author: "+level_author+"\nlevel_message: "+level_message+"\nlevel_background: "+level_background+"\nlevel_url1: "+level_url1+"\nlevel_bg_url2: "+level_bg_url2+"\nlevel_music: "+level_music+"\nlevel_powerup: "+level_powerup+"\nlevel_width: "+level_width+"\nlevel_height: "+level_height+"\nlevel_variable_1: "+level_variable_1+"\nlevel_variable_2: "+level_variable_2+"\nlevel_layer_priority: "+level_layer_priority+"\nlevel_layer2_width: "+level_layer2_width+"\nlevel_layer2_height: "+level_layer2_height+"\nlevel_layer2_xpos: "+level_layer2_xpos+"\nlevel_layer2_ypos: "+level_layer2_ypos+"\nlevel_layer_priority_2: "+level_layer_priority_2+"\nlevel_variable_3: "+level_variable_3+"\noneentrance: "+str(oneentrance)+"\nall_entrances: "+str(all_entrances)+"\noneexit: "+str(oneexit)+"\nall_exits: "+str(all_exits)+"\nlayer_1: "+str(layer_1)+"\nlayer_2: "+str(layer_2)+"\ncurrent_row: "+str(current_row)+"\ntiles_processed: "+str(tiles_processed)+"\n\n"+str(e)+" occured on line "+str(e.__traceback__.tb_lineno)+"\033[0m")
            return
        
    else:
        print("\033[31m"+"Invalid level code!\nNo valid delimiters found in file."+"\033[0m")
        return
        
def exportAll(fileFormat):
    if game=="smf" or game=="smfe":
        filePath=filedialog.askdirectory()
        if filePath=="":
            print("\x1B[3mNo Path Selected!\x1B[0m")
            return
        if fileFormat=="csv":
            output="SMFDATA\nname=\""+level_name+"\"\nlvlbg="+level_background+"\nlvlmusic="+level_music+"\nlvlwidth="+level_width+"\nbnsbg="+bonus_background+"\nbnsmusic="+bonus_music+"\nbnswidth="+bonus_width+"\n\nstart("+start_xpos+","+start_ypos+") @ "+start_at
            print("Gathering level header data...")
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_header.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print("\033[33m\x1B[3mFile in use!\033[0m")
            output="SMFWARPS"
            print("Processing warp data...")
            for i in range(len(level_warps)):
                output+="\nfrom("+level_warps[i][1]+","+level_warps[i][0]+")levelto("+level_warps[i][3]+","+level_warps[i][4]+")in"+level_warps[i][2]+",facing\""+level_warps[i][5]+"\",anim\""+level_warps[i][6]+"\""
            for i in range(len(bonus_warps)):
                output+="\nfrom("+bonus_warps[i][1]+","+bonus_warps[i][0]+")bonusto("+bonus_warps[i][3]+","+bonus_warps[i][4]+")in"+bonus_warps[i][2]+",facing\""+bonus_warps[i][5]+"\",anim\""+bonus_warps[i][6]+"\""
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_warps.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
        elif fileFormat=="txt":
            output="("
            for i in level:
                for j in i:
                    output+=j+","
            try:
                output+=level_name+","+level_background+","+start_xpos+","+start_ypos+","+level_music+","+str(int(level_width)-320)+",)("
            except:
                output+=level_name+","+level_background+","+start_xpos+","+start_ypos+","+level_music+","+level_width+",)("
            for i in bonus:
                for j in i:
                    output+=j+","
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
        else:
            print("\x1B[3mInvalid file format!\x1B[0m")
            return
        print("\033[92mSuccess!\033[0m")
        return
    elif game=="smf2" or game=="smf2c":
        filePath=filedialog.askdirectory()
        if filePath=="":
            print("\x1B[3mNo Path Selected!\x1B[0m")
            return
        if fileFormat=="csv":
            output="SMF2DATA\nname=\""+level_name+"\"\ndescription=\""+level_description+"\"\nauthor=\""+level_author+"\"\nmessage=\""+level_message+"\"\n\nbg="+level_background+"\nurl1=\""+level_url1+"\"\nurl2=\""+level_bg_url2+"\"\nmusic="+level_music+"\nstartstatus="+level_powerup+"\nlayerpriority1="+level_layer_priority+"\nlayerpriority2="+level_layer_priority_2+"\nlayer2xpos="+level_layer2_xpos+"\nlayer2ypos="+level_layer2_ypos+"\nvar1="+level_variable_1+"\nvar2="+level_variable_2+"\nvar3="+level_variable_3
            print("Gathering level header data...")
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_header.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print("\033[33m\x1B[3mFile in use!\033[0m")
            output="SMF2WARPS"
            print("Processing warp data...")
            for i in range(len(all_entrances)):
                output+="\nentrance"+str(i+1)+"[x:"+all_entrances[i][1]+",y:"+all_entrances[i][2]+",anim:"+all_entrances[i][0]+",status:"+all_entrances[i][3]+"]"
            output+="\n"
            for i in range(len(all_exits)):
                output+="\nexit[x:"+all_exits[i][0]+",y:"+all_exits[i][1]+",type:"+all_exits[i][2]+",to:"+all_exits[i][3]+"]"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_warps.txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
            output=""
            tiles_read=0
            for i in layer_2:
                for j in i:
                    print("Processed "+str(tiles_read)+"/"+str(int((int(level_layer2_height)/20)*(int(level_layer2_width)/20)))+" Layer 2 tiles ("+str(math.floor(tiles_read/((int(level_layer2_height)/20)*(int(level_layer2_width)/20))*100))+"% done)", end='\r')
                    output+=j+","
                    tiles_read+=1
                output+="\n"
                if output[-1:]==",":
                    output=output[:-1]
                output+="\n"
            print("Processed all "+str(tiles_read)+" tiles in Layer 2.            ")
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+"_layer2.csv"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                    output+=j+","
            output+="&"
            for i in layer_2:
                for j in i:
                    output+=j+","
            output+="&"
            try:
                file=open(str(filePath+"/"+level_name.replace("/","⧸").replace("\\","⧹").replace("*","⁎").replace("\"","‟").replace("<","❮").replace(">","❯").replace(":","˸").replace("|","⏐").replace("?","？")+".txt"),mode='w', encoding="utf-8")
                file.write(output)
                file.close()
            except PermissionError:
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
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
                print("\033[33m\x1B[3mFile in use!\033[0m")
        else:
            print("\x1B[3mInvalid file format!\x1B[0m")
            return
        print("\033[92mSuccess!\033[0m")
        return
    else:
        print("\x1B[3mNo level in memory!\x1B[0m")
        return

def importTiles(toModify):
    if toModify=="":
        print("\x1B[3mNo property specified!\x1B[0m")
        return
    
    global level
    global bonus
    
    global layer_1
    global layer_2
    
    global level_width
    global level_height
    
    if game!="":
        if toModify=="level" or toModify=="lvl" or toModify=="l":
            if game=="smf" or game=="smfe":
                level.clear()
            elif game=="smf2" or game=="smf2c":
                print("\x1B[3mIncorrect game mode - level is an SMF-only property!\x1B[0m")
                return
        elif toModify=="bonus" or toModify=="bns" or toModify=="b":
            if game=="smf" or game=="smfe":
                bonus.clear()
            elif game=="smf2" or game=="smf2c":
                print("\x1B[3mIncorrect game mode - bonus is an SMF-only property!\x1B[0m")
                return
        elif toModify=="layer 1" or toModify=="layer1" or toModify=="l1":
            if game=="smf2" or game=="smf2c":
                layer_1.clear()
            elif game=="smf" or game=="smfe":
                print("\x1B[3mIncorrect game mode - layer 1 is an SMF2-only property!\x1B[0m")
                return
        elif toModify=="layer 2" or toModify=="layer2" or toModify=="l2":
            if game=="smf2" or game=="smf2c":
                layer_2.clear()
            elif game=="smf" or game=="smfe":
                print("\x1B[3mIncorrect game mode - layer 2 is an SMF2-only property!\x1B[0m")
                return
        else:
            print("\x1B[3mInvalid Property!\x1B[0m")
            return
        filePath=filedialog.askopenfilename(title="Please open Super Mario Flash level tiles.")
        if filePath=="":
            print("\x1B[3mNo File Opened!\x1B[0m")
            return
        file=open(filePath,mode='r', encoding="utf-8")
        try:
            file_data=file.read()
        except UnicodeDecodeError:
            print("\033[31mInvalid file!\nConsider converting your level data to txt or csv.\033[0m")
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
                    if level_width!=len(row)*20:
                        level_width=len(row)*20
                    row.clear()
                    tile=""
                elif toModify=="layer 2" or toModify=="layer2" or toModify=="l2":
                    row.append(tile)
                    frozen_row=tuple(row)
                    layer_2.append(frozen_row)
                    if level_layer2_width!=len(row)*20:
                        level_layer2_width=len(row)*20
                    row.clear()
                    tile=""
            else:
                tile+=file_data[i]
        if toModify=="layer 1" or toModify=="layer1" or toModify=="l1":
            if level_height!=len(layer_1)*20:
                level_height=len(layer_1)*20
        elif toModify=="layer 2" or toModify=="layer2" or toModify=="l2":
            if level_layer2_height!=len(layer_2)*20:
                level_layer2_height=len(layer_2)*20
        print("\033[92mSuccess!\033[0m")
    else:
        print("\x1B[3mNo level in memory!\x1B[0m")
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
        print("\033[31mCurrent console environment does not support Curses.\033[0m")
        return [yPos,xPos,sublevel,xPosTo,yPosTo,playerDir,animation]
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
    console.addstr(7,0,"[Cancel]")
    console.addstr(8,0,"[Save]")
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
        console.addstr(7,1,"Cancel")
        console.addstr(8,1,"Save")
        
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
            console.addstr(7,1,"Cancel",curses.A_REVERSE)
        elif current_item==8:
            console.addstr(8,1,"Save",curses.A_REVERSE)
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
        print("\033[31mCurrent console environment does not support Curses.\033[0m")
        return
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
    console.addstr(5,0,"[Cancel]")
    console.addstr(6,0,"[Save]")
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
        console.addstr(5,1,"Cancel")
        console.addstr(6,1,"Save")
        
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
            console.addstr(5,1,"Cancel",curses.A_REVERSE)
        elif current_item==5:
            console.addstr(6,1,"Save",curses.A_REVERSE)
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

def replace(data):
    toModify=""
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
        if data[:7]=="header ":
            toModify="header"
            data=data[7:]
        elif data[:5]=="head ":
            toModify="header"
            data=data[5:]
        elif data[:2]=="h ":
            toModify="header"
            data=data[2:]
        elif data=="header" or data=="head":
            toModify="header"
            data=""
        elif data[:1]=="h":
            toModify="header"
            data=data[1:]
        elif data[:5]=="warp ":
            toModify="warps"
            data=data[5:]
        elif data[:4]=="warp":
            toModify="warps"
            data=data[4:]
        elif data[:2]=="w ":
            toModify="warps"
            data=data[2:]
        elif data[:5]=="warps":
            toModify="warps"
            data=""
        elif data[:1]=="w":
            toModify="warps"
            data=data[1:]
        elif data[:9]=="entrance ":
            toModify="entrances"
            data=data[9:]
        elif data[:8]=="entrance":
            toModify="entrances"
            data=data[8:]
        elif data[:5]=="entr ":
            toModify="entrances"
            data=data[5:]
        elif data[:4]=="entr":
            toModify="entrances"
            data=data[4:]
        elif data[:9]=="entrances":
            toModify="entrances"
            data=""
        elif data[:2]=="n ":
            toModify="entrances"
            data=data[2:]
        elif data[:1]=="n":
            toModify="entrances"
            data=data[1:]
        elif data[:5]=="exit ":
            toModify="exits"
            data=data[5:]
        elif data[:4]=="exit":
            toModify="exits"
            data=data[4:]
        elif data[:5]=="exits":
            toModify="exits"
            data=""
        elif data[:2]=="x ":
            toModify="exits"
            data=data[2:]
        elif data[:1]=="x":
            toModify="exits"
            data=data[1:]
        elif data[:6]=="tiles ":
            toModify="tiles"
            data=data[6:]
        elif data[:5]=="tiles":
            toModify="tiles"
            data=data[5:]
        elif data[:2]=="t ":
            toModify="tiles"
            data=data[2:]
        elif data[:1]=="t":
            toModify="tiles"
            data=data[1:]
        else:
            print("\x1B[3mInvalid attribute!\x1B[0m")
            return
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
                print("\x1B[3mInvalid attribute!\x1B[0m")
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
            if data=="+":
                toModifySub="add"
            else:
                warpNum=""
                for i in data:
                    if i==" " or not i.isnumeric():
                        break
                    else:
                        warpNum+=i
                if warpNum=="":
                    print("\x1B[3mPlease specify a warp number.\x1B[0m")
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
                    print("\x1B[3mInvalid attribute!\x1B[0m")
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
                        print("\x1B[3mPlease specify an entrance ID between 1 and "+str(len(all_entrances))+"\x1B[0m")
                    else:
                        print("\x1B[3mPlease specify an exit number between 0 and "+str(len(all_exits)-1)+"\x1B[0m")
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
                    print("\x1B[3mInvalid attribute!\x1B[0m")
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
                print("\x1B[3mInvalid attribute!\x1B[0m")
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
                    level_name=input("Change level name from «"+level_name+"» to: ")
                print("Successfully changed level name!")
            elif toModifySub=="lvlwidth":
                if game=="smf" or game=="smfe":
                    if data!="":
                        level_width=data
                    else:
                        level_width=input("Change level width from "+level_width+" to: ")
                    try:
                        print("Successfully changed level width to "+level_width+" ("+str(int(level_width)/20)+" tiles)")
                    except:
                        print("Successfully changed level width to "+level_width+" (not an integer - issues may occur)")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mChanging the level width in an SMF2 level without changing the level tiles will cause issues. Action denied.\x1B[0m")
            elif toModifySub=="lvlbg":
                if game=="smf" or game=="smfe":
                    if data!="":
                        level_background=data
                    else:
                        level_background=input("Change level background from "+level_background+" to: ")
                    try:
                        if int(level_background)>6:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print("Successfully changed level background to "+level_background+" ("+smfe_background_names[int(level_background)]+")")
                    except:
                        print("Successfully changed level background to "+level_background+" ("+smfe_background_names[0]+")")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
            elif toModifySub=="lvlmus":
                if game=="smf" or game=="smfe":
                    if data!="":
                        level_music=data
                    else:
                        level_music=input("Change level music from "+level_music+" to: ")
                    try:
                        if int(level_music)>11:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print("Successfully changed level music to "+level_music+" ("+smfe_music_names[int(level_music)]+")")
                    except:
                        print("Successfully changed level music to "+level_music+" ("+smfe_music_names[0]+")")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
            elif toModifySub=="bnsbg":
                if game=="smf" or game=="smfe":
                    if data!="":
                        bonus_background=data
                    else:
                        bonus_background=input("Change bonus background from "+bonus_background+" to: ")
                    try:
                        if int(bonus_background)>6:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print("Successfully changed bonus background to "+bonus_background+" ("+smfe_background_names[int(bonus_background)]+")")
                    except:
                        print("Successfully changed bonus background to "+bonus_background+" ("+smfe_background_names[0]+")")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
            elif toModifySub=="bnsmus":
                if game=="smf" or game=="smfe":
                    if data!="":
                        bonus_music=data
                    else:
                        bonus_music=input("Change bonus music from "+bonus_music+" to: ")
                    try:
                        if int(bonus_music)>11:
                            print("Game forced to switch to SMF E")
                            game="smfe"
                        print("Successfully changed bonus music to "+bonus_music+" ("+smfe_music_names[int(bonus_music)]+")")
                    except:
                        print("Successfully changed bonus music to "+bonus_music+" ("+smfe_music_names[0]+")")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
            elif toModifySub=="startx":
                if game=="smf" or game=="smfe":
                    if data!="":
                        start_xpos=data
                    else:
                        start_xpos=input("Change start xPos from "+start_xpos+" to: ")
                    try:
                        print("Successfully changed start xPos to "+start_xpos+" ("+int(start_xpos)/20+" tiles)")
                    except:
                        print("Successfully changed start xPos to "+start_xpos+" (0 tiles)")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mIn SMF2, player's start coordinates are stored in entrance data, not the header.\x1B[0m")
            elif toModifySub=="starty":
                if game=="smf" or game=="smfe":
                    if data!="":
                        start_ypos=data
                    else:
                        start_ypos=input("Change start yPos from "+start_ypos+" to: ")
                    try:
                        print("Successfully changed start yPos to "+start_ypos+" ("+int(start_ypos)/20+" tiles)")
                    except:
                        print("Successfully changed start yPos to "+start_ypos+" (0 tiles)")
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mIn SMF2, player's start coordinates are stored in entrance data, not the header.\x1B[0m")
            elif toModifySub=="startat":
                if game=="smf" or game=="smfe":
                    if data=="":
                        start_at=input("Change start sublevel from "+start_at+" to: ")
                    if data.lower()=="level" or data.lower()=="lvl" or data.lower()=="l":
                        start_at="Level"
                    elif data.lower()=="bonus" or data.lower()=="bns" or data.lower()=="b":
                        start_at="Bonus"
                    else:
                        print("\x1B[3mInvalid sublevel!\x1B[0m")
                        return
                    print("Successfully changed start sublevel to "+start_at)
                elif game=="smf2" or game=="smf2c":
                    print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
            elif toModifySub=="desc":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_description=data
                    else:
                        level_description=input("Change level description to: ")
                    print("Successfully changed level description!")
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mNo description attribute exists for SMF.\x1B[0m")
            elif toModifySub=="bg":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_background=data
                    else:
                        level_background==input("Change background from "+level_background+" to: ")
                    if game=="smf2c":
                        try:
                            print("Successfully changed background to "+level_background+" ("+smf2c_background_names[int(level_background)]+")")
                        except:
                            print("Successfully changed background to "+level_background+" ("+smf2c_background_names[0]+")")
                    else:
                        try:
                            if int(level_background)>11:
                                print("Game forced to switch to SMF2 C")
                                game="smf2c"
                                print("Successfully changed background to "+level_background+" ("+smf2c_background_names[int(level_background)]+")")
                            else:
                                print("Successfully changed background to "+level_background+" ("+smf2_background_names[int(level_background)]+")")
                        except:
                            print("Successfully changed background to "+level_background+" ("+smf2_background_names[0]+")")
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mNo background attribute exists for SMF. Please specify whether you're modifying a level or bonus background.\x1B[0m")
            elif toModifySub=="mus":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_music=data
                    else:
                        level_music=input("Change background from "+level_music+" to: ")
                    if game=="smf2c":
                        try:
                            print("Successfully changed music to "+level_music+" ("+smf2c_music_names[int(level_music)]+")")
                        except:
                            print("Successfully changed music to "+level_music+" ("+smf2c_music_names[0]+")")
                    else:
                        try:
                            if int(level_music)==19:
                                print("Game forced to switch to SMF2 C")
                                game="smf2c"
                            print("Successfully changed music to "+level_music+" ("+smf2c_music_names[int(level_music)]+")")
                        except:
                            print("Successfully changed music to "+level_music+" ("+smf2c_music_names[0]+")")
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mNo music attribute exists for SMF. Please specify whether you're modifying the level or bonus music.\x1B[0m")
            elif toModifySub=="powerup":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_powerup=data
                    else:
                        level_powerup=input("Change start state from "+level_powerup+" to: ")
                    try:
                        print("Successfully changed start state to "+level_powerup+" ("+smf2_powerup_names[int(level_powerup)]+")")
                    except:
                        print("Successfully changed start state to "+level_powerup+" ("+smf2_powerup_names[29]+")")
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mNo start state attribute exists for SMF.\x1B[0m")
            elif toModifySub=="url1":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_url1=data
                    else:
                        level_url1=input("Change background url 1 to: ")
                    print("Game forced to switch to background 11 ("+smf2_background_names[11]+")")
                    level_background=11
                    print("Successfully changed background url 1 to "+level_url1)
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mSMF has no custom backgrounds.\x1B[0m")
            elif toModifySub=="url2":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_bg_url2=data
                    else:
                        level_bg_url2=input("Change background url 2 to: ")
                    print("Game forced to switch to background 11 ("+smf2_background_names[11]+")")
                    level_background=11
                    print("Successfully changed background url 2 to "+level_bg_url2)
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mSMF has no custom backgrounds.\x1B[0m")
            elif toModifySub=="layerpri1":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer_priority=data
                    else:
                        level_layer_priority=input("Change layer priority 1 from "+level_layer_priority+" to: ")
                    print("Successfully changed layer priority 1 to "+level_layer_priority)
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mSMF has no layers.\x1B[0m")
            elif toModifySub=="layerpri2":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer_priority_2=data
                    else:
                        level_layer_priority_2=input("Change layer priority 2 from "+level_layer_priority_2+" to: ")
                    print("Successfully changed layer priority 2 to "+level_layer_priority_2)
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mSMF has no layers.\x1B[0m")
            elif toModifySub=="layer2x":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer2_xpos=data
                    else:
                        level_layer2_xpos=input("Change layer 2 xPos from "+level_layer2_xpos+" to: ")
                    print("Successfully changed layer 2 xPos to "+level_layer2_xpos)
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mSMF has no layers.\x1B[0m")
            elif toModifySub=="layer2y":
                if game=="smf2" or game=="smf2c":
                    if data!="":
                        level_layer2_ypos=data
                    else:
                        level_layer2_ypos=input("Change layer 2 yPos from "+level_layer2_ypos+" to: ")
                    print("Successfully changed layer 2 yPos to "+level_layer2_ypos)
                elif game=="smf" or game=="smfe":
                    print("\x1B[3mSMF has no layers.\x1B[0m")
            elif toModifySub=="":
                global decorType
                
                try:
                    console=curses.initscr()
                except:
                    print("\033[31mCurrent console environment does not support Curses.\033[0m")
                    return
                console.keypad(True)
                console.clear()
                if decorType!=0:
                    console.addstr(0,0," Header ".center(screenx,decorTypes[decorType]))
                else:
                    console.addstr(0,0,"Header")
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
                    console.addstr(10,0,"[Cancel]")
                    console.addstr(11,0,"[Save]")
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
                        console.addstr(10,1,"Cancel")
                        console.addstr(11,1,"Save")
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
                            console.addstr(10,1,"Cancel",curses.A_REVERSE)
                        elif current_item==7:
                            console.addstr(11,1,"Save",curses.A_REVERSE)
                        console.refresh()
                        key=console.getch()
                        console.refresh()
                        if key==10: # Enter
                            if current_item<6:
                                current_item=(current_item+1)%8
                                if current_item==6:
                                    level_background,level_music,level_width,bonus_background,bonus_music,bonus_width=old_data
                                curses.endwin()
                                print("Exited header editor.")
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
                    console.addstr(15,0,"[Cancel]")
                    console.addstr(16,0,"[Save]")
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
                        console.addstr(15,1,"Cancel")
                        console.addstr(16,1,"Save")
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
                            console.addstr(15,1,"Cancel",curses.A_REVERSE)
                        elif current_item==11:
                            console.addstr(16,1,"Save",curses.A_REVERSE)
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
                                print("Exited header editor.")
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
                print("\x1B[3mInvalid attribute!\x1B[0m")
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
                            print("\x1B[3mWarp number too high!\x1B[0m")
                        elif len(level_warps)==0:
                            print("\x1B[3mNo warps exist for this sublevel. Please create a new one.\x1B[0m")
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
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
                            elif toModifySub=="ypos":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[0]=data
                                    else:
                                        modified[0]=input("Change yPos of warp from "+modified[0]+" to: ")
                                    print("Successfully changed yPos of warp to "+modified[0])
                                elif game=="smf2" or game=="smf2c":
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
                            elif toModifySub=="xposto":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[3]=data
                                    else:
                                        modified[3]=input("Change xPos of warp's exit from "+modified[3]+" to: ")
                                    print("Successfully changed xPos of warp's exit to "+modified[3])
                                elif game=="smf2" or game=="smf2c":
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
                            elif toModifySub=="yposto":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[4]=data
                                    else:
                                        modified[4]=input("Change yPos of warp's exit from "+modified[4]+" to: ")
                                    print("Successfully changed yPos of warp's exit to "+modified[4])
                                elif game=="smf2" or game=="smf2c":
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
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
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
                            elif toModifySub=="dir":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[5]=data
                                    else:
                                        modified[5]=input("Change direction of warp from "+modified[5]+" to: ")
                                    print("Successfully changed direction of warp to "+modified[5])
                                elif game=="smf2" or game=="smf2c":
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
                            elif toModifySub=="type":
                                if game=="smf" or game=="smfe":
                                    if data!="":
                                        modified[6]=data
                                    else:
                                        modified[6]=input("Change animation of warp from "+modified[6]+" to: ")
                                    print("Successfully changed animation of warp to "+modified[6])
                                elif game=="smf2" or game=="smf2c":
                                    print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
                            else:
                                modified=smfWarpModifier(modified[0],modified[1],modified[2],modified[3],modified[4],modified[5],modified[6])
                            level_warps[int(warpNum)]=tuple(modified)
                    elif sublevel=="Bonus":
                        if int(warpNum)>len(bonus_warps)-1:
                            print("\x1B[3mWarp number too high!\x1B[0m")
                        elif len(bonus_warps)==0:
                            print("\x1B[3mNo warps exist for this sublevel. Please create a new one.\x1B[0m")
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
                    print("\x1B[3mInvalid attribute!\x1B[0m")
            elif game=="smf2" or game=="smf2c":
                print("\x1B[3mWarps are an SMF-only property. Please refer to Entrances or Exits.\x1B[0m")
        elif toModify=="entrances":
            if game=="smf2" or game=="smf2c":
                if toModifySub=="add":
                    all_entrances.append(tuple(smf2WarpModifier("Entrances","0","0","0","1")))
                elif warpNum!="":
                    if int(warpNum)>len(all_entrances):
                        print("\x1B[3mEntrance number too high!\x1B[0m")
                    elif len(all_entrances)==0:
                        print("\x1B[3mNo entrances exist for this sublevel. Please create a new one, otherwise the level will be unplayable.\x1B[0m")
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
                                    print("\x1B[3mEntrance number too high!\x1B[0m")
                                else:
                                    modified2=list(all_entrances[int(data)-1])
                                    all_entrances[int(data)-1]=tuple(modified)
                                    modified=modified2
                                    print("Successfully swapped Entrance "+warpNum+" and Entrance "+data)
                            except:
                                print("\x1B[3mEntrance number not an integer!\x1B[0m")
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
                print("\x1B[3mEntrances are an SMF2-only property. Please refer to Warps.\x1B[0m")
        elif toModify=="exits":
            if game=="smf2" or game=="smf2c":
                if toModifySub=="add":
                    all_exits.append(tuple(smf2WarpModifier("Exits","0","0","1","1")))
                elif warpNum!="":
                    if int(warpNum)>len(all_exits)-1:
                        print("\x1B[3mExit number too high!\x1B[0m")
                    elif len(all_exits)==0:
                        print("\x1B[3mNo exits exist for this sublevel. Please create a new one.\x1B[0m")
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
                print("\x1B[3mExits are an SMF2-only property. Please refer to Warps.\x1B[0m")
        elif toModify=="tiles":
            if tileReplacerValues[0]=="" and tileReplacerValues[1]!="":
                print("\x1B[3mBeginning of X range was not specified.\x1B[0m")
                return
            if tileReplacerValues[2]=="" and tileReplacerValues[3]!="":
                print("\x1B[3mBeginning of Y range was not specified.\x1B[0m")
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
                print("\x1B[3mX and Y ranges are not integers.\x1B[0m")
                return
            if tileReplacerValues[0]>tileReplacerValues[1]:
                print("\x1B[3mX range out of order - the beginning of the range should come first.\x1B[0m")
                return
            if tileReplacerValues[2]>tileReplacerValues[3]:
                if tileReplacerValues[3]==-1:
                    if game=="smf" or game=="smfe":
                        print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
                    elif game=="smf2" or game=="smf2c":
                        print("\x1B[3mSMF has no layers.\x1B[0m")
                else:
                    print("\x1B[3mY range out of order - the beginning of the range should come first.\x1B[0m")
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
                        print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
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
                        print("\x1B[3mSMF2 has no sublevel distinction.\x1B[0m")
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
                        print("\x1B[3mSMF has no layers.\x1B[0m")
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
                        print("\x1B[3mSMF has no layers.\x1B[0m")
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
        print("\x1B[3mNo level in memory!\x1B[0m")
        return

def awaitInput():
    while True:
        command=input("→ ")
        if command=="open" or command=="o":
            openFile("")
        elif command[:5]=="open ":
            openFile(command[5:])
        elif command[:2]=="o ":
            openFile(command[2:])
        elif command[:7]=="export ":
            exportAll(command[7:])
        elif command[:4]=="exp ":
            exportAll(command[4:])
        elif command[:2]=="e ":
            exportAll(command[2:])
        elif command[:7]=="import ":
            importTiles(command[7:])
        elif command[:6]=="import":
            importTiles("")
        elif command[:4]=="imp ":
            importTiles(command[4:])
        elif command[:2]=="i ":
            importTiles(command[2:])
        elif command[:1]=="i":
            importTiles(command[1:])
        elif command=="settings" or command=="set" or command=="s":
            changeConfig()
        elif command=="replace" or command=="rep":
            print("\x1B[3mNo data specified!\x1B[0m")
        elif command[:8]=="replace ":
            replace(command[8:])
        elif command[:4]=="rep ":
            replace(command[4:])
        elif command[:2]=="r ":
            replace(command[2:])
        elif command[:1]=="r":
            replace(command[1:])
        elif command=="header" or command=="head" or command=="h":
            printInfo()
        elif command[:5]=="help ":
            generalHelp(command[5:])
        elif command[:4]=="help":
            generalHelp("")
        elif command[:2]=="? ":
            generalHelp(command[2:])
        elif command[:1]=="?":
            generalHelp(command[1:])
        elif command[:4]=="exit" or command[:1]=="x":
            exit(0)
        else:
            print("\x1B[3mInvalid command!\x1B[0m")

configLoad()
if decorType!=0:
    title=" SMF Level Reader v"+versionNames[programVersion]+" "
    length=len(title)
    padding=(screenx-length)//2
    centered_text=decorTypes[decorType]*padding+"\033[1m"+title+"\033[0m"+decorTypes[decorType]*padding
    print(centered_text)
else:
    print("\033[1mSMF Level Reader v"+versionNames[programVersion]+"\033[0m")
print("Visit \u001b[36m\u001b[4mhttps://github.com/AeroPurple/SMFLevelReader\033[0m to report issues and download updates!")
time.sleep(titleScreenWaitTime/1000*16)
print("What would you like to do?")
awaitInput()