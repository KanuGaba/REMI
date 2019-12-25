###########
#   APP   #
###########
# The 'main'. Starts the application.



# Library imports.
import threading
import time
import sys
import random
import webview

# Internal imports
from wake_word_detector.wake_word_detector import startWakeWordDetection
from controller import Controller



# Function to perform necessary setup once pywebview has loaded and rendered.
def setup(window):
    controller.set_window(window)
    startWakeWordDetection(controller.on_wake_word_trigger, window)



# Main.
if __name__ == "__main__":
    controller = Controller()
    window = webview.create_window('REMI', html=open("recipe.html").read(), js_api=controller)
    webview.start(setup, window)