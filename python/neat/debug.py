import sys

DEBUG_ERROR = 1
DEBUG_INFO = 2
DEBUG_ALGO = 4
DEBUG_FILEINPUT = 8
DEBUG_INTEGRITY = 16

g_header = { DEBUG_ERROR: "ERR",
             DEBUG_INFO: "INF",
             DEBUG_ALGO: "ALG",
             DEBUG_FILEINPUT: "FIO",
             DEBUG_INTEGRITY: "ING",
             }

debug_level = (0 | \
               DEBUG_ERROR | \
               DEBUG_INFO | \
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
        sys.stdout.flush()
    return

def dcallstack(level):
    if is_set(level):
        frame = inspect.currentframe().f_back
        strings = []
        while frame:
            # up one level
            func = frame.f_code
            funcname = func.co_name
            filename = func.co_filename.split("/")[-1]
            lineno = frame.f_lineno
            s = "%s:%s:%d" % (funcname, filename, lineno)
            strings.append(s)
            frame = frame.f_back
        strings.reverse()
        for i in range(len(strings)):
            print "%s [%d] %s" % (g_header[level], i+1, strings[i])
    return

def main():
    print "Need debug exercise code here."
    return
    
if __name__ == "__main__":
    main()

