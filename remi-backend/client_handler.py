####################
#  CLIENT HANDLER  #
####################
# The class that handles client requests.



# Library imports
from flask import request
import json

# Internal imports
import keys
import intents
import states
import clinc_utils
import utils
import spoonacular_helper



class ClientHandler():
    def resolve(self, client_request_obj):
        curr_intent = client_request_obj.get(keys.CLIENT_intent)

        if (curr_intent == intents.INTENT_client_recipes):
            recipe_name = client_request_obj.get(keys.CLIENT_RECIPE_query)
            recipe_list = spoonacular_helper.autocomplete_recipe(recipe_name)
            client_request_obj[keys.CLIENT_RECIPE_recipe_list] = recipe_list
            return self.build_client_response(client_request_obj)

        elif (curr_intent == intents.INTENT_client_chat):
            return self.build_client_response(clinc_utils.post_clinc_request(client_request_obj))

        elif (curr_intent == intents.INTENT_client_fetch_recipe_steps):
            recipe_id = client_request_obj.get(keys.CLIENT_CHAT_curr_recipe_id)
            detailed_recipe_steps = spoonacular_helper.get_recipe_steps(recipe_id)
            simplified_recipe_steps = []
            for i in range(len(detailed_recipe_steps)):
                simplified_recipe_steps.append(str(i+1) + ") " + str(detailed_recipe_steps[i][keys.SPOONACULAR_step]))
            response = {keys.CLIENT_CHAT_recipe_steps: simplified_recipe_steps}

            return self.build_client_response(response)


        else:
            return self.build_client_response(client_request_obj)

    def build_client_response(self, json_obj: dict):
        return json.dumps(json_obj)