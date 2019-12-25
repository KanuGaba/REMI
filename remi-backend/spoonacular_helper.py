#############################
#   SPOONACULAR API CALLS   #
#############################
# The functions that handles the spoonacular API calls.



# Library imports.
import requests
import json
import spoonacular as sp
from typing import List
from collections import defaultdict

# Internal imports
import keys
import recipes
import utils



# constant returned when nothing in found in spoonacular

# Bad recipe cache. 
# The Spoonacular library does not appear to support requests caching.
# Interim solution. Should use sqlite.
ingredient_substitute_cache = {}
unit_conversion_cache = defaultdict(dict)
recipe_cache = {}

# place spoonacular api key here
api_instance = sp.API("9391ecfd5e9b4e59beb707c9ab26f637")

def get_all_substitutes(ingredient: str) -> list:
    response = api_instance.get_ingredient_substitutes(ingredient).json()
    try:
        return response[keys.SPOONACULAR_substitutes_key]
    except (IndexError, KeyError):
        return None

def get_substitute(ingredient: str, i: int) -> str:
    if (ingredient in ingredient_substitute_cache):
        utils.debug_log("Fetching substitute from cache.")
        substitute_list = ingredient_substitute_cache[ingredient]
    else:    
        substitute_list = api_instance.get_ingredient_substitutes(ingredient).json()
        ingredient_substitute_cache[ingredient] = substitute_list
    try:
        return substitute_list[keys.SPOONACULAR_substitutes_key][i]
    except (IndexError, KeyError):
        return keys.SPOONACULAR_unavailable

def resolve_ingredient(ingredient: str) -> str:
    response = api_instance.autocomplete_ingredient_search(ingredient).json()
    try:
        resolved_ingredient = response[0][keys.SPOONACULAR_name_key]
        return resolved_ingredient
    except IndexError:
        return keys.SPOONACULAR_unavailable

def unit_conversion(source_unit: str, target_unit: str, amount: float) -> float:
    if (source_unit in unit_conversion_cache and target_unit in unit_conversion_cache[source_unit]):
        utils.debug_log("Fetching conversion from cache.")
        return unit_conversion_cache[source_unit][target_unit]
    
    elif (target_unit in unit_conversion_cache and source_unit in unit_conversion_cache[target_unit]):
        utils.debug_log("Fetching conversion from cache.")
        return (1/unit_conversion_cache[target_unit][source_unit])
    
    else:
        response = api_instance.convert_amounts("flour", target_unit, amount, source_unit).json()
        converted_amount = float(response[keys.SPOONACULAR_target_amount])
        unit_conversion_cache[source_unit][target_unit] = converted_amount

    return converted_amount

def autocomplete_recipe(recipe_name: str) -> List:
    return api_instance.autocomplete_recipe_search(recipe_name, 8).json()

def get_recipe_steps(recipe_id: str) -> List:
    if (recipe_id in recipe_cache):
        utils.debug_log("Fetching recipe from cache.")
        return recipe_cache[recipe_id]

    response = api_instance.get_analyzed_recipe_instructions(recipe_id)
    recipe = response.json()
    instruction_list = []

    # Each recipe has many different instruction containers.
    # Each instruction container contains a list of steps.
    for instruction_container in recipe:
        instruction_list = instruction_list + instruction_container[keys.SPOONACULAR_steps_list]
    
    recipe_cache[recipe_id] = instruction_list

    return instruction_list
