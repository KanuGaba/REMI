######################
#   UNIT CONVERTER   #
######################
# The class that handles the unit conversion competency.



# Library imports
from flask import request
import json

# Internal imports
import keys
import clinc_utils
import utils
import spoonacular_helper



class UnitConverter():
    # All competency classes should have a 'resolve' function that the route function in main will call.
    def resolve(self, request_obj: dict):
        source_unit = clinc_utils.get_slot_value_clinc(request_obj, keys.UC_source_unit, keys.CLINC_tokens)
        target_unit = clinc_utils.get_slot_value_clinc(request_obj, keys.UC_target_unit, keys.CLINC_tokens)
        amount = clinc_utils.get_slot_value_clinc(request_obj, keys.UC_amount, keys.CLINC_tokens)


        if (source_unit != None and target_unit != None and amount != None):
            converted_amount = self.convert(source_unit, target_unit, amount)

            clinc_utils.set_slot_value_clinc(request_obj, keys.UC_amount, keys.CLINC_processed_value, converted_amount)
            clinc_utils.set_slot_value_clinc(request_obj, keys.UC_source_unit, keys.CLINC_processed_value, source_unit)
            clinc_utils.set_slot_value_clinc(request_obj, keys.UC_target_unit, keys.CLINC_processed_value, target_unit)

            clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.UC_amount, keys.UC_source_unit, keys.UC_target_unit])

        return clinc_utils.build_clinc_response(request_obj)

    def convert(self, source_unit: str, target_unit: str, amount: float) -> float:
        return spoonacular_helper.unit_conversion(source_unit, target_unit, amount)
