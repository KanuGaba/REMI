# remi-backend

## Setup
Clone repository and set up virtual environment:

```python
> python3 -m venv env
> source env/bin/activate
```

Run the following command to install dependencies:
```python
> pip install -r requirements.txt
```

To host:
```python
> python3 app.py
```

(Optional)
Consider getting ngrok if you want to test any new code with the Clinc platform.
https://ngrok.com/

Cons of this method is that it only works for one ngrok url at a time. (i.e. only one of us can test at a time.)
Still figuring out a better method.


## Writing Code.
### Competency Files
We will be structuring the backend this way.
Each competency on Clinc has a corresponding **Competency Class** in our backend.

You should structure your Competency Class this way:
```python
class CompetencyClass():
    def resolve(self, request_obj: dict):
        # Your code here.
```

The main routing is abstracted away in app.py. Whenever app.py receives a Clinc request that should be routed to your Competency Class,
it will call the resolve method on your Competency Class with the Clinc request json object.

In your code:
* If you need to make an API request to spoonacular, please write a function in spoonacular.py that does this request for you.
* If you need to parse the clinc request json, please try to use the functions in clinc_utils as much as possible and refrain from parsing the json yourself. (You can add new methods in that file if you want.)
* Please refrain from using static strings for your keys.


### Static Strings
The three files:
```python
> keys.py
> intents.py
> states.py
```
are files that hold static strings that map with our keys on the Clinc Platform.
Please don't use the raw values of the keys in any other files or it may lead to difficulties in debugging.

Format for keys.py
<COMPETENCY_NAME_IN_CAPS>_<key_name_lowercase>

Format for intents.py
INTENT_<intent_name_lowercase>

Format for states.py
STATE_<state_name_lowercase>


### Clinc specific knowledge.
Clinc has a couple of rules that you have to follow for it to work right.
Here is a general template you can use so that your processed response will work with Clinc.

It covers the steps from extracing a certain slot's value to returning it back to Clinc.

Template:
```python
# Fetch the raw value.
val = clinc_utils.get_slot_value_clinc(request_obj, ***<Slot_Key>***, keys.CLINC_tokens)

# Process the value.
new_val = process(val)

# Set the return value.
clinc_utils.set_slot_value_clinc(request_obj, ***<Slot_Key>***, keys.CLINC_processed_value, new_val)

# Return
clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.SLOT_num])

# Return the processed object.
return clinc_utils.build_clinc_response(request_obj)
```

Example:
Suppose we wish to extract a slot called "num" and we want to return "num" slot's value + 10.
```python
Example: 
request_obj; # From Clinc

# Get num's value
# Here request_obj is the json response from Clinc, keys.SLOT_num is just the raw string "num".
num = clinc_utils.get_slot_value_clinc(request_obj, keys.SLOT_num, keys.CLINC_tokens)   # Just always use keys.CLINC_tokens whenever you want the value corresponding to the slot.

new_num = num + 10

# Set the return value.
clinc_utils.set_slot_value_clinc(request_obj, keys.SLOT_num, keys.CLINC_processed_value, new_num)   # keys.CLINC_processed_value is a parameter you need to pass in to specify that you are setting the return value.

# You need to let Clinc know that this slot has a return value.
clinc_utils.set_slot_resolved_clinc(request_obj, keys.CLINC_resolved_status_true, [keys.SLOT_num])

# Return the processed object.
return clinc_utils.build_clinc_response(request_obj)
```



### API calls to Spoonacular.
Please put all code for api requests to Spoonacular in functions in spoonacular.py



## Deploy to Heroku
Install Heroku CLI on your machine.
The most universal solution is:
``` shell
curl https://cli-assets.heroku.com/install.sh | sh 
```

Verify the installation:
``` shell
heroku --version  
```

Register 'heroku' in your git config for the backend respository to remi-backend-app.
``` shell
heroku git:remote -a remi-backend-app  
```

Only push to heroku from master. After you've merged into master, checkout the master branch and run:
``` shell
git push heroku master
```
The username is **remi.ai.team@umich.edu** and the password is **dofficialremiai#2019**. <br/>

Things are usually done after pushing to heroku master though you might occasionally have to run this command but it is extremely unlikely.
``` shell
heroku ps:scale web=1 
```

To view logs on heroku, run:
```
heroku logs --tail 
```