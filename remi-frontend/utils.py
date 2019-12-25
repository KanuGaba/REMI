#############
#   UTILS   #
#############
# Debug and error logging.



# Library imports.
import json



debug_flag = True

def debug_log(msg):
    if (debug_flag):
        print (msg)

def debug_json_log(msg):
    if (debug_flag):
        print (json.dumps(msg, sort_keys=True, indent=2, separators=(',', ':')))

def error_log(msg):
    print ("Error:", msg)