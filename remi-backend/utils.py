import json

debug_flag = True

def debug_log(msg):
    if (debug_flag):
        print (msg)

def debug_json_log(msg):
    if (debug_flag):
        print (json.dumps(msg, sort_keys=True, indent=2, separators=(',', ':')))