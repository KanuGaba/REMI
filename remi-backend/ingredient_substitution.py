############################
#  INGREDIENT SUBSTITUTER  #
############################
# The class that handles the Ingredient substitution competency.



# Library imports
from flask import request
import json

# Internal imports
import keys
import states
import clinc_utils
import utils
import spoonacular_helper



class IngredientSubstitution():
    def __init__(self):
        self.substitute_number = {}
        self.substitute_cache = {}

    def reset_substitute_number(self, request_obj: dict):
        self.substitute_number[clinc_utils.get_session_id(request_obj)] = 0

    def increment_substitute_number(self, request_obj: dict):
        self.substitute_number[clinc_utils.get_session_id(request_obj)] += 1

    def make_substitution(self, client_request_obj, resolved_missing_ingredient: str, substitute_name: str):
        if (client_request_obj != None):
            recipe_id = client_request_obj[keys.CLIENT_CHAT_curr_recipe_id]
        else:
            recipe_id = "324694"
        recipe = spoonacular_helper.get_recipe_steps(recipe_id)
        for step in recipe:
            #has_ingr = False
            #for ingr in step[keys.SPOONACULAR_ingredient_list]:
            #    if ingr["id"] == resolved_missing_ingredient:
            #        has_ingr = True
            #        break
            #if(has_ingr):
            step_text = step[keys.SPOONACULAR_step]
            try:
                index = step_text.lower().index(resolved_missing_ingredient.lower())
                step_text = step_text[:index] + substitute_name + step_text[index+len(resolved_missing_ingredient):]
                step[keys.SPOONACULAR_step] = step_text
            except:
                pass



    # All competency classes should have a 'resolve' function that the route function in main will call.
    def resolve(self, request_obj: dict):
        
        client_request_obj = clinc_utils.get_client_request_obj(request_obj)

        if not clinc_utils.check_for_slot(request_obj, keys.IS_ingredient):
            # no ingredient slot, do nothing
            return clinc_utils.build_clinc_response(request_obj)

        if(clinc_utils.get_slot_value_clinc(request_obj, keys.IS_substitue, keys.CLINC_resolved) == keys.CLINC_resolved_status_true):
            resolved_missing_ingredient = clinc_utils.get_slot_value_clinc(request_obj, keys.IS_ingredient, keys.CLINC_processed_value)
        else:
            missing_ingredient = clinc_utils.get_slot_value_clinc(request_obj, keys.IS_ingredient, keys.CLINC_tokens)
            print("resolving ingredient: " + missing_ingredient)
            resolved_missing_ingredient = spoonacular_helper.resolve_ingredient(missing_ingredient)
            print("resolved ingredient: " + resolved_missing_ingredient)

        if(resolved_missing_ingredient == keys.SPOONACULAR_unavailable):
            utils.debug_log("cannot find ingredient in spoonacular")
            return clinc_utils.build_clinc_response(request_obj)

        if (clinc_utils.get_state(request_obj) == states.STATE_ingredient_confirm):
            selected = clinc_utils.get_slot_value_clinc(request_obj, keys.IS_substitue, keys.CLINC_processed_value)
            split_sel = selected.split()
            index = split_sel.index("=")
            numbers = [i for i in range(index, len(split_sel)) if split_sel[i][0].isnumeric()]
            for n in numbers:
                if n < len(split_sel)-1:
                    split_sel[n] = ''
                    split_sel[n+1] = ''
            if(index == -1 or index+1 >= len(split_sel)):
                print("Cannot extract name of substitute. This should not happen")
                return clinc_utils.build_clinc_response(request_obj)
            substitute_name = ' '.join(split_sel[index+1:])
            substitute_name = substitute_name[2:]
            self.make_substitution(client_request_obj, resolved_missing_ingredient, substitute_name)
            return clinc_utils.build_clinc_response(request_obj)

        # try to find substitute for ingredient
        #substitue = spoonacular_helper.get_substitute(resolved_missing_ingredient, self.substitute_number[clinc_utils.get_session_id(request_obj)])
        if(resolved_missing_ingredient in self.substitute_cache):
            substitute_list = self.substitute_cache[resolved_missing_ingredient]
        else:
            substitute_list = spoonacular_helper.get_all_substitutes(resolved_missing_ingredient)
        self.substitute_cache[resolved_missing_ingredient] = substitute_list

        if substitute_list == None:
            print("cannot find substitute for ingredient")
            clinc_utils.set_slot_value_clinc(request_obj, keys.IS_ingredient, keys.CLINC_processed_value, resolved_missing_ingredient)
            clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.IS_ingredient])
            clinc_utils.set_state(request_obj, states.STATE_ingredient_selection)
            return clinc_utils.build_clinc_response(request_obj)

        else:
            print("All substitutes:",substitute_list)
            index = self.substitute_number[clinc_utils.get_session_id(request_obj)]
            if (index >= len(substitute_list)):
                print("End of substitute list")
                clinc_utils.create_slot(request_obj, keys.IS_substitue, {})
                clinc_utils.set_state(request_obj, states.STATE_ingredient_end)
                return clinc_utils.build_clinc_response(request_obj)
            substitute = substitute_list[self.substitute_number[clinc_utils.get_session_id(request_obj)]]

            print("found substitute, constucting response and returing")
            clinc_utils.set_slot_value_clinc(request_obj, keys.IS_ingredient, keys.CLINC_processed_value, resolved_missing_ingredient)
            clinc_utils.create_slot(request_obj, keys.IS_substitue, {})
            clinc_utils.set_slot_value_clinc(request_obj, keys.IS_substitue, keys.CLINC_processed_value, substitute)
            clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.IS_substitue, keys.IS_ingredient])
            clinc_utils.set_state(request_obj, states.STATE_ingredient_selection)
            return clinc_utils.build_clinc_response(request_obj)
