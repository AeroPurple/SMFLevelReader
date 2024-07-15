import tkinter as tk
from tkinter import filedialog
import os
from os import listdir
from os.path import dirname, basename, splitext, join
from struct import pack
import math
from multiprocessing.sharedctypes import Value
import traceback
import time
print("\033[1m"+"SMF Level Reader v0.8"+"\033[0m")
time.sleep(1)
print("Please open a Super Mario Flash level file.")

root = tk.Tk()
root.withdraw()

filePath=filedialog.askopenfilename()
if filePath=="":
    exit()
try:
    file=open(filePath,mode='r', encoding="utf-8")
    level_code=file.read()
except UnicodeDecodeError:
    print("\033[31m"+"invalid file\nconsider converting your level data to txt or csv"+"\033[0m")
    exit(1)

#print(level_code) # useful for debugging

counter=0
game=""
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
        level_raw=[]
        bonus=[]
        bonus_raw=[]
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
        level_warps=[]
        bonus_warps=[]
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
                        level_raw.append(current_tile)
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
        if level_name=="":
            level_name_print="\x1B[3m"+"None"+"\x1B[0m"
        else:
            level_name_print=level_name
        while True: # Background Number
            counter+=1
            if level_code[counter]!=",":
                level_background+=level_code[counter]
            else:
                break
        if level_background=="1":
            level_background_print="1 - Land"
        elif level_background=="2":
            level_background_print="2 - Cave"
        elif level_background=="3":
            level_background_print="3 - Forest"
        elif level_background=="4":
            level_background_print="4 - Castle"
        elif level_background=="5":
            level_background_print="5 - Snow"
        elif level_background=="6":
            level_background_print="6 - Ghost"
        else:
            game="smfe"
            if level_background=="7":
                level_background_print="7 - Hills"
            elif level_background=="8":
                level_background_print="8 - Snow 2"
            elif level_background=="9":
                level_background_print="9 - Rock"
            elif level_background=="10":
                level_background_print="10 - Castle 2"
            elif level_background=="11":
                level_background_print="11 - Ghost 2"
            elif level_background=="12":
                level_background_print="12 - Cave 2"
            elif level_background=="13":
                level_background_print="13 - Autumn"
            elif level_background=="14":
                level_background_print="14 - Night"
            elif level_background=="15":
                level_background_print="15 - Dark"
            elif level_background=="16":
                level_background_print="16 - Night 2"
            elif level_background=="17":
                level_background_print="17 - Land 2"
            elif level_background=="18":
                level_background_print="18 - Waterfall"
            elif level_background=="19":
                level_background_print="19 - Ruins"
            elif level_background=="20":
                level_background_print="20 - Sky"
            elif level_background=="21":
                level_background_print="21 - Mountain"
            elif level_background=="22":
                level_background_print="22 - Snow 3"
            elif level_background=="23":
                level_background_print="23 - Castle Walls"
            elif level_background=="24":
                level_background_print="24 - Castle 3"
            elif level_background=="25":
                level_background_print="25 - Castle 4"
            elif level_background=="26":
                level_background_print="26 - Desert"
            elif level_background=="27":
                level_background_print="27 - Volcano"
            elif level_background=="28":
                level_background_print="28 - Volcanic Cave"
            else:
                game="smf"
                level_background_print="\x1B[3m"+level_background+" - None"+"\x1B[0m"
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
        if level_music=="1":
            level_music_print="1 - Overworld"
        elif level_music=="2":
            level_music_print="2 - Forest"
        elif level_music=="3":
            level_music_print="3 - Athletic"
        elif level_music=="4":
            level_music_print="4 - Map"
        elif level_music=="5":
            level_music_print="5 - Underground"
        elif level_music=="6":
            level_music_print="6 - Fortress"
        elif level_music=="7":
            level_music_print="7 - Bowser"
        elif level_music=="8":
            level_music_print="8 - Toad Shop/Level Builder"
        elif level_music=="9":
            level_music_print="9 - Invincibile"
        elif level_music=="10":
            level_music_print="10 - Level Complete"
        elif level_music=="11":
            level_music_print="11 - World Complete"
        else:
            game="smfe"
            if level_music=="12":
                level_music_print="12 - Castle"
            elif level_music=="13":
                level_music_print="13 - Bonus"
            elif level_music=="14":
                level_music_print="14 - Final Bowser"
            elif level_music=="15":
                level_music_print="15 - Ghost House (SMW)"
            elif level_music=="16":
                level_music_print="16 - Ghost House (SMB)"
            elif level_music=="17":
                level_music_print="17 - Volcano"
            elif level_music=="18":
                level_music_print="18 - Airship"
            elif level_music=="19":
                level_music_print="19 - Desert"
            else:
                game="smf"
                level_music_print="\x1B[3m"+level_music+" - None"+"\x1B[0m"
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
                        bonus_raw.append(current_tile)
                        if current_tile!="":
                            if int(current_tile)>194:
                                game="smfe"
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
        if bonus_background=="1":
            bonus_background_print="1 - Land"
        elif bonus_background=="2":
            bonus_background_print="2 - Cave"
        elif bonus_background=="3":
            bonus_background_print="3 - Forest"
        elif bonus_background=="4":
            bonus_background_print="4 - Castle"
        elif bonus_background=="5":
            bonus_background_print="5 - Snow"
        elif bonus_background=="6":
            bonus_background_print="6 - Ghost"
        else:
            game="smfe"
            if bonus_background=="7":
                bonus_background_print="7 - Hills"
            elif bonus_background=="8":
                bonus_background_print="8 - Snow 2"
            elif bonus_background=="9":
                bonus_background_print="9 - Rock"
            elif bonus_background=="10":
                bonus_background_print="10 - Castle 2"
            elif bonus_background=="11":
                bonus_background_print="11 - Ghost 2"
            elif bonus_background=="12":
                bonus_background_print="12 - Cave 2"
            elif bonus_background=="13":
                bonus_background_print="13 - Autumn"
            elif bonus_background=="14":
                bonus_background_print="14 - Night"
            elif bonus_background=="15":
                bonus_background_print="15 - Dark"
            elif bonus_background=="16":
                bonus_background_print="16 - Night 2"
            elif bonus_background=="17":
                bonus_background_print="17 - Land 2"
            elif bonus_background=="18":
                bonus_background_print="18 - Waterfall"
            elif bonus_background=="19":
                bonus_background_print="19 - Ruins"
            elif bonus_background=="20":
                bonus_background_print="20 - Sky"
            elif bonus_background=="21":
                bonus_background_print="21 - Mountain"
            elif bonus_background=="22":
                bonus_background_print="22 - Snow 3"
            elif bonus_background=="23":
                bonus_background_print="23 - Castle Walls"
            elif bonus_background=="24":
                bonus_background_print="24 - Castle 3"
            elif bonus_background=="25":
                bonus_background_print="25 - Castle 4"
            elif bonus_background=="26":
                bonus_background_print="26 - Desert"
            elif bonus_background=="27":
                bonus_background_print="27 - Volcano"
            elif bonus_background=="28":
                bonus_background_print="28 - Volcanic Cave"
            else:
                if int(level_background)<7 or int(level_background)>28:
                    game="smf"
                bonus_background_print="\x1B[3m"+bonus_background+" - None"+"\x1B[0m"
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
        if bonus_music=="1":
            bonus_music_print="1 - Overworld"
        elif bonus_music=="2":
            bonus_music_print="2 - Forest"
        elif bonus_music=="3":
            bonus_music_print="3 - Athletic"
        elif bonus_music=="4":
            bonus_music_print="4 - Map"
        elif bonus_music=="5":
            bonus_music_print="5 - Underground"
        elif bonus_music=="6":
            bonus_music_print="6 - Fortress"
        elif bonus_music=="7":
            bonus_music_print="7 - Bowser"
        elif bonus_music=="8":
            bonus_music_print="8 - Toad Shop/Level Builder"
        elif bonus_music=="9":
            bonus_music_print="9 - Invincibile"
        elif bonus_music=="10":
            bonus_music_print="10 - Level Complete"
        elif bonus_music=="11":
            bonus_music_print="11 - World Complete"
        else:
            game="smfe"
            if bonus_music=="12":
                bonus_music_print="12 - Castle"
            elif bonus_music=="13":
                bonus_music_print="13 - Bonus"
            elif bonus_music=="14":
                bonus_music_print="14 - Final Bowser"
            elif bonus_music=="15":
                bonus_music_print="15 - Ghost House (SMW)"
            elif bonus_music=="16":
                bonus_music_print="16 - Ghost House (SMB)"
            elif bonus_music=="17":
                bonus_music_print="17 - Volcano"
            elif bonus_music=="18":
                bonus_music_print="18 - Airship"
            elif bonus_music=="19":
                bonus_music_print="19 - Desert"
            else:
                if int(level_music)<12 or int(level_music)>19:
                    game="smf"
                bonus_music_print="\x1B[3m"+bonus_music+" - None"+"\x1B[0m"
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
        
        if game=="smf":
            print("\033[1m"+"Game: "+"\033[0m"+"Super Mario Flash")
        elif game=="smfe":
            print("\033[1m"+"Game: "+"\033[0m"+"Super Mario Flash Ver. E")
        else:
            print("\033[31m"+"You messed with the source code, didn't you? "+"\033[0m")
        print("\033[1m"+"Level Name: "+"\033[0m"+level_name_print)
        print("\033[1m"+"Level Background: "+"\033[0m"+level_background_print)
        print("\033[1m"+"Level Music: "+"\033[0m"+level_music_print)
        if int(level_width)/20!=math.floor(int(level_width)/20) and (int(level_width)<320 or int(level_width)>4500):
            print("\033[1m"+"Level Width: "+"\033[0m"+level_width+" ("+"{:.0f}".format(int(level_width)/20)+" tiles, no right border, unintended size)")
        elif int(level_width)/20!=math.floor(int(level_width)/20):
            print("\033[1m"+"Level Width: "+"\033[0m"+level_width+" ("+"{:.0f}".format(int(level_width)/20)+" tiles, no right border)")
        elif (int(level_width)<320 or int(level_width)>4500):
            print("\033[1m"+"Level Width: "+"\033[0m"+level_width+" ("+"{:.0f}".format(int(level_width)/20)+" tiles, unintended size)")
        else:
            print("\033[1m"+"Level Width: "+"\033[0m"+level_width+" ("+"{:.0f}".format(int(level_width)/20)+" tiles)")
        print("\033[1m"+"Bonus Background: "+"\033[0m"+bonus_background_print)
        print("\033[1m"+"Bonus Music: "+"\033[0m"+bonus_music_print)
        if int(bonus_width)/20!=math.floor(int(bonus_width)/20) and (int(bonus_width)<320 or int(bonus_width)>4500):
            print("\033[1m"+"Bonus Width: "+"\033[0m"+bonus_width+" ("+"{:.0f}".format(int(bonus_width)/20)+" tiles, no right border, unintended size)")
        elif int(bonus_width)/20!=math.floor(int(bonus_width)/20):
            print("\033[1m"+"Bonus Width: "+"\033[0m"+bonus_width+" ("+"{:.0f}".format(int(bonus_width)/20)+" tiles, no right border)")
        elif (int(bonus_width)<320 or int(bonus_width)>4500):
            print("\033[1m"+"Bonus Width: "+"\033[0m"+bonus_width+" ("+"{:.0f}".format(int(bonus_width)/20)+" tiles, unintended size)")
        else:
            print("\033[1m"+"Bonus Width: "+"\033[0m"+bonus_width+" ("+"{:.0f}".format(int(bonus_width)/20)+" tiles)")    
        print("\033[1m"+"Start Point: "+"\033[0m"+start_at+" @ xPos "+start_xpos+" yPos "+start_ypos+" ("+str(int(start_xpos)/20)+" tiles horz, "+str(int(start_ypos)/20)+" tiles vert)")
        print("\033[1m"+"Level Warps:"+"\033[0m")
        for i in range(len(level_warps)):
            if level_warps[i][2]=="Level" or level_warps[i][2]=="Bonus":
                warp_end_sublevel_print=level_warps[i][2]
            else:
                warp_end_sublevel_print=level_warps[i][2]+" (invalid, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            if level_warps[i][5]=="right" or level_warps[i][5]=="left":
                warp_end_direction_print="facing "+level_warps[i][5]
            else:
                warp_end_direction_print="\x1B[3m"+"glitchy entrance ("+level_warps[i][5]+")"+"\x1B[0m"
            if level_warps[i][6]=="Up" or level_warps[i][6]=="Down" or level_warps[i][6]=="Left" or level_warps[i][6]=="Right":
                warp_end_type_print="Pipe "+level_warps[i][6]+" Animation"
            elif level_warps[i][6]=="Appear":
                warp_end_type_print="No Animation"
            else:
                warp_end_type_print="\x1B[3m"+"invalid animation \""+level_warps[i][6]+"\""+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            warp_print="\tWarp from xPos "+str(int(level_warps[i][1])*20)+" yPos "+str(int(level_warps[i][0])*20)+" to xPos "+level_warps[i][3]+" yPos "+level_warps[i][4]+" in "+warp_end_sublevel_print+", "+warp_end_direction_print+", "+warp_end_type_print
            
            print(warp_print)
        if level_warps==[]:
            warp_print="\x1B[3m"+"\tNone"+"\x1B[0m"
            print(warp_print)
        print("\033[1m"+"Bonus Warps:"+"\033[0m")
        for i in range(len(bonus_warps)):
            if bonus_warps[i][2]=="Level" or bonus_warps[i][2]=="Bonus":
                warp_end_sublevel_print=bonus_warps[i][2]
            else:
                warp_end_sublevel_print=bonus_warps[i][2]+" (invalid, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            if bonus_warps[i][5]=="right" or bonus_warps[i][5]=="left":
                warp_end_direction_print="facing "+bonus_warps[i][5]
            else:
                warp_end_direction_print="\x1B[3m"+"glitchy entrance ("+bonus_warps[i][5]+")"+"\x1B[0m"
            if bonus_warps[i][6]=="Up" or bonus_warps[i][6]=="Down" or bonus_warps[i][6]=="Left" or bonus_warps[i][6]=="Right":
                warp_end_type_print="Pipe "+bonus_warps[i][6]+" Animation"
            elif bonus_warps[i][6]=="Appear":
                warp_end_type_print="No Animation"
            else:
                warp_end_type_print="\x1B[3m"+"invalid animation \""+bonus_warps[i][6]+"\""+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            warp_print="\tWarp from xPos "+str(int(bonus_warps[i][1])*20)+" yPos "+str(int(bonus_warps[i][0])*20)+" to xPos "+level_warps[i][3]+" yPos "+level_warps[i][4]+" in "+warp_end_sublevel_print+", "+warp_end_direction_print+", "+warp_end_type_print
            
            print(warp_print)
        if bonus_warps==[]:
            warp_print="\x1B[3m"+"\tNone"+"\x1B[0m"
            print(warp_print)
        
        export=input("\nWould you like to export the level data as a CSV and TXT files? (Y/N): ")
        if export.lower()=="y":
            filePath=filedialog.askdirectory()
            if filePath=="":
                exit()
            output="SMFDATA\nname=\""+level_name+"\"\nlvlbg="+level_background+"\nlvlmusic="+level_music+"\nlvlwidth="+level_width+"\nbnsbg="+bonus_background+"\nbnsmusic="+bonus_music+"\nbnswidth="+bonus_width+"\n\nstart("+start_xpos+","+start_ypos+") @ "+start_at
            print("Gathering level header data...")
            file=open(str(filePath+"/"+level_name+"_header.txt"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            output="SMFWARPS"
            print("Processing warp data...")
            for i in range(len(level_warps)):
                output+="\nfrom("+level_warps[i][1]+","+level_warps[i][0]+")levelto("+level_warps[i][3]+","+level_warps[i][4]+")in"+level_warps[i][2]+",facing\""+level_warps[i][5]+"\",anim\""+level_warps[i][6]+"\""
            for i in range(len(bonus_warps)):
                output+="\nfrom("+bonus_warps[i][1]+","+bonus_warps[i][0]+")bonusto("+bonus_warps[i][3]+","+bonus_warps[i][4]+")in"+bonus_warps[i][2]+",facing\""+bonus_warps[i][5]+"\",anim\""+bonus_warps[i][6]+"\""
            file=open(str(filePath+"/"+level_name+"_warps.txt"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            output=""
            print("Processing Level tiles...")
            for i in level:
                for j in i:
                    output+=j+","
                output+="\n"
            file=open(str(filePath+"/"+level_name+"_level.csv"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            output=""
            print("Processing Bonus tiles...")
            for i in bonus:
                for j in i:
                    output+=j+","
                output+="\n"
            file=open(str(filePath+"/"+level_name+"_bonus.csv"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            print("Success!")
        else:
            exit()
    except IndexError as e:
        errorString=str(e)+" occured on line "+str(e.__traceback__.tb_lineno)
        if level==[]:
            errorString="file contains no level tile data"
        elif e.__traceback__.tb_lineno==68:
            errorString="unexpected level tile data size"
        elif bonus==[]:
            errorString="file contains no bonus tile data"
        elif e.__traceback__.tb_lineno==246:
            errorString="unexpected bonus tile data size"
        print("\033[31m"+"invalid or incomplete level code\n"+errorString+"\033[0m")
        exit(1)
    except ValueError as e:
        errorString=str(e)+" occured on line "+str(e.__traceback__.tb_lineno)
        if e.__traceback__.tb_lineno==75:
            errorString="tile #"+str(tiles_processed)+" in level tile data is not an integer - returned \""+current_tile+"\""
        elif e.__traceback__.tb_lineno==253:
            errorString="tile #"+str(tiles_processed)+" in bonus tile data is not an integer - returned \""+current_tile+"\""
        print("\033[31m"+"invalid tile data\n"+errorString+"\033[0m")
        exit(1)
        

elif game=="smf2":
    try:
        level_name=""
        level_description=""
        level_author=""
        level_message=""
        level_background=""
        level_url1=""
        level_bg_url2=""
        level_music=""
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
        entrance_type=""
        entrance_x=""
        entrance_y=""
        entrance_mario_status=""
        oneentrance=[]
        all_entrances=[]
        exit_x=""
        exit_y=""
        exit_type=""
        exit_link_to=""
        oneexit=[]
        all_exits=[]
        layer_1=[]
        layer_1_raw=[]
        layer_2=[]
        layer_2_raw=[]
        current_row=[]
        tiles_processed=0
        while True: # Level Name
            counter+=1
            if level_code[counter]!="&":
                level_name+=level_code[counter]
            else:
                break
        if level_name=="":
            level_name_print="\x1B[3m"+"None"+"\x1B[0m"
        else:
            level_name_print=level_name
        while True: # Level Description
            counter+=1
            if level_code[counter]!="&":
                level_description+=level_code[counter]
            else:
                break
        if level_description=="":
            level_description_print="\x1B[3m"+"None"+"\x1B[0m"
        else:
            level_description_print=level_description
        while True: # Level Author
            counter+=1
            if level_code[counter]!="&":
                level_author+=level_code[counter]
            else:
                break
        if level_author=="":
            level_author_print="\x1B[3m"+"None"+"\x1B[0m"
        else:
            level_author_print=level_author
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
            level_url1_print=level_url1
            level_bg_url2_print=level_bg_url2
        while True: # Background Number
            if level_code[counter]=="&":
                counter+=1
            if level_code[counter]!=",":
                level_background+=level_code[counter]
                counter+=1
            else:
                break
        if level_background=="1":
            level_background_print="1 - Clouds (Light Green)"
        elif level_background=="2":
            level_background_print="2 - Mint Hills (Light Orange)"
        elif level_background=="3":
            level_background_print="3 - Forest (Black)"
        elif level_background=="4":
            level_background_print="4 - Ghost House"
        elif level_background=="5":
            level_background_print="5 - Underground"
        elif level_background=="6":
            level_background_print="6 - Underwater (Blue)"
        elif level_background=="7":
            level_background_print="7 - Castle (Gray)"
        elif level_background=="8":
               level_background_print="8 - Bonus (Blue)"
        elif level_background=="9":
            level_background_print="9 - Night (Blue)"
        elif level_background=="11":
            level_background_print="11 - Custom"
        else:
            if int(level_background)>11:
                game="smf2c"
                if level_background=="12":
                    level_background_print="12 - Blue Hills (Blue)"
                elif level_background=="19":
                    level_background_print="19 - Clouds (Light Orange)"
                elif level_background=="20":
                    level_background_print="20 - Clouds (Light Blue)"
                elif level_background=="21":
                    level_background_print="21 - Clouds (Blue)"
                elif level_background=="22":
                    level_background_print="22 - Clouds (Dark)"
                elif level_background=="23":
                    level_background_print="23 - Mint Hills (Light Green)"
                elif level_background=="24":
                    level_background_print="24 - Mint Hills (Light Blue)"
                elif level_background=="25":
                    level_background_print="25 - Mint Hills (Blue)"
                elif level_background=="26":
                    level_background_print="26 - Mint Hills (Dark)"
                elif level_background=="27":
                    level_background_print="27 - Gray Hills (Light Orange)"
                elif level_background=="28":
                    level_background_print="28 - Gray Hills (Light Green)"
                elif level_background=="29":
                    level_background_print="29 - Gray Hills (Light Blue)"
                elif level_background=="30":
                    level_background_print="30 - Gray Hills (Blue)"
                elif level_background=="31":
                    level_background_print="31 - Gray Hills (Dark)"
                elif level_background=="32":
                    level_background_print="32 - Black Hills (Light Orange)"
                elif level_background=="33":
                    level_background_print="33 - Black Hills (Light Green)"
                elif level_background=="34":
                    level_background_print="34 - Black Hills (Light Blue)"
                elif level_background=="35":
                    level_background_print="35 - Black Hills (Blue)"
                elif level_background=="36":
                    level_background_print="36 - Black Hills (Dark)"
                elif level_background=="37":
                    level_background_print="37 - Green Hills (Light Orange)"
                elif level_background=="38":
                    level_background_print="38 - Green Hills (Light Green)"
                elif level_background=="39":
                    level_background_print="39 - Green Hills (Light Blue)"
                elif level_background=="40":
                    level_background_print="40 - Green Hills (Blue)"
                elif level_background=="41":
                    level_background_print="41 - Green Hills (Dark)"
                elif level_background=="53":
                    level_background_print="53 - Blue Hills (Light Orange)"
                elif level_background=="54":
                    level_background_print="54 - Blue Hills (Light Green)"
                elif level_background=="55":
                    level_background_print="55 - Blue Hills (Light Blue)"
                elif level_background=="56":
                    level_background_print="56 - Blue Hills (Dark)"
                elif level_background=="132":
                    level_background_print="132 - Mint Tall Hills (Light Orange)"
                elif level_background=="133":
                    level_background_print="133 - Mint Tall Hills (Light Green)"
                elif level_background=="134":
                    level_background_print="134 - Mint Tall Hills (Light Blue)"
                elif level_background=="135":
                    level_background_print="135 - Mint Tall Hills (Blue)"
                elif level_background=="136":
                    level_background_print="136 - Mint Tall Hills (Dark)"
                elif level_background=="137":
                    level_background_print="137 - Gray Tall Hills (Light Orange)"
                elif level_background=="138":
                    level_background_print="138 - Gray Tall Hills (Light Green)"
                elif level_background=="139":
                    level_background_print="139 - Gray Tall Hills (Light Blue)"
                elif level_background=="140":
                    level_background_print="140 - Gray Tall Hills (Blue)"
                elif level_background=="141":
                    level_background_print="141 - Gray Tall Hills (Dark)"
                elif level_background=="142":
                    level_background_print="142 - Black Tall Hills (Light Orange)"
                elif level_background=="143":
                    level_background_print="143 - Black Tall Hills (Light Green)"
                elif level_background=="144":
                    level_background_print="144 - Black Tall Hills (Light Blue)"
                elif level_background=="145":
                    level_background_print="145 - Black Tall Hills (Blue)"
                elif level_background=="146":
                    level_background_print="146 - Black Tall Hills (Dark)"
                elif level_background=="147":
                    level_background_print="147 - Green Tall Hills (Light Orange)"
                elif level_background=="148":
                    level_background_print="148 - Green Tall Hills (Light Green)"
                elif level_background=="149":
                    level_background_print="149 - Green Tall Hills (Light Blue)"
                elif level_background=="150":
                    level_background_print="150 - Green Tall Hills (Blue)"
                elif level_background=="151":
                    level_background_print="151 - Green Tall Hills (Dark)"
                else:
                    game="smf2"
                    level_background_print="\x1B[3m"+level_background+" - None"+"\x1B[0m"
            else:
                level_background_print="\x1B[3m"+level_background+" - None"+"\x1B[0m"
        while True: # Music Number
            counter+=1
            if level_code[counter]!=",":
                level_music+=level_code[counter]
            else:
                break
        if level_music=="1":
            level_music_print="1 - Overworld"
        elif level_music=="2":
            level_music_print="2 - Athletic"
        elif level_music=="3":
            level_music_print="3 - Castle"
        elif level_music=="4":
            level_music_print="4 - Underground"
        elif level_music=="5":
            level_music_print="5 - Underwater"
        elif level_music=="6":
            level_music_print="6 - Ghost House"
        elif level_music=="7":
            level_music_print="7 - Airship"
        elif level_music=="8":
            level_music_print="8 - Bonus"
        elif level_music=="9":
            level_music_print="9 - Bowser"
        elif level_music=="10":
            level_music_print="10 - Invincibile"
        elif level_music=="11":
            level_music_print="11 - P-Switch"
        elif level_music=="12":
            level_music_print="12 - Goal 1 Fanfare"
        elif level_music=="13":
            level_music_print="13 - Goal 2 Fanfare"
        elif level_music=="14":
            level_music_print="14 - Player Down"
        elif level_music=="15":
            level_music_print="15 - Boom Boom"
        elif level_music=="16":
            level_music_print="16 - World Map 1"
        elif level_music=="17":
            level_music_print="17 - World Map 2"
        elif level_music=="18":
            level_music_print="18 - Key Exit"
        elif level_music=="19":
            game="smf2c"
            level_music_print="19 - Custom"
        else:
            level_music_print="\x1B[3m"+level_music+" - None"+"\x1B[0m"
        while True: # Mario's State
            counter+=1
            if level_code[counter]!=",":
                level_powerup+=level_code[counter]
            else:
                break
        if level_powerup=="0":
            level_powerup_print="0 - Small Mario"
        elif level_powerup=="1":
            level_powerup_print="1 - Big Mario"
        elif level_powerup=="2":
            level_powerup_print="2 - Fire Mario"
        elif level_powerup=="3":
            level_powerup_print="3 - Cape Mario"
        elif level_powerup=="4":
            level_powerup_print="4 - Frictionless Cape Mario (unintended)"
        elif level_powerup=="5":
            level_powerup_print="5 - Fragile Yoshi-Riding Small Mario (unintended)"
        elif level_powerup=="6":
            level_powerup_print="6 - Fragile Yoshi-Riding Big Mario (unintended)"
        elif level_powerup=="7":
            level_powerup_print="7 - Fragile Yoshi-Riding Fire Mario (unintended)"
        elif level_powerup=="8":
            level_powerup_print="8 - Fragile Yoshi-Riding Cape Mario (unintended)"
        elif level_powerup=="9":
            level_powerup_print="9 - Door-Entering Mario (unintended, "+"\033[31m"+"crashes the game"+"\033[0m"+")"
        elif level_powerup=="10":
            level_powerup_print="10 - Vine-Climbing Small Mario (unintended)"
        elif level_powerup=="11":
            level_powerup_print="11 - Vine-Climbing Big Mario (unintended)"
        elif level_powerup=="12":
            level_powerup_print="12 - Vine-Climbing Fire Mario (unintended)"
        elif level_powerup=="13":
            level_powerup_print="13 - Vine-Climbing Cape Mario (unintended)"
        elif level_powerup=="15":
            level_powerup_print="15 - Carrying Small Mario (unintended)"
        elif level_powerup=="16":
            level_powerup_print="16 - Carrying Big Mario (unintended)"
        elif level_powerup=="17":
            level_powerup_print="17 - Carrying Fire Mario (unintended)"
        elif level_powerup=="18":
            level_powerup_print="18 - Carrying Cape Mario (unintended)"
        elif level_powerup=="25":
            level_powerup_print="25 - Swimming Small Mario"
        elif level_powerup=="26":
            level_powerup_print="26 - Swimming Big Mario"
        elif level_powerup=="27":
            level_powerup_print="27 - Swimming Fire Mario"
        elif level_powerup=="28":
            level_powerup_print="28 - Swimming Cape Mario"
        else:
            level_powerup_print="\x1B[3m"+level_powerup+" - No Mario (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"+"\x1B[0m"
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
        if level_layer_priority=="0":
            level_layer_priority_print="0 - Disabled Level Tiles and Music (unintended)"
        elif level_layer_priority=="1":
            level_layer_priority_print="1 - Disabled Background (unintended)"
        elif level_layer_priority=="2":
            level_layer_priority_print="2 - Disabled Level Tiles (unintended)"
        elif level_layer_priority=="3":
            level_layer_priority_print="3 - Default"
        elif level_layer_priority=="4":
            level_layer_priority_print="4 - Disabled Level Tiles (unintended)"
        else:
            level_layer_priority_print=level_layer_priority+" - HUD Hidden Behind Tiles (unintended)"
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
        if level_layer_priority_2=="0":
            level_layer_priority_2_print="0 - Disabled Level Tiles + Glitchy Death Animation (unintended)"
        elif level_layer_priority_2=="1":
            level_layer_priority_2_print="1 - Disabled Background (unintended)"
        elif level_layer_priority_2=="2":
            level_layer_priority_2_print="2 - Default"
        elif level_layer_priority_2=="3":
            level_layer_priority_2_print="3 - Disabled Level Tiles (unintended)"
        else:
            level_layer_priority_2_print=level_layer_priority_2+" - Default (unintended variable range)"
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
        counter+=1
        current_tile=""
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
                        layer_1_raw.append(current_tile)
                        if current_tile!="":
                            if int(current_tile)>406:
                                game="smf2c"
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
                        layer_2_raw.append(current_tile)
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

        if game=="smf2":
            print("\033[1m"+"Game: "+"\033[0m"+"Super Mario Flash 2")
        elif game=="smf2c":
            print("\033[1m"+"Game: "+"\033[0m"+"Super Mario Flash 2 Ver. C")
        else:
            print("\033[31m"+"You messed with the source code, didn't you? "+"\033[0m")
        print("\033[1m"+"Level Name: "+"\033[0m"+level_name_print)
        print("\033[1m"+"Description: "+"\033[0m"+level_description_print)
        print("\033[1m"+"Author: "+"\033[0m"+level_author_print)
        if level_message=="":
            print("\033[1m"+"Message Block Text: "+"\033[0m"+"\x1B[3m"+"None"+"\x1B[0m")
        else:
            print("\033[1m"+"Message Block Text: «"+"\033[0m"+level_message+"\033[1m"+"»"+"\033[0m")
        print("\033[1m"+"Background: "+"\033[0m"+level_background_print)
        if level_background=="11":
            print("\033[1m"+"Background URL 1: "+"\033[0m"+level_url1) if level_url1!="" else print("\033[1m"+"Background URL 1: "+"\033[0m"+"\x1B[3m"+"None"+"\x1B[0m")
            print("\033[1m"+"Background URL 2: "+"\033[0m"+level_bg_url2) if level_bg_url2!="" else print("\033[1m"+"Background URL 2: "+"\033[0m"+"\x1B[3m"+"None"+"\x1B[0m")
        print("\033[1m"+"Music: "+"\033[0m"+level_music_print)
        print("\033[1m"+"Mario's State: "+"\033[0m"+level_powerup_print)
        print("\033[1m"+"Level Dimensions: "+"\033[0m"+level_width+"x"+level_height+" ("+str(int(level_height)/20)+" Rows by "+str(int(level_width)/20)+" Columns)")
        print("\033[1m"+"Unknown Variable="+"\033[0m"+level_variable_1)
        print("\033[1m"+"Unknown Variable="+"\033[0m"+level_variable_2)
        print("\033[1m"+"Layer Priority Variable: "+"\033[0m"+level_layer_priority_print)
        print("\033[1m"+"Layer 2 Dimensions: "+"\033[0m"+level_layer2_width+"x"+level_layer2_height+" ("+str(int(level_layer2_height)/20)+" Rows by "+str(int(level_layer2_width)/20)+" Columns)")
        print("\033[1m"+"Layer 2 X Offset: "+"\033[0m"+level_layer2_xpos)
        print("\033[1m"+"Layer 2 Y Offset: "+"\033[0m"+level_layer2_ypos)
        print("\033[1m"+"Layer Priority Variable: "+"\033[0m"+level_layer_priority_2_print)
        print("\033[1m"+"Unknown Variable="+"\033[0m"+level_variable_3)
        print("\033[1m"+"Entrances:"+"\033[0m")
        for i in range(len(all_entrances)):
            if i==0:
                entrance_print="\t"+"\033[1m"+"ID "+str(i+1)+" (Starting Point):"+"\033[0m"+" "
            else:
                entrance_print="\t"+"\033[1m"+"ID "+str(i+1)+":"+"\033[0m"+" "
            if all_entrances[i][0]=="0":
                entrance_type_print="Standard Entrance"
            elif all_entrances[i][0]=="1":
                entrance_type_print="Repeating Door Animation (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            elif all_entrances[i][0]=="2":
                entrance_type_print="Upward Pipe Entrance"
            elif all_entrances[i][0]=="3":
                entrance_type_print="Downward Pipe Entrance"
            elif all_entrances[i][0]=="4":
                entrance_type_print="Repeating Downward Pipe Animation (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            elif all_entrances[i][0]=="5":
                entrance_type_print="Repeating Upward Pipe Animation (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            elif all_entrances[i][0]=="6":
                entrance_type_print="Pipe Entrance Right"
            elif all_entrances[i][0]=="7":
                entrance_type_print="Pipe Entrance Left"
            elif all_entrances[i][0]=="8":
                entrance_type_print="Repeating Pipe Left Animation (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            elif all_entrances[i][0]=="9":
                entrance_type_print="Repeating Pipe Right Animation (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            else:
                entrance_type_print="No Mario (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"

            if all_entrances[i][3]=="0":
                entrance_mario_status_print="No Mario (unintended, "+"\033[33m"+"softlocks the game"+"\033[0m"+")"
            elif all_entrances[i][3]=="1":
                entrance_mario_status_print="Facing Right"
            elif all_entrances[i][3]=="2":
                entrance_mario_status_print="Facing Left"
            elif all_entrances[i][3]=="3":
                entrance_mario_status_print="Running Right (unintended)"
            elif all_entrances[i][3]=="4":
                entrance_mario_status_print="Running Left (unintended)"
            elif all_entrances[i][3]=="5":
                entrance_mario_status_print="Skidding Right (unintended)"
            elif all_entrances[i][3]=="6":
                entrance_mario_status_print="Skidding Left (unintended)"
            elif all_entrances[i][3]=="7":
                entrance_mario_status_print="Jumping Right (unintended)"
            elif all_entrances[i][3]=="8":
                entrance_mario_status_print="Jumping Left (unintended)"
            elif all_entrances[i][3]=="9":
                entrance_mario_status_print="Falling Right (unintended)"
            elif all_entrances[i][3]=="10":
                entrance_mario_status_print="Falling Left (unintended)"
            elif all_entrances[i][3]=="11":
                entrance_mario_status_print="Crouching Right (unintended)"
            elif all_entrances[i][3]=="12":
                entrance_mario_status_print="Crouching Left (unintended)"
            elif all_entrances[i][3]=="13":
                entrance_mario_status_print="Sliding Right (unintended)"
            elif all_entrances[i][3]=="14":
                entrance_mario_status_print="Sliding Left (unintended)"
            elif all_entrances[i][3]=="15":
                entrance_mario_status_print="Kicking Right (unintended)"
            else:
                if all_entrances[i][3].isdigit():
                    if int(all_entrances[i][3])>0:
                        entrance_mario_status_print="Kicking Left (unintended)"
                    else:
                        entrance_mario_status_print="Superposition Mario (unintended)"
                else:
                    entrance_mario_status_print="Superposition Mario (unintended)"
            entrance_print=entrance_print+entrance_type_print+" ["+all_entrances[i][0]+"], "+entrance_mario_status_print+" ["+all_entrances[i][3]+"] @ xPos "+all_entrances[i][1]+" yPos "+all_entrances[i][2]+" ("+str(int(all_entrances[i][1])/20)+" tiles horz, "+str(int(all_entrances[i][2])/20)+" tiles vert)"

            print(entrance_print)
        print("\033[1m"+"Exits:"+"\033[0m")
        exit_print=""
        for i in range(len(all_exits)):
            exit_print="\t"
            if all_exits[i][2]=="1":
                exit_type_print="Door"
            elif all_exits[i][2]=="2":
                exit_type_print="P-Switch Door"
            elif all_exits[i][2]=="3":
                exit_type_print="Downward Pipe"
            elif all_exits[i][2]=="4":
                exit_type_print="Upward Pipe"
            elif all_exits[i][2]=="5":
                exit_type_print="Pipe Right"
            elif all_exits[i][2]=="6":
                exit_type_print="Pipe Left"
            else:
                exit_type_print="Invalid"

            exit_print=exit_print+exit_type_print+" ["+all_exits[i][2]+"] to "+"\033[1m"+"ID "+str(int(all_exits[i][3])+1)+"\033[0m"+" @ xPos "+str(int(all_exits[i][0])*20)+" yPos "+str(int(all_exits[i][1])*20)+" ("+all_exits[i][0]+" tiles horz, "+all_exits[i][1]+" tiles vert)"
            print(exit_print)
            
        if exit_print=="":
            print("\x1B[3m"+"\tNone"+"\x1B[0m")
            
        export=input("\nWould you like to export the level data as a CSV and TXT files? (Y/N): ")
        if export.lower()=="y":
            filePath=filedialog.askdirectory()
            if filePath=="":
                exit()
            output="SMF2DATA\nname=\""+level_name+"\"\ndescription=\""+level_description+"\"\nauthor=\""+level_author+"\"\nmessage=\""+level_message+"\"\n\nbg="+level_background+"\nurl1=\""+level_url1+"\"\nurl2=\""+level_bg_url2+"\"\nmusic="+level_music+"\nstartstatus="+level_powerup+"\nlayerpriority1="+level_layer_priority+"\nlayerpriority2="+level_layer_priority_2+"\nlayer2xpos="+level_layer2_xpos+"\nlayer2ypos="+level_layer2_ypos+"\nvar1="+level_variable_1+"\nvar2="+level_variable_2+"\nvar3="+level_variable_3
            print("Gathering level header data...")
            file=open(str(filePath+"/"+level_name+"_header.txt"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            output="SMF2WARPS"
            print("Processing warp data...")
            for i in range(len(all_entrances)):
                output+="\nentrance"+str(i+1)+"[x:"+all_entrances[i][1]+",y:"+all_entrances[i][2]+",anim:"+all_entrances[i][0]+",status:"+all_entrances[i][3]+"]"
            output+="\n"
            for i in range(len(all_exits)):
                output+="\nexit[x:"+all_exits[i][0]+",y:"+all_exits[i][1]+",type:"+all_exits[i][2]+",to:"+all_exits[i][3]+"]"
            file=open(str(filePath+"/"+level_name+"_warps.txt"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            output=""
            tiles_read=0
            for i in layer_1:
                for j in i:
                    print("Processed "+str(tiles_read)+"/"+str(int((int(level_height)/20)*(int(level_width)/20)))+" Layer 1 tiles ("+str(math.floor(tiles_read/((int(level_height)/20)*(int(level_width)/20))*100))+"% done)", end='\r')
                    output+=j+","
                    tiles_read+=1
                output+="\n"
            print("Processed all "+str(tiles_read)+" tiles in Layer 1.            ")
            file=open(str(filePath+"/"+level_name+"_layer1.csv"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            output=""
            tiles_read=0
            for i in layer_2:
                for j in i:
                    print("Processed "+str(tiles_read)+"/"+str(int((int(level_layer2_height)/20)*(int(level_layer2_width)/20)))+" Layer 2 tiles ("+str(math.floor(tiles_read/((int(level_layer2_height)/20)*(int(level_layer2_width)/20))*100))+"% done)", end='\r')
                    output+=j+","
                    tiles_read+=1
                output+="\n"
            print("Processed all "+str(tiles_read)+" tiles in Layer 2.            ")
            file=open(str(filePath+"/"+level_name+"_layer2.csv"),mode='w', encoding="utf-8")
            file.write(output)
            file.close()
            print("Success!")
        else:
            exit()
    except Exception as e:
        print("\033[31m"+"exception encountered during parsing\ndata dump:\n\nlevel_name: "+level_name+"\nlevel_description: "+level_description+"\nlevel_author: "+level_author+"\nlevel_message: "+level_message+"\nlevel_background: "+level_background+"\nlevel_url1: "+level_url1+"\nlevel_bg_url2: "+level_bg_url2+"\nlevel_music: "+level_music+"\nlevel_powerup: "+level_powerup+"\nlevel_width: "+level_width+"\nlevel_height: "+level_height+"\nlevel_variable_1: "+level_variable_1+"\nlevel_variable_2: "+level_variable_2+"\nlevel_layer_priority: "+level_layer_priority+"\nlevel_layer2_width: "+level_layer2_width+"\nlevel_layer2_height: "+level_layer2_height+"\nlevel_layer2_xpos: "+level_layer2_xpos+"\nlevel_layer2_ypos: "+level_layer2_ypos+"\nlevel_layer_priority_2: "+level_layer_priority_2+"\nlevel_variable_3: "+level_variable_3+"\noneentrance: "+str(oneentrance)+"\nall_entrances: "+str(all_entrances)+"\noneexit: "+str(oneexit)+"\nall_exits: "+str(all_exits)+"\nlayer_1: "+str(layer_1)+"\nlayer_2: "+str(layer_2)+"\ncurrent_row: "+str(current_row)+"\ntiles_processed: "+str(tiles_processed)+"\n\n"+str(e)+" occured on line "+str(e.__traceback__.tb_lineno)+"\033[0m")
        exit(1)
	
else:
    print("\033[31m"+"invalid level code\nno valid delimiters found in file"+"\033[0m")
    exit(1)