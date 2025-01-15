import requests
import os
from logger import *

# Hugging face API key
# TODO: define the API key as an env variable and get it with os instead
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
headers = {"Authorization": "Bearer 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"}

allowed_extensions = {"png", "jpg"}
logger = get_logger(__name__)


def response_to_output_raw(response: requests.models.Response) -> str | dict:
    """
    Collect the raw response of the huggingface model and conevrt it into text
    """
    
    logger.debug("Processing HuggingFace Response.")

    # get the payload
    payload = response.json()

    # grab first object (which contains the output)
    if type(payload) != dict:
        response_dict = payload[0]
        return response_dict["generated_text"]
    else:

        if "error" in payload:
            return f"ERROR: {payload['error']}"

        return payload


def clean_response(model_output, prompt):
    """
    Clean the model response for display, by removing the prompt which is automatically included in the LLMs output
    """
    logger.debug("Cleaning model response.")
    response = model_output.split("|||||")[1]

    return f"-----------Prompt-----------\n {prompt} \n-----------Model Response----------- \n{response}"


def allowed_filename(filename: str | None):

    logger.debug("Checking for allowed filename.")

    if filename == None:
        return False

    if "." not in filename:
        return False

    # -1 isntead of [1] if for whatever reason someone had name img.png.jpg
    if filename.rsplit(".")[-1] not in allowed_extensions:
        return False

    return True


def get_model_response(text : str) -> str:
    """
    Gets the model response + adds separator |||||
    """

    payload = {
        "inputs": "you are a biology specialist who will convert the following sentence into a bullet point list summarizing the observations."
        + text
        + "|||||",
    }

    try:
        logger.debug(f"Sending request with header: {headers} and payload: {payload} to Huggingface.")
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        model_output = response_to_output_raw(response)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in LLM API request: {e}", exc_info=True)
        print(f"ERROR: in calling huggingface for model response -> {str(e)}")
        return "ERROR"

    if type(model_output) == dict:
        logger.error(f"Error: unrecognized return from LLM: {model_output}")
        raise ValueError(f"Error: unrecognized return from LLM: {model_output}")

    response_clean = response.json()
    response_clean[0]["generated_text"] = clean_response(model_output, text)

    return response_clean[0]["generated_text"]


def build_data_dirs(upload_dir: str, id_num: int):

    file_path = os.path.join(upload_dir, str(id_num) + "/")
    os.makedirs(file_path)

    return file_path
