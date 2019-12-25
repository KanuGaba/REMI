#################
#   SET TIMER   #
#################
# The class that handles the set timer competency.



# Library imports
from flask import request
import json

# Internal imports
import keys
import clinc_utils
from utils import debug_log
import spoonacular_helper
import recipes
import intents

to_seconds = {
    'seconds': 1,
    'minutes': 60,
    'hours': 3600,
    'days': 86400,
    'second': 1,
    'minute': 60,
    'hour': 3600,
    'day': 86400
}

def seconds_to_verbal(seconds):
    units = ['days', 'hours', 'minutes', 'seconds']
    res = ""
    for unit in units:
        value = seconds // to_seconds[unit]
        seconds = seconds % to_seconds[unit]
        if value == 0:
            continue
        res += str(value) + ' ' + unit + ' '
    return res

def resolve_length(length_str):
    tokens = length_str.split()
    total_time = 0
    for i, token in enumerate(tokens):
        if (token not in to_seconds):
            continue
        if (i != 0 and tokens[i-1].isdigit()):
            total_time += int(tokens[i-1]) * to_seconds[token]
        else:
            total_time += to_seconds[token]

    return total_time



class TimerSetter():
    def __init__(self, step_changer):
        # Legacy for clinc testing.
        self.step_changer = step_changer
        self.available = set(range(5))
        self.dummies = [0] * 5

    # All competency classes should have a 'resolve' function that the route function in main will call.
    def resolve(self, request_obj: dict):
        # Client request object from front end.
        client_request_obj = clinc_utils.get_client_request_obj(request_obj)
        if (client_request_obj != None):
            curr_step = client_request_obj.get(keys.CLIENT_CHAT_curr_step)
            curr_recipe_id = client_request_obj.get(keys.CLIENT_CHAT_curr_recipe_id)
            available = set(client_request_obj.get(keys.CLIENT_CHAT_available_timer_id))
            debug_log("Available Timers:" + str(available))
        else:
            curr_step = self.step_changer.clinc_testing_curr_step
            curr_recipe_id = "324694"
            available = self.available

        try:
            if(clinc_utils.get_slot_value_clinc(request_obj, keys.TIMER_id, keys.CLINC_resolved) == keys.CLINC_resolved_status_true):
                id = str(clinc_utils.get_slot_value_clinc(request_obj, keys.TIMER_id, keys.CLINC_processed_value))
            else:
                id = clinc_utils.get_slot_value_clinc(request_obj, keys.TIMER_id, keys.CLINC_tokens, -1)
            
            length = clinc_utils.get_slot_value_clinc(request_obj, keys.TIMER_length, keys.CLINC_tokens, -1)
        except:
            id = None
            length = None
        
        seconds = 0
        start_timer = True
        print(id)

        # Resolve ID
        if (id == None or not id.isdigit() or int(id) < 0 or int(id) > 4):
            # Select ID automatically
            if (len(available) != 0):
                id = available.pop()
                clinc_utils.create_slot(request_obj, keys.TIMER_id, {})
                clinc_utils.set_slot_value_clinc(request_obj, keys.TIMER_id, keys.CLINC_processed_value, int(id))
                clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.TIMER_id])               
            else:
                # All timers in use, clinc should respond accordingly
                return clinc_utils.build_clinc_response(request_obj)
        else:
            clinc_utils.set_slot_value_clinc(request_obj, keys.TIMER_id, keys.CLINC_processed_value, int(id))
            clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.TIMER_id])               
            if (int(id) not in available and clinc_utils.get_intent(request_obj) == intents.INTENT_set_timer_start):
                clinc_utils.set_state(request_obj, keys.TIMER_override_timer)
                start_timer = False
            else:
                # ID exists!
                if (int(id) not in available):
                    debug_log(str(id)+" not available!")
                available.discard(int(id))

            

        # Resolve length if ID can be resolved
        if (length != None):
            seconds = resolve_length(length)
            clinc_utils.set_slot_value_clinc(request_obj, keys.TIMER_length, keys.CLINC_processed_value, seconds_to_verbal(seconds))
            clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.TIMER_length])
        else:
            # If length is not given in the utterance, check the current step for a length
            instruction_list = spoonacular_helper.get_recipe_steps(curr_recipe_id)
            instr = instruction_list[max(curr_step, 0)]   # User could be at step -1 (just started recipe.)
            if (instr.get('length', None) != None):
                seconds = int(instr['length']['number']) * to_seconds[instr['length']['unit']]
                clinc_utils.create_slot(request_obj, keys.TIMER_length, {})
                clinc_utils.set_slot_value_clinc(request_obj, keys.TIMER_length, keys.CLINC_processed_value, seconds_to_verbal(seconds))
                clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.TIMER_length])
            else:
                # Mark id as available if length could not be resolved
                start_timer = False
                available.add(id)
        
        if (start_timer):
            # With integrated frontend.
            if (client_request_obj):
                client_request_obj[keys.CLIENT_CHAT_timer_id] = id
                client_request_obj[keys.CLIENT_CHAT_timer_duration] = seconds
                client_request_obj[keys.CLIENT_CHAT_available_timer_id] = list(available)
                debug_log("Remaining Timers:" + str(available))
            
            # Legacy: For Clinc testing.
            else:
                self.dummies[int(id)] = seconds
                print(self.dummies)

        else:
            # With integrated frontend.
            if (client_request_obj):
                client_request_obj[keys.CLIENT_CHAT_timer_id] = None
                client_request_obj[keys.CLIENT_CHAT_timer_duration] = None

        return clinc_utils.build_clinc_response(request_obj)




