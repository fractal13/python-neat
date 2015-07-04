DEBUG_ERROR = 1
DEBUG_ALGO = 4
DEBUG_FILEINPUT = 8
DEBUG_INTEGRITY = 16

g_header = { DEBUG_ERROR: "ERR",
             DEBUG_ALGO: "ALG",
             DEBUG_FILEINPUT: "FIO",
             DEBUG_INTEGRITY: "ING",
             }

debug_level = (0 | \
#               DEBUG_ERROR | \
#               DEBUG_ALGO | \
#               DEBUG_FILEINPUT | \
#               DEBUG_INTEGRITY | \
               0 )

import inspect

def is_set(level):
    return (debug_level & level) > 0

def dprint(level, *args):
    if is_set(level):
        frame = inspect.currentframe().f_back
        func = inspect.currentframe().f_back.f_code
        s = "%s %s:%s:%d:" % (g_header[level], func.co_name, func.co_filename.split("/")[-1], frame.f_lineno)
        for a in args:
            s += " " + str(a)
        print s
    return

    

