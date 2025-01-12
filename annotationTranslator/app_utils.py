import requests
import os
import random
import sqlite3

# Hugging face API key
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
headers = {"Authorization": "Bearer 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"}

allowed_extensions = {'png', 'jpg'}

"""
Collect the raw response of the huggingface model and conevrt it into text
"""
def response_to_output_raw(response : requests.models.Response) -> str | dict:
    # get the payload
    payload = response.json()

    # grab first object (which contains the output)
    if (type(payload) != dict):
        response_dict = payload[0]
        return response_dict["generated_text"]
    else: 

        if ('error' in payload):
            return f"ERROR: {payload['error']}"
        
        return payload 
    

"""
Clean the model response for display, by removing the prompt which is automatically included in the LLMs output
"""
def clean_response(model_output, prompt):

    response = model_output.split("|||||")[1]

    return f"-----------Prompt-----------\n {prompt} \n-----------Model Response----------- \n{response}"

def allowed_filename(filename : str | None):

    if (filename == None):
        return False

    if ('.' not in filename):
        return False
    
    #-1 isntead of [1] if for whatever reason someone had name img.png.jpg
    if (filename.rsplit('.')[-1] not in allowed_extensions):
        return False

    return True

"""
Gets the model response + adds separator |||||
"""
def get_model_response(text):

    payload = {
        "inputs": "you are a biology specialist who will convert the following sentence into a bullet point list summarizing the observations."
        + text + "|||||",
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    model_output = response_to_output_raw(response)

    if type(model_output) == dict:
        raise ValueError(f"Error: unrecognized return from LLM: {model_output}")

    response_clean = response.json()
    response_clean[0]["generated_text"] = clean_response(model_output, text)

    return response_clean 

def build_data_dirs(upload_dir : str, id_num : int):
    
    file_path = os.path.join(upload_dir, str(id_num) + "/")
    os.makedirs(file_path)

    return file_path
