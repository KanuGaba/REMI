###########
#   APP   #
###########
# The 'main'. Handles routing.


# Library imports.
from flask import Flask, request, jsonify
import json
import requests_cache
# from flask_sqlalchemy import SQLAlchemy     # For db in the future.
# from flask_marshmallow import Marshmallow   # For serialization in the future.

# Internal imports.
import clinc_utils
import utils
import states
import intents
import keys
import unit_converter
import set_timer
import step_change
import ingredient_substitution
import client_handler


# Initialize Flask app.
app = Flask(__name__)

# Initialize cache
# Cache entries expire after an hour.
requests_cache.install_cache(cache_name='external_api_cache', backend='sqlite', expire_after=3600)

# Initialize competency classes.
converter = unit_converter.UnitConverter()
step_changer = step_change.StepChange()
timer_setter = set_timer.TimerSetter(step_changer)
substitute_finder = ingredient_substitution.IngredientSubstitution()
client_handler_instance = client_handler.ClientHandler()

@app.route("/", methods=["POST"])
def route():
    clinc_request_obj = request.get_json()     # Parse json as a python dictionary.

    curr_intent = clinc_utils.get_intent(clinc_request_obj)
    curr_state  = clinc_utils.get_state(clinc_request_obj)

    # Route to correct class.
    if (curr_intent == intents.INTENT_unit_conversion_start):
        return converter.resolve(clinc_request_obj)

    elif(curr_intent == intents.INTENT_repeat_step or curr_intent == intents.INTENT_next_step or curr_intent == intents.INTENT_previous_step):
        return step_changer.resolve(curr_intent, clinc_request_obj)

    #elif (curr_intent == intents.INTENT_set_timer_start or curr_intent == intents.INTENT_set_timer_update):
    elif (curr_state == states.STATE_set_timer or curr_state == states.STATE_override_yes):
        return timer_setter.resolve(clinc_request_obj)

    elif (curr_intent == intents.INTENT_ingredient_substitution_start):
        substitute_finder.reset_substitute_number(clinc_request_obj)
        return substitute_finder.resolve(clinc_request_obj)
    elif (curr_state == states.STATE_ingredient_selection and curr_intent == intents.INTENT_use_another_substitute):
        substitute_finder.increment_substitute_number(clinc_request_obj)
        return substitute_finder.resolve(clinc_request_obj)
    elif (curr_state == states.STATE_ingredient_confirm):
        #substitute_finder.increment_substitute_number(clinc_request_obj)
        return substitute_finder.resolve(clinc_request_obj)
    elif (curr_intent == intents.INTENT_ingredient_missing):
        return substitute_finder.resolve(clinc_request_obj)

    # Default return original request.
    return clinc_utils.build_clinc_response(clinc_request_obj)

@app.route("/client", methods=["POST"])
def route_client():
    client_request_obj = request.get_json()
    return client_handler_instance.resolve(client_request_obj)

if __name__ == '__main__':
    app.run(debug=True)
