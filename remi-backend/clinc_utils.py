###############
# CLINC UTILS #
###############
# Handle processing clinc responses boilerplate
# Please refer to the terminology guide at the bottom of this file for
# a visual guide to which part of the Clinc Request each function handles.



# Library imports
from flask import request
import json
import requests
from typing import Any, Iterable, List

# Internal imports
import keys
import intents
import states
import utils



CLINC_ai_version = '4c0fb55a-0f01-4e7a-b724-ad1c25fa1f2d'
CLINC_app_key = '07b1a5e8b72a82381eba6d59525c9f6a668f94ef'



# *** SLOT MAP ***
def get_slots_map(clinc_request_json: dict) -> dict:
    slot_map = clinc_request_json.get(keys.CLINC_slots_map, None)
    if (slot_map):
        return slot_map
    raise Exception("No slots map in request!")


# *** SLOT ***
def get_slot(clinc_request_json: dict, slot_key: str) -> dict:
    return get_slots_map(clinc_request_json).get(slot_key, None)

def create_slot(clinc_request_json: dict, slot_key: str, value_map: dict) -> dict:
    new_slot = dict()
    new_slot[keys.CLINC_type] = "string"

    if value_map.get(keys.CLINC_resolved, None) == None:
        value_map[keys.CLINC_resolved] = -1

    if value_map.get(keys.CLINC_tokens, None) == None:
        value_map[keys.CLINC_tokens] = ""

    new_slot[keys.CLINC_values_list] = [value_map]
    clinc_request_json[keys.CLINC_slots_map][slot_key] = new_slot


# *** LIST OF VALUE MAPS ***
def get_list_of_value_maps(clinc_request_json: dict, slot_key: str) -> List[dict]:
    slot = get_slot(clinc_request_json, slot_key)
    if (not slot):
        return None
    else:
        return slot.get(keys.CLINC_values_list, None)


# *** VALUE MAP ***
def get_clinc_values_map(clinc_request_json: dict, slot_key: str, index: int = 0) -> dict:
    values_list = get_list_of_value_maps(clinc_request_json, slot_key)
    if (values_list and len(values_list) > index):
        return values_list[index]
    return None


# *** SLOT VALUE ***
def check_for_slot(clinc_request_obj: dict, slot_key: str) -> bool:
    try:
        get_slots_map(clinc_request_obj)
    except:
        return False

    print(slot_key + " slot: " + str(get_slot(clinc_request_obj, slot_key)))
    if get_slot(clinc_request_obj, slot_key):
        print("found slot")
        return True
    else:
        print("slot doesn't exist")
        return False

def get_slot_value_clinc(clinc_request_json: dict, slot_key: str, value_key: str, index: int = 0) -> dict:
    clinc_values_map = get_clinc_values_map(clinc_request_json, slot_key, index)
    if (clinc_values_map):
        return clinc_values_map.get(value_key, None)

def set_slot_value_clinc(clinc_request_json: dict, slot_key: str, value_key: str, new_value: Any, index: int = 0) -> None:
    clinc_values_map = get_clinc_values_map(clinc_request_json, slot_key, index)
    if (clinc_values_map):
        clinc_values_map[value_key] = new_value

def set_slot_resolved_clinc(clinc_request_json: dict, resolved_status: str, slot_keys_list: Iterable, index: int = 0) -> None:
    for slot_key in slot_keys_list:
        set_slot_value_clinc(clinc_request_json, slot_key, keys.CLINC_resolved, resolved_status, index)

def create_slot(clinc_request_json: dict, slot_key: str, value_map: dict) -> dict:
    new_slot = dict()
    new_slot['type'] = "string"

    if (value_map.get(keys.CLINC_resolved, None) == None):
        value_map[keys.CLINC_resolved] = -1

    if (value_map.get(keys.CLINC_tokens, None) == None):
        value_map[keys.CLINC_tokens] = ''

    new_slot[keys.CLINC_values_list] = [value_map]
    clinc_request_json[keys.CLINC_slots_map][slot_key] = new_slot


# *** STATE ***
def get_state(clinc_request_json: dict) -> None:
    return clinc_request_json[keys.CLINC_state]

def set_state(clinc_request_json: dict, new_state: str) -> None:
    clinc_request_json[keys.CLINC_state] = new_state


# *** INTENT ***
def get_intent(clinc_request_json: dict) -> str:
    return clinc_request_json[keys.CLINC_intent]

def set_intent(clinc_request_json: dict, new_intent: str) -> None:
    clinc_request_json[keys.CLINC_intent] = new_intent


# *** SESSION ***
# get the unique session id from the request object
def get_session_id(clinc_request_obj: dict) -> str:
    return str(clinc_request_obj[keys.CLINC_session_id])


# *** CLASSIFIER STATE  ***
# Don't worry about this in the context of the backend.
# Only used for front end.
def get_classifier_state(clinc_request_json: dict) -> str:
    return clinc_request_json.get(keys.CLINC_classifier_state, None)


# Processing before returning from POST request.
def build_clinc_response(json_obj: dict):
    return json.dumps(json_obj)


# *** CLIENT_REQUEST_OBJ ***
def get_client_request_obj(clinc_request_json: dict) -> dict:
    return clinc_request_json.get(keys.CLINC_client_request_obj)

