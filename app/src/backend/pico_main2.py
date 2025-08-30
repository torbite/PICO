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

#### --- GET PICO INSTRUCTIONS PROMPT AND LOAD AI --- ####

funcDocs = {}
for i in chatFunctions.functions:
   funcDocs[i.__name__] = i.__doc__

mainInstructions = ""
aiPersonality = ""
with open("../../PICO_AI_Instructions/mainInstructions.txt", 'r') as file:
    mainInstructions = file.read()
with open("../../PICO_AI_Instructions/aiPersonality.txt", 'r') as file:
    aiPersonality = file.read()

userInformation = f""""""
functionsInformation = f"""The available functions are: {funcDocs}"""

functions_prompt = f"{mainInstructions}\n {functionsInformation}\n {aiPersonality}\n {userInformation}"

PICO_AI = chatFunctions.AI_character(functions_prompt)
# PICO_AI = chatFunctions.AI_character(llamaPrompt, False)
# PICO_AI.changeAiModel("gpt-4.1-nano")

### --- USE PICO FUNCTIONS --- ###

def decompileJson(json_response):
    try:
        data = json.loads(json_response)
        return data
    except Exception as e:
        return f"error while loading json: {e}"
    
function_names = [i.__name__ for i in chatFunctions.functions]
# function_names = []
def executeFunction(function_name, parameters):
    global function_names

    if not function_name in function_names:
        return "function does not exist"
    try:
        result = chatFunctions.functions[function_names.index(function_name)](*parameters)
    except Exception as e:
        print(f"error, {e}")
        result = e
    return result

def handleData(data: list):
    global PICO_AI
    all_present = all(s in data.keys() for s in ['response', 'function', 'parameters'])
    if not all_present:
        print("\nNOT ALL PRESENT")
        print(data)
        raise KeyError("data keys not correct")
    
    # response = data["response"]

    function_name = data["function"]
    parameters = data["parameters"]
    
    while function_name != None and function_name != "":
        print("")
        print("EXECUTING FUNVCTION")
        print(function_name, parameters)
        print()
        response = data["response"]
        yield response
        result = executeFunction(function_name, parameters)
        message = f"function {function_name} executed and returned {result}"
        pico_response = PICO_AI.systemMessage(message)
        data = decompileJson(pico_response)
        print(pico_response)
        print(data)
        # input()
        function_name = data["function"]
        parameters = data["parameters"]

    yield data["response"]
    return data["response"]

    


def getPicoResponse(user_input):
    computerInfo = chatFunctions.getComputerInfo()
    time2 = time.time()
    inp = f'Computer Info: {computerInfo}\nPrompt: {user_input}'
    response = PICO_AI.message(inp)
    data = decompileJson(response)
    seggages_ment = []
    try:
        for response in handleData(data):
            seggages_ment.append(response)
            yield(response)
    except Exception as e:
        print(data)
        print(e)
        return "error"
    # text = data["response"]
    return seggages_ment

print()
if __name__ == "__main__":
    while True:
        r = input("--> ")
        time1 = time.time()
        print()
        for resp in getPicoResponse(r):
            print(resp)
        print()
        time2 = time.time()
        dt = time2- time1
        print(dt)