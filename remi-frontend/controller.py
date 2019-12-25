##################
#   CONTROLLER   #
##################
# The central logic hub for the frontend.



# Library imports
import speech_recognition as sr
import requests
import webview

# Internal imports
import keys
import intents
from utils import debug_log, debug_json_log, error_log
from timer import Timer



class Controller():
    def __init__(self):
        # Controller internal data structures.
        self.backend_url = "https://remi-backend-app.herokuapp.com/client"
        self.listening_to_instruction = False
        self.curr_recipe_id = "583898"  # Some random default recipe.
        self.curr_recipe_name = "Recipe"
        self.curr_step = -1
        self.chat_history = []
        self.timer_hash = dict()
        self.available_timer_id = [0,1,2,3,4]
        self.qid = ""
        self.dialog_id = ""
        self.session_id = ""

        # UI <-> Controller state data structures.
        self.window = None
        self.user_messages = []
        self.remi_messages = []
        self.show_remi_loading = False
        self.show_user_loading = False
        self.show_recipe_steps = False
        self.user_verbal_request_recipe_steps = False
        self.show_recipe_steps = False
        self.user_verbal_request_timer_list = False
        self.show_timer_list = False



    #################################
    # Controller Internal Functions #
    #################################
    # Wake word trigger handler.
    def on_wake_word_trigger(self):
        if not self.listening_to_instruction:
            self.listen_for_instruction()

    # Start speech-to-text for spoken instruction.
    def listen_for_instruction(self):
        # Update internal and UI state.
        self.listening_to_instruction = True
        self.show_user_loading = True

        # Set up speech-to-text recognizer.
        r = sr.Recognizer()                                                                                 
        with sr.Microphone() as source:                                                                      
            debug_log("Speak:")                                                                              
            audio = r.listen(source)   

        try:
            # Parse user's speech as text.
            spoken_text = r.recognize_google(audio)

            # Update UI state.
            spoken_text = spoken_text.capitalize()
            self.user_messages.append(spoken_text)
            self.show_user_loading = False

            spoken_text = spoken_text.lstrip().rstrip().lower()

            if (spoken_text == "show recipe"):
                self.user_verbal_request_recipe_steps = True
                self.show_recipe_steps = True
            elif (spoken_text == "hide recipe" or spoken_text == "close recipe"):
                self.user_verbal_request_recipe_steps = True
                self.show_recipe_steps = False
            elif (spoken_text == "show timer" or spoken_text == "show timers"):
                self.user_verbal_request_timer_list = True
                self.show_timer_list = True
            elif (spoken_text == "hide timer" or spoken_text == "hide timers" or spoken_text == "close timer" or spoken_text == "close timers"):
                self.user_verbal_request_timer_list = True
                self.show_timer_list = False
            else:
                # Send request to backend.
                self.make_request(spoken_text)

            print("You said " + spoken_text)
        except sr.UnknownValueError:
            self.remi_messages.append("Sorry, I didn't catch that!")
            error_log("SpeechRecognizer: Unknown speech.")
            self.show_user_loading = False
        except sr.RequestError as e:
            self.remi_messages.append("Sorry, something went wrong with my interpreter!")
            error_log("SpeechRecognizer: Request error.")
            self.show_user_loading = False

        # Update internal state.
        self.listening_to_instruction = False

    # Call backend (Recipe page.)
    def api_call_recipe(self, incomplete_recipe_name):
        debug_log("Received request to complete {}".format(incomplete_recipe_name))
        
        # return [{"id":42569,"title":"chicken bbq"},{"id":583898,"title":"chicken pho"},{"id":598884,"title":"omg chicken"}]
        
        response_json = requests.post(
            self.backend_url,
            json={
                keys.CLIENT_intent: intents.INTENT_client_recipes,
                keys.CLIENT_RECIPE_query: incomplete_recipe_name
            },
            headers={
                'Content-Type': 'application/json'
            }
        ).json()
        debug_json_log(response_json)
        return self.resolve_recipe(response_json)

    # Handle backend response (Recipe page.)
    def resolve_recipe(self, response_json):
        return response_json[keys.CLIENT_RECIPE_recipe_list]

    # Call backend (Chat page.)
    def api_call_chat(self, message):
        debug_log("Received request to complete {}".format(message))
        self.show_remi_loading = True
        try:
            response_json = requests.post(
                self.backend_url,
                json={
                    keys.CLIENT_intent: intents.INTENT_client_chat,
                    keys.CLIENT_CHAT_curr_recipe_id: self.curr_recipe_id,
                    keys.CLIENT_CHAT_curr_step: self.curr_step,
                    keys.CLIENT_CHAT_user_message: message,
                    keys.CLIENT_CHAT_available_timer_id: self.available_timer_id,

                    # New additions.
                    keys.CLIENT_CHAT_clinc_qid: self.qid,
                    keys.CLIENT_CHAT_clinc_dialog_id: self.dialog_id,
                    keys.CLIENT_CHAT_clinc_session_id: self.session_id
                },
                headers={
                    'Content-Type': 'application/json'
                }
            ).json()
        except:
            self.remi_messages.append("I am sorry, my circuits are a little fuzzy!")
            self.show_remi_loading = False
            return

        self.show_remi_loading = False
        debug_json_log(response_json)
        self.resolve_chat(response_json)

    def api_call_recipe_list(self, recipe_id):
        print ("api_call_recipe_list")
        try:
            response_json = requests.post(
                self.backend_url,
                json={
                    keys.CLIENT_intent: intents.INTENT_client_fetch_recipe_steps,
                    keys.CLIENT_CHAT_curr_recipe_id: recipe_id,
                },
                headers={
                    'Content-Type': 'application/json'
                }
            ).json()
        except:
            return []

        return response_json.get(keys.CLIENT_CHAT_recipe_steps, [])

    # Handle backend response (Chat page.)
    def resolve_chat(self, response_json):
        subintent = response_json.get(keys.CLIENT_subintent)
        remi_message = response_json.get(keys.CLIENT_CHAT_remi_message)

        # New additions.
        self.qid = response_json.get(keys.CLIENT_CHAT_clinc_qid)
        self.dialog_id = response_json.get(keys.CLIENT_CHAT_clinc_dialog_id)
        self.session_id = response_json.get(keys.CLIENT_CHAT_clinc_session_id)
        
        if (subintent == intents.SUBINTENT_client_recipe_walkthrough):
            self.curr_step = response_json.get(keys.CLIENT_CHAT_curr_step)
            self.chat_history.append(remi_message)
            self.remi_messages.append(remi_message)

        elif (subintent == intents.SUBINTENT_client_timer_create):
            self.available_timer_id = response_json.get(keys.CLIENT_CHAT_available_timer_id)
            timer_id = response_json.get(keys.CLIENT_CHAT_timer_id)            
            timer_duration = response_json.get(keys.CLIENT_CHAT_timer_duration)
            # timer_id is None or timer_duration is None indicates timer setup failed on the backend.
            if (timer_id != None and timer_duration != None):
                self.timer_hash[timer_id] = Timer(timer_id, int(timer_duration), self.notify_timer_done)
                self.timer_hash[timer_id].start()

            self.chat_history.append(remi_message)
            self.remi_messages.append(remi_message)

        elif (subintent == intents.SUBINTENT_client_timer_update):
            self.available_timer_id = response_json.get(keys.CLIENT_CHAT_available_timer_id)
            timer_id = response_json.get(keys.CLIENT_CHAT_timer_id)
            timer_duration = response_json.get(keys.CLIENT_CHAT_timer_duration)

            # Cancel existing.
            if (timer_id in self.timer_hash):
                self.timer_hash[timer_id].cancel()
                self.timer_hash.pop(timer_id, None)
                debug_log("Timer {} cancelled!".format(timer_id))
            else:
                debug_log("Timer {} does not exist!".format(timer_id))

            # Reset new timer.
            if (timer_id != None and timer_duration != None):
                self.timer_hash[timer_id] = Timer(timer_id, int(timer_duration), self.notify_timer_done)
                self.timer_hash[timer_id].start()

            self.chat_history.append(remi_message)
            self.remi_messages.append(remi_message)

    # Helper function for timers.
    def notify_timer_done(self, id):        
        self.timer_hash.pop(id, None)
        if (id not in self.available_timer_id):
            self.available_timer_id.append(int(id)) # Gap! Assumes id is int type.
        self.remi_messages.append("Timer {} is done!".format(id))



    ####################
    # UI -> Controller #
    ####################
    # UI polls the Controller through this function (i.e. syncs state) (Chat page.)
    def get_state_chat(self, params):
        user_messages_response = self.user_messages[:]
        self.user_messages = []
        remi_messages_response = self.remi_messages[:]
        self.remi_messages = []
        state = {
            "user_messages": user_messages_response,
            "remi_messages": remi_messages_response,
            "show_remi_loading": self.show_remi_loading,
            "show_user_loading": self.show_user_loading,
            "timer_status": {k:self.timer_hash[k].remaining() for k in self.timer_hash},
            "show_recipe_steps": self.show_recipe_steps,
            "user_verbal_request_recipe_steps": self.user_verbal_request_recipe_steps,
            "show_timer_list": self.show_timer_list,
            "user_verbal_request_timer_list": self.user_verbal_request_timer_list
        }
        self.user_verbal_request_recipe_steps = False
        self.user_verbal_request_timer_list = False
        return state

    def fetch_recipes(self, params):
        print ("UI called for recipe fetch in fetch_recipes!")
        recipe_list = self.api_call_recipe_list(self.curr_recipe_id)
        print ("Fetched them recipes!")
        recipe_data = {
            "recipe_name": self.curr_recipe_name,
            "recipe_steps": recipe_list
        }
        return recipe_data  # Might need to use state!

    # When user has selected a recipe. (Recipe page.)
    def selected_recipe(self, recipe_data):
        # Setup
        debug_log("Selected recipe data: {}!".format(str(recipe_data)))
        self.curr_recipe_id = int(recipe_data["recipe_id"].lstrip().rstrip())
        self.curr_recipe_name = recipe_data["recipe_name"].lstrip().rstrip().title()
        self.curr_step = -1
        self.qid = self.dialog_id = self.session_id = ""
        self.load_chat_page()

    # Also applicable for Controller -> Controller: 
    # Centralized function for when user has issued a request text/speech. (Chat page.)
    def make_request(self, message):
        self.chat_history.append(message)
        self.api_call_chat(message)

    # When user clicks back button on chat page.
    def back_pressed(self, params):
        self.curr_recipe_id = 583898    # Some default recipe. (Pedantic)
        self.curr_recipe_name = "Recipe"
        self.curr_step = -1             # Reset step counter. (Pedantic)
        self.qid = self.dialog_id = self.session_id = "" # Reset id's. (Pedantic)
        self.load_recipe_page()

    # For UI to debug to the same console as the controller.
    def console_log(self, msg):
        debug_log(msg)



    ####################
    # Controller -> UI #
    ####################
    # Load recipe page.
    def load_recipe_page(self):
        if (self.window):
            debug_log("Loading recipe page...")
            self.window.load_html(open('recipe.html').read())
        else:
            error_log("Could not load recipe page!")

    # Load chat page.
    def load_chat_page(self):
        if (self.window):
            debug_log("Loaded chat page...")
            self.window.load_html(open('chat.html').read())
        else:
            error_log("Could not load chat page!")

    # Configure UI window.
    def set_window(self, window):
        self.window = window
