###############
#   INTENTS   #
###############
# Synced with backend.



# Client Intents. Used to inform backend which page we are on.
INTENT_client_recipes = "client_recipes"
INTENT_client_chat = "client_chat"
INTENT_client_fetch_recipe_steps = "client_fetch_recipe_steps"

# Client Subintents. Used by backend inform frontend what to do after it responds.
SUBINTENT_client_timer_create = "client_timer_create"
SUBINTENT_client_timer_update = "client_timer_update"
SUBINTENT_client_timer_cancel = "client_timer_cancel"
SUBINTENT_client_recipe_walkthrough = "client_recipe_walkthrough"
SUBINTENT_client_error = "client_error"