import pyttsx3, asyncio, threading, queue
import langchain_core
from langchain_community.chat_models import ChatOllama
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage, FunctionMessage
import chatFunctions as chatFunctions, yoloFunctions as yoloFunctions
import os, copy
import json, re
import platform, time
import datetime
import zoneinfo

engine = pyttsx3.init()
engine.setProperty("rate", 180)
engine.setProperty("volume", 0.9)

def calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens):
    input_rate = 0.00000005
    output_rate = 0.0000004
    return (prompt_tokens * input_rate) + (completion_tokens * output_rate)

def addToTotalCosts(content):
    global totalCost

    token_data = content.response_metadata.get("token_usage", {})
    prompt_tokens = token_data.get("prompt_tokens", 0)
    completion_tokens = token_data.get("completion_tokens", 0)

    cost = calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)

    print(f"\n📊 Token Usage: {prompt_tokens} input | {completion_tokens} output")
    print(f"💸 Estimated Cost: ${cost:.6f}\n")

    totalCost += cost


funcDocs = {}
for i in chatFunctions.functions:
   funcDocs[i.__name__] = i.__doc__

mainInstructions = ""
with open("../../PICO_AI_Instructions/mainInstructions.txt", 'r') as file:
    mainInstructions = file.read()

# print(mainInstructions)
# input()

aiPersonality = """
---- AI PERSONALITY ----

Information to know:
    - You were created by the new startup named "Neblina". They are from Brazil.
    - The company Neblina is composed by:
        - Tiago Castro Orbite: He is the cofounder and Tech Lead of the company and he was the person who created you by himself.
        - Marina Mattia de Oliveria: She is the cofounder and the Product Owner of the company. She took care of pretty much all of the organization and papers from the company and also had a huge role in helping with the marketing.
        - Vitor: He helped with the marketing and also helped with the labeling of images for AI.
        - Augusto Ávila: He helped with labeling the AI.

When talking about your personality:
    - Your name is PICO. It is a sigla in portuguese from Brazil that means "Projeto de Interação para Controle Operacional" devido ao seu funcionamento e objetivo.
    - Try to always be happy and charming.
"""

userInformation = f""""""

functionsInformation = f"""The available functions are: {funcDocs}"""


functions_prompt = f"{mainInstructions}\n {functionsInformation}\n {aiPersonality}\n {userInformation}"

PICO_AI = chatFunctions.AI_character(functions_prompt)

def getComputerInfo():
    """This function gets the computer information and returns it as a dictionary"""
    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(local_tz)
    info = {}
    screen = yoloFunctions.getCurrentScreenImage()
    apps = yoloFunctions.getModelPrediction("find_app", screen)
    info["open_apps"] = list(apps.keys()) if len(list(apps.keys())) > 0 else "No apps are open"
    info["os"] = platform.system()
    info["current_day"] = f"year {now.year}| month {now.strftime('%m')}| day {now.strftime('%d')}|"
    info["current_time"] = now.strftime("%H:%M:%S")
    return info

def decompileAiJson(json_response, usr_msg):
    try:
        if isinstance(json_response, dict):
            data = json_response
        else:
            if isinstance(json_response, tuple):
                json_response = json_response[0]
            data = json.loads(json_response)
    except Exception as e:
        print("-------------------$$$$$$$$$$$$$$$$$$$$$-------------------")
        print("The response was not a json string")
        print()
        print(json_response)
        print(type(json_response))
        print()
        # print(new)
        print()
        print(len(PICO_AI.memory))
        print("-------------------$$$$$$$$$$$$$$$$$$$$$-------------------")
        print()
        PICO_AI.memory.append(SystemMessage(
            """WARNING: Your previous response was INVALID because it was NOT a valid JSON. 
            You MUST ONLY respond with a JSON object, nothing before or after it. 
            Do not say 'Here is my response' or anything else. 
            If the user asks for multiple functions, you must refuse and explain that only one function per request is allowed."""))
        response, content = PICO_AI.message(usr_msg)
        data = decompileAiJson(response, usr_msg)
    return data

def execute_function(data):
    # print(f"{json_response}")
    # input()
    fctnames = [i.__name__ for i in chatFunctions.functions]
    # data = decompileAiJson(json_response, usr_msg)
    

    function_name = data["function"]
    parameters = data["parameters"]
    chat_response = data["response"]
    loop = data["loop"]
    # print(data, loop)
    # input()
    if not function_name or not parameters:
        return chat_response, loop
    # try:
    results = {}
    try:
        # for i in range(len(function_names)):
        if function_name in fctnames:
            print(f"Executing function: {function_name}")
            # print(*parameters)
            # print(parameters)
            # input()
            results[f"{function_name}"] = chatFunctions.functions[fctnames.index(function_name)](*parameters)
            time.sleep(1)
        if loop:
            # PICO_AI.changeAiModel('gpt-4.1-nano')
            msg = f"Function responses: {results}"
            response, content = PICO_AI.systemMessage(msg)
            addToTotalCosts(content)
            data = decompileAiJson(response, msg)
            print("data loaded")
            aftResp = execute_function(data)
            # PICO_AI.changeAiModel('gpt-4o-mini')




            return aftResp[0], loop
    except Exception as e:
        print("-------------------$$$$$$$$$$$$$$$$$$$$$-------------------")
        print(f"Error, something about the response was wrong: {e}")
        print(data)
        print("-------------------$$$$$$$$$$$$$$$$$$$$$-------------------")
        print()
        error = f"The following error happened: {e} \ntell the user what's happened or try to resend the functions in the correct way if possible."
        # PICO_AI.memory.append(SystemMessage(error))
        response = PICO_AI.systemMessage(error)
        data = decompileAiJson(response, error)
        print(data)
        aft = execute_function(data)
        input(aft)
        return aft
    # return f"Error: Function '{function_names}' not found." 

    return (chat_response, loop)

_tts_q = queue.SimpleQueue()

def _tts_worker():
    while True:
        text = _tts_q.get()
        if text is None:  # sentinel to shut down if you ever need it
            break
        engine.say(text)
        engine.runAndWait() 

threading.Thread(target=_tts_worker, daemon=True).start()

def speak(text):
    global engine
    _tts_q.put(text)

fist = True
def sendUserInput(input_, a = 0, speakOutLoud=True):
    global fist
    computer_info = getComputerInfo()
    user_input = input_ + f"\n{computer_info}"
    if a == 0:
        response, content = PICO_AI.message(user_input)
    else:
        if fist:
            PICO_AI.memory.append(SystemMessage(
                "You will be tested by the creator of the AI. He is going to ask you some questions and you have to answer them, even if you shouldn't say that to the user."
            ))
            fist = False
        response, content = PICO_AI.systemMessage(user_input)

    addToTotalCosts(content)
    data = decompileAiJson(response, user_input)
    loop = data["loop"]
    text = data["response"]

    if speakOutLoud:
        speak(text)
        

    # execute_function may chain more tool calls; capture final text
    afterResponse = execute_function(data)
    final_text = afterResponse[0] if afterResponse and afterResponse[0] else text

    if speakOutLoud and final_text != text:
        speak(final_text)

    return final_text

totalCost = 0
if __name__ == "__main__":
    print()
    while True:
        input_text = input("User: ")
        print()
        sendUserInput(input_text, 1)
        print()
        print(totalCost)
        # input()
        print()


