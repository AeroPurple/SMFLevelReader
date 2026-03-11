import sys

tick="√"
try:
    tick.encode(sys.stdout.encoding)
except UnicodeEncodeError as e:
    tick="v"

ANSICodes={
    0:["","","","","","","","","","","","","","","","","","","","","(X) ERROR: ","/!\\ WARNING: ",f"[{tick}] SUCCESS: ","/!\\ TYPEERROR: "],
    1:["\033[0m","\033[1m","\x1B[3m","\x1B[4m","\033[30m","\033[31m","\033[32m","\033[33m","\033[34m","\033[35m","\033[36m","\033[37m","\033[90m","\033[91m","\033[92m","\033[93m","\033[94m","\033[95m","\033[96m","\033[97m","","","",""]
}

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
    "id":"",
    "sublevel":"",
    "lo_x":"",
    "hi_x":"",
    "lo_y":"",
    "hi_y":"",
    "value":"",
    "typeinvalid":""
}

def defineColors(useANSI):
    global colorScheme
    
    DEFAULT=ANSICodes[useANSI][0]
    BOLD=ANSICodes[useANSI][1]
    ITALIC=ANSICodes[useANSI][2]
    UNDERLINE=ANSICodes[useANSI][3]
    DIM_BLACK=ANSICodes[useANSI][4]
    DIM_RED=ANSICodes[useANSI][5]
    DIM_GREEN=ANSICodes[useANSI][6]
    DIM_YELLOW=ANSICodes[useANSI][7]
    DIM_BLUE=ANSICodes[useANSI][8]
    DIM_MAGENTA=ANSICodes[useANSI][9]
    DIM_CYAN=ANSICodes[useANSI][10]
    DIM_WHITE=ANSICodes[useANSI][11]
    BLACK=ANSICodes[useANSI][12]
    RED=ANSICodes[useANSI][13]
    GREEN=ANSICodes[useANSI][14]
    YELLOW=ANSICodes[useANSI][15]
    BLUE=ANSICodes[useANSI][16]
    MAGENTA=ANSICodes[useANSI][17]
    CYAN=ANSICodes[useANSI][18]
    WHITE=ANSICodes[useANSI][19]
    ERROR_TEXT=ANSICodes[useANSI][20]
    WARN_TEXT=ANSICodes[useANSI][21]
    SUCCESS_TEXT=ANSICodes[useANSI][22]
    TE_TEXT=ANSICodes[useANSI][23]

    return {
        "default":DEFAULT,
        "bold":BOLD,
        "error":RED+ERROR_TEXT, # used to be DIM_RED
        "warning":YELLOW+WARN_TEXT, # used to be DIM_YELLOW
        "success":GREEN+SUCCESS_TEXT,
        "link":BLUE+UNDERLINE, # used to be DIM_CYAN
        "null":BLACK, # used to be ITALIC
        "typeerror":DIM_YELLOW+TE_TEXT, # used to be ITALIC
        "command":YELLOW,
        "subcommand":WHITE, # used to be DEFAULT+BOLD
        "section":DEFAULT,
        "id":GREEN,
        "sublevel":DIM_GREEN,
        "lo_x":DIM_BLUE,
        "hi_x":BLUE,
        "lo_y":DIM_MAGENTA,
        "hi_y":MAGENTA,
        "value":CYAN,
        "typeinvalid":DIM_RED,
        "newline":MAGENTA
    }