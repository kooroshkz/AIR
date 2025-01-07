import requests

def response_to_output_raw(response : requests.models.Response) -> str:
    # get the payload
    payload = response.json()

    # grab first object (which contains the output)
    response_dict = payload[0]

    return response_dict["generated_text"]


def clean_response(model_output: str, prompt: str) -> str:
    response = model_output[len(prompt) :]

    return f"-----------Prompt-----------\n {prompt} \n-----------Model Response----------- \n{response}"
