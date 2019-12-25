######################
#   STEP CHANGE      #
######################
# The class that handles all of the step change competencies.



# Library imports
from flask import request
import json

# Internal imports
import keys
import clinc_utils
import utils
import spoonacular_helper
import intents
import recipes




class StepChange():

    def __init__(self):
        self.step_text = ""
        self.clinc_testing_curr_step = 0
        self.clinc_testing_curr_recipe_id = "324694"
    
    # All competency classes should have a 'resolve' function that the route function in main will call.
    def resolve(self, curr_intent, request_obj: dict):
        # Make sure request_obj has recipe id and curr step.
        client_request_obj = clinc_utils.get_client_request_obj(request_obj)
        
        if (client_request_obj != None):
            # Using our front end.
            # Get current recipe id and step.
            utils.debug_log("Front end calling step change.")
            curr_recipe_id = client_request_obj[keys.CLIENT_CHAT_curr_recipe_id]
            curr_step = client_request_obj[keys.CLIENT_CHAT_curr_step]
            clinc_utils.set_client_request_obj_prop(request_obj, keys.CLIENT_subintent, intents.SUBINTENT_client_recipe_walkthrough)
        else:
            # For testing purposes with the Clinc platform.
            utils.debug_log("Clinc front end calling step change.")
            curr_recipe_id = self.clinc_testing_curr_recipe_id
            curr_step = self.clinc_testing_curr_step

        recipe_steps_list = spoonacular_helper.get_recipe_steps(curr_recipe_id)

        if (curr_intent == intents.INTENT_repeat_step):
            # Curr Step is initialized to -1 when user has just started recipe.
            if (curr_step == -1):
                curr_step += 1

        elif(curr_intent == intents.INTENT_next_step):
            if (curr_step >= len(recipe_steps_list)-1):
                clinc_utils.create_slot(request_obj, keys.SC_instruction_text, {
                    keys.CLINC_resolved: keys.CLINC_resolved_status_true,
                    keys.CLINC_processed_value: "Congratulations! You finished the recipe!"
                })
                return clinc_utils.build_clinc_response(request_obj)
            else:
                curr_step += 1

        elif(curr_intent == intents.INTENT_previous_step):
            utils.debug_log("previous step.")
            if (curr_step <= 0):
                clinc_utils.create_slot(request_obj, keys.SC_instruction_text, {
                    keys.CLINC_resolved: keys.CLINC_resolved_status_true,
                    keys.CLINC_processed_value: "Sorry! You don't have any more steps before this!"
                })
                return clinc_utils.build_clinc_response(request_obj)
            else:
                curr_step -= 1

        if (client_request_obj):
            clinc_utils.set_client_request_obj_prop(request_obj, keys.CLIENT_CHAT_curr_step, curr_step)
        else:
            self.clinc_testing_curr_step = curr_step
            
        step_text = recipe_steps_list[curr_step][keys.SPOONACULAR_step]

        clinc_utils.create_slot(request_obj, keys.SC_instruction_text, {
            keys.CLINC_resolved: keys.CLINC_resolved_status_true,
            keys.CLINC_processed_value : step_text
        })
    
        response = clinc_utils.build_clinc_response(request_obj)
        return response
