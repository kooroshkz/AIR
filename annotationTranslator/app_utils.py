import requests

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
    

def clean_response(model_output: str, prompt: str) -> str:

    response = model_output[len(prompt) :]

    return f"-----------Prompt-----------\n {prompt} \n-----------Model Response----------- \n{response}"