def set_client_request_obj_prop(clinc_request_json: dict, key: str, value: int) -> None:
    clinc_request_json[keys.CLINC_client_request_obj][key] = value


# *** CLIENT REQUESTS ***
def get_clinc_app_key() -> str:
    # Fetch OAuth
    url_oauth = "https://api.clinc.ai/v1/oauth"

    headers_oauth = {
        "cache_control": "no-cache",
        "content-type": "application/x-www-form-urlencoded"
    }

    data_oauth = {
        "institution": "eecs498team6",
        "username": "user3",
        "password": "password3",
        "grant_type": "password",
        "scope": "query",
    }

    response_oauth = requests.post(url_oauth, data=data_oauth, headers=headers_oauth)
    response_oauth_json = response_oauth.json()

    # Fetch API Key.
    oauth_token = response_oauth_json['access_token']

    url_app_token = "https://api.clinc.ai/v1/apps/applicationtoken"

    headers_app_token = {
        "Authorization": "Bearer "+str(oauth_token),
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded"
    }

    data_app_token = {
        "scopes":"query app_read",
        "force":"true"
    }

    response_app_token = requests.post(url_app_token, data=data_app_token, headers=headers_app_token)
    response_app_token_json = response_app_token.json()

    return (response_app_token_json["token"])

def post_clinc_request(client_request_obj: dict) -> dict:
    response_json = requests.post(
        'https://api.clinc.ai:443/v1/query',
        json={
            keys.CLINC_client_request_obj: client_request_obj,
            'query' : client_request_obj[keys.CLIENT_CHAT_user_message],
            'ai_version': CLINC_ai_version,
            'lat': 0.0,
            'lon': 0.0,
            'time_offset': 0,
            'device': 'Derp',
            keys.CLINC_qid: client_request_obj[keys.CLIENT_CHAT_clinc_qid],
            keys.CLINC_dialog_id: client_request_obj[keys.CLIENT_CHAT_clinc_dialog_id],
            keys.CLINC_session_id: client_request_obj[keys.CLIENT_CHAT_clinc_session_id]
        },
        headers={
            'Authorization': 'app-key {}'.format(CLINC_app_key),
            'Content-Type': 'application/json'
        }
    ).json()

    # Need to fetch the client_request_obj in the business logic response
    # as backend will perform necessary updates to client_request_obj
    if (keys.CLINC_business_logic_response in response_json):
        client_request_obj = response_json[keys.CLINC_business_logic_response][keys.CLINC_client_request_obj]
    else:
        client_request_obj = response_json[keys.CLINC_client_request_obj]

    # Update response message.
    client_request_obj[keys.CLIENT_CHAT_remi_message] = response_json[keys.CLINC_visuals][keys.CLINC_formatted_response]
    client_request_obj[keys.CLIENT_subintent] = get_client_subintent(response_json)
    
    # Update identifiers.
    client_request_obj[keys.CLIENT_CHAT_clinc_qid] = response_json[keys.CLINC_qid]
    client_request_obj[keys.CLIENT_CHAT_clinc_dialog_id] = response_json[keys.CLINC_dialog_id]
    client_request_obj[keys.CLIENT_CHAT_clinc_session_id] = response_json[keys.CLINC_session_id]

    return client_request_obj

def get_client_subintent(response_json):
    intent = get_intent(response_json)
    classifier_state = get_classifier_state(response_json)
    
    utils.debug_json_log(classifier_state)

    if (classifier_state == states.STATE_set_timer and intent == intents.INTENT_set_timer_start):
        return intents.SUBINTENT_client_timer_create

    # Many competencies have cs_yes.
    # Update timer needs to be:
    #   state: "override_yes"
    #   intent: "cs_yes"
    elif (classifier_state == states.STATE_override_yes and intent == intents.INTENT_cs_yes):
        return intents.SUBINTENT_client_timer_update

    # TODO: Timer cancelling.
    # elif (intent == **cancelling timer**):
    #     return intents.SUBINTENT_client_timer_cancel

    else:
        return intents.SUBINTENT_client_recipe_walkthrough
        # intent == intents.INTENT_next_step or 
        # intent == intents.INTENT_previous_step or 
        # intent == intents.INTENT_repeat_step or 
        # intent == intents.INTENT_unit_conversion_start or 
        # intents == intents.INTENT_ingredient_substitution_start or
        # intents == intents.INTENT_ingredient_missing



### TERMINOLOGY USED IN THIS FILE ###
"""
*** A SLOT MAP ***
'slots': {

    *** A SLOT ***
    '_AMOUNT_': {
        'type': 'string',

        *** A LIST OF VALUE MAPS ***
        'values': [

            *** A VALUE MAP *** (first one in the list is the CLINC VALUE MAP.)
            {

                *** A SLOT VALUE ***
                'resolved': -1, (the resolved slot value)
                'tokens': '100'

            }
        ]
    }
}

*** TERMINOLOGY ***                 :       ### FUNCTION ###
A SLOT MAP                          :       get_slots_map
A SLOT                              :       get_slot(slot_key)
A LIST OF VALUES MAP                :       get_list_of_value_maps(slot_key)
A VALUE MAP                         :       get_clinc_values_map(slot_key)
A SLOT VALUE                        :       set/get_slot_value_clinc
"""
