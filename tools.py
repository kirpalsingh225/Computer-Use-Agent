from crewai.tools import tool
import pyautogui
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
import os
import google.generativeai as genai
from google import genai
from PIL import Image
import time


@tool("Open user given Application")
def open_application(app_name: str) -> str:
    """
    Input : app_name string the app that needs to be opened
    Description : This method takes an application name as input that has to be launched.
    Output : A string telling whether that application opened or not
    """

    try:
        # Press the Windows key
        pyautogui.press('win')
        time.sleep(2)  # Give the Start Menu/Search a moment to appear

        # Type the text
        pyautogui.write(app_name)
        time.sleep(2) # small pause to allow the text to be processed.

        # Press Enter
        pyautogui.press('enter')

        return "Application successfully opened"
    except Exception as e:
        return f"Got an error beacuse of {e}"

    # Function logic here
    


@tool("useful to click the elements")
def click(x : int, y : int) -> str:
    '''
    Description:
        This function is used to click an element on screen

    Input:
        x : the x coordinate of the element of type int
        y : the y coordinate of the element of type int

    Output:
        a string indicating whether the action was completed or not
    '''
    try:
        pyautogui.click(x, y)
        return f"Successfully clicked on the {x} and {y} coordinates"
    except Exception as e:
        return f"Unsuccessfull to click on the {x} and {y} coordinates because of {e}"

@tool("useful to scroll the page")
def scroll() -> str:
    '''
    Description:
        This function is used to scroll the screen

    Input:
        no input

    Output:
        a string indicating whether the action was completed or not
    '''
    try:
        pyautogui.scroll(-200)
        return f"Successfully abled to scroll"
    except Exception as e:
        return f"Unsuccessfull to scroll because of {e}"


@tool("useful to type on screen")
def type_text(text : str) -> str:
    '''
    Description:
        This function is used to write text on screen

    Input:
        text : the text that need to be typed of string type

    Output:
        a string indicating whether the action was completed or not
    '''
    try:
        pyautogui.write(text)
        return f"Successful to write the {text}"
    except Exception as e:
        return f"Unsuccessful to write the {text} because of {e}"



class Output(BaseModel):
    action : str = Field(description="Tells about the next action and what you will achieve")
    coordinates : List[int] = Field(description="Contains 2 values x and y to click on some element")

parser = PydanticOutputParser(pydantic_object=Output)

prompt = PromptTemplate(

    template = '''You are an expert in image reasoning and you can 
    reason with the image and the context provided.
    Provide me the coordinates of {object} from the image and 
    image width and height is {dims} and the coordinates should not
    exclude the dimensions range \n {format_instruction}''',
    input_variables = ["object", "dims"],
    partial_variables = {"format_instruction":parser.get_format_instructions()}
)

#formatted_prompt = prompt.invoke({"object":"tiger", "dims":image.size})

@tool("useful to know the current state of the screen and take action")
def get_next_action(previous_state : str, element : str) -> tuple:
    '''
    Description:
        This function captures the current state of the screen, analyzes it, and determines the next action to take based on the provided element and previous state.

    Input
        previous_state (str): A string describing the previous state or action taken. This can be used to provide context for the next action.
        element (str): The element or object on the screen that needs to be interacted with (e.g., a button, text field, etc.).

    Output:
        tuple: A tuple containing two elements:
            - action (str): A description of the next action to be taken (e.g., "Click on the button").
            - coordinates (List[int]): A list of two integers representing the x and y coordinates on the screen where the action should be performed.'''
    try:
        pyautogui.screenshot("screen.jpg")
        image = Image.open("screen.jpg")

        formatted_prompt = prompt.invoke({"object":element, "dims":image.size})


        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[formatted_prompt, image])

        final_result = parser.parse(response.text)

        return final_result.action, final_result.coordinates


    except Exception as e:
        return f"Error while giving the action and coordinates {e}"

