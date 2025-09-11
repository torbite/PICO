import pyttsx3, asyncio, threading, queue
import langchain_core
from langchain_community.chat_models import ChatOllama
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage, FunctionMessage
import chatFunctions as chatFunctions, yoloFunctions as yf, audioFunctions as af
import os, copy
import json, re
import platform, time
import datetime
import zoneinfo

#### --- GET PICO INSTRUCTIONS PROMPT AND LOAD AI --- ####

speaker = af.speakerThing(rate=180, volume=0.9, debug=True)

funcDocs = {}
for i in chatFunctions.functions:
   funcDocs[i.__name__] = i.__doc__

consiousnessInstructions = ""
picoInstructions = ""
aiPersonality = ""
with open("../../PICO_AI_Instructions/consiousnessInstructions.txt", 'r') as file:
    mainInstructions = file.read()
with open("../../PICO_AI_Instructions/picoInstructions.txt", 'r') as file:
    picoInstructions = file.read()
with open("../../PICO_AI_Instructions/aiPersonality.txt", 'r') as file:
    aiPersonality = file.read()

# userInformation = f""""""
functionsInformation = f"""The available functions are: {funcDocs}"""

consiousness_prompt = f"{mainInstructions}\n {functionsInformation}"
pico_prompt = f"{picoInstructions}\n{aiPersonality}\nHere is a list of everything that can be executed. The given action is not possible say you cannot do it {functionsInformation}"

PICO_AI = chatFunctions.AI_character(pico_prompt, "gpt-4.1-nano")
CONSIOUSNESS_AI = chatFunctions.AI_character(consiousness_prompt, "gpt-5-nano")

### --- USE PICO FUNCTIONS --- ###

def decompileJson(json_response):
    try:
        data = json.loads(json_response)
        return data
    except Exception as e:
        print(json_response)
        print(f"error while loading json: {e}")
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
    global CONSIOUSNESS_AI
    all_present = all(s in data.keys() for s in ['function', 'parameters'])
    if not all_present:
        print("\nNOT ALL PRESENT")
        print(data)
        raise KeyError("data keys not correct")
    
    # response = data["response"]

    function_name = data["function"]
    parameters = data["parameters"]
    
    messages = []

    while function_name != None and function_name != "":
        try:
            result = executeFunction(function_name, parameters)
            message = f"function {function_name} executed and returned {result}"
        except Exception as e:
            message =  f"function {function_name} tried to be executed but errored: {e}"
        messages.append(message)
        # all_mem = CONSIOUSNESS_AI.get_messages_to_text()
        # tokens = re.split(r"[ \n]+", all_mem)
        # print("tokens of CONSIOUSNESS memory: ", len(tokens))
        pico_response = CONSIOUSNESS_AI.systemMessage(message)
        # print(f"response CONSIOUSNESS token len = {len(pico_response)}" )
        data = decompileJson(pico_response)
        function_name = data["function"]
        parameters = data["parameters"]
    
    final_message = "\n".join(messages)
    return final_message
    


def getPicoResponse(user_input):
    # print("aaaaaa")
    global PICO_AI, CONSIOUSNESS_AI, speaker
    CONSIOUSNESS_AI.resetMemory()
    computerInfo = chatFunctions.getComputerInfo()
    time2 = time.time()
    inp = f'Computer Info: {computerInfo}\nPrompt: {user_input}'
    response = PICO_AI.message(inp)
    # print(f"response token len = {len(response)}" )
    data = decompileJson(response)
    user_response = data["user_response"]
    prompt = data["prompt"]

    yield user_response
    speaker.speak(user_response)
    if not prompt:
        return
    

    # all_mem = CONSIOUSNESS_AI.get_messages_to_text()
    # tokens = re.split(r"[ \n]+", all_mem)
    # print("tokens of CONSIOUSNESS memory: ", len(tokens))

    consiousness_response = CONSIOUSNESS_AI.message(inp + "\n" + prompt)

    # print(f"response CONSIOUSNESS token len = {len(consiousness_response)}" )

    data = decompileJson(consiousness_response)

    try:
        retult = handleData(data)
        finalResponse = PICO_AI.systemMessage(f"The functions responses: {retult}. Now explain to the user what's happened")
        data = decompileJson(finalResponse)
        finalUserResponse = data["user_response"]
        speaker.speak(finalUserResponse)
        speaker.wait_until_done()
        yield finalUserResponse
        return finalUserResponse
    except Exception as e:
        # print(data)
        print(e)
        yield "error"
    # text = data["response"]
    return

print()
if __name__ == "__main__":
    # print("PICO_AI id:", id(PICO_AI), "mem id:", id(PICO_AI.memory))
    # print("CONS  id:", id(CONSIOUSNESS_AI), "mem id:", id(CONSIOUSNESS_AI.memory))
    # input()
    while True:
        r = input("--> ")
        time1 = time.time()
        print()
        for resp in getPicoResponse(r):
            print(resp)
        print()
        time2 = time.time()
        dt = time2- time1
        # print(dt)
        # all_mem = PICO_AI.get_messages_to_text()
        # tokens = re.split(r"[ \n]+", all_mem)
        # print("tokens of PICO memory: ", len(tokens))
