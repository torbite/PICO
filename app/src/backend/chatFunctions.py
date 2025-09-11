from langchain_community.chat_models import ChatOllama
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage, FunctionMessage
import pyautogui as gui, numpy as np, cv2, time, copy, os
import yoloFunctions as yf
import json, ast, re
import pyautogui as gui
import subprocess, platform, datetime
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class AI_character():
    def __init__(self, objective, ai_model = "gpt-5-nano"):
        self.model = ChatOpenAI(model=ai_model, temperature=1)
        # self.model = ChatOllama(model="llama3")
        self.objective = objective
        self.models = ['gpt-4o-mini','gpt-5-nano','gpt-4', 'gpt-4.1-nano', 'gpt-5-mini']
        self.memory = [
            SystemMessage(objective)
        ]
    
    def message(self, user_message):
        self.memory.append(HumanMessage(user_message))
        content = self.model.invoke(self.memory)
        response = content.content
        self.memory.append(AIMessage(response))
        return response#, content
    
    def systemMessage(self, system_message):
        self.memory.append(SystemMessage(system_message))
        content = self.model.invoke(self.memory)
        response = content.content
        self.memory.append(AIMessage(response))
        return response#, content
    
    def resetMemory(self):
        self.memory = [
            SystemMessage(self.objective)
        ]
    
    def changeAiModel(self, modelName):
        if modelName in self.models:
            self.model = ChatOpenAI(model=modelName)

    def get_messages_to_text(self):
        messages = self.memory
        parts = []
        for m in messages:
            content = getattr(m, "content", None)
            parts.append(str(content) if content is not None else str(m))
        return "\n".join(parts)
        


class AI_builder():
    def __init__(self, objective, ai_model = "gpt-4.1-nano"):
        self.model = ChatOpenAI(model=ai_model, temperature=1)
        # self.model = ChatOllama(model="llama3")
        self.objective = objective
        self.memory = [
            SystemMessage(objective)
        ]
    
    def message(self, user_message):
        mem = copy.deepcopy(self.memory)
        mem.append(HumanMessage(user_message))
        response = self.model.invoke(mem).content
        return response
    
    def systemMessage(self, system_message):
        self.memory.append(SystemMessage(system_message))
        response = self.model.invoke(self.memory).content
        self.memory.append(AIMessage(response))
        return response


# --------------------------------------------------- # --------------------------------------------------- #
# ------------------------------------------ BASE CHAT FUNCTIONS ------------------------------------------ #
# --------------------------------------------------- # --------------------------------------------------- #

def getComputerInfo():
    """This function gets the computer information and returns it as a dictionary"""
    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(local_tz)
    info = {}
    screen = yf.getCurrentScreenImage()
    apps = yf.getModelPrediction("find_app", screen)
    info["open_apps"] = list(apps.keys()) if len(list(apps.keys())) > 0 else "No apps are open"
    info["os"] = platform.system()
    info["current_day"] = f"year {now.year}| month {now.strftime('%m')}| day {now.strftime('%d')}|"
    info["current_time"] = now.strftime("%H:%M:%S")
    return info

def writeText(text):
    """This function takes a string and writes it to the screen"""
    gui.hotkey('command', 'a')
    gui.hotkey('command', 'a')
    time.sleep(0.2)
    gui.typewrite(text)
    time.sleep(0.5)
    return None


app_search = AI_builder("""You are an AI that can only respond True or False, nothing else.
                            You will receive a list from the user and you will need to know whether an app x is in the list or not.
                           Example:
                           User input: "Is the app Whatsapp in the list? ["whatsapp", "spotify", "youtube"]"
                           Expected response: True
                           """)
def checkIfAppIsOppened(app_name):
    global app_search
    screen = yf.getCurrentScreenImage()
    results = yf.getModelPrediction("find_app", screen)
    apps = results.keys()
    isThereApp = app_search.message(f"Is the app {app_name} in the list? {apps}")
    response = False
    if "true" in isThereApp.lower():
        response = True
    elif "false" in isThereApp.lower():
        response = False
    
    return response
    



# --------------------------------------------------- # --------------------------------------------------- #
# ------------------------------------------ APPS CHAT FUNCTIONS ------------------------------------------ #
# --------------------------------------------------- # --------------------------------------------------- #

def addNumbers(a, b):
    """Params: a -> float and b -> float. This function takes two numbers and returns the sum of a + b"""
    return a + b

def multiplyNumbers(a, b):
    """Params: a -> float and b -> float. This function takes two numbers and returns the product of a * b"""
    return a*b

first_time = True
def openApp(app_name, plataform):
    """Params: app_name, plataform. put the name of the app and that app gets oppened. for example: user input -> "Open the whatsapp app" : then set the parameter to WhatsApp". You also need to set the plataform to the user's plataform, being the ONLY possible ones "windows" or "mac". do not send "darwin" or "linux" or anything else. Just "windows" or "mac". Returns if app was oppened or not."""
    global first_time
    appHasOppened = checkIfAppIsOppened(app_name)
    a = 3
    while not appHasOppened:

        if plataform == "windows":
            gui.hotkey('winleft', 's')
            time.sleep(0.1)           
            gui.write(app_name)          
            time.sleep(0.1)
            gui.press('enter') 

        if plataform == "mac":
            if first_time:
                gui.hotkey('command', 'space')
                first_time = False
            gui.hotkey('command', 'space')
            time.sleep(0.1)
            gui.write(app_name)          
            time.sleep(0.1)
            gui.press('enter')
            time.sleep(1)
            appHasOppened = checkIfAppIsOppened(app_name)
        
        a -= 1
        if a == 0:
            break
           
    time.sleep(0.25)
    # input("a") 
    return f"The app {app_name} has been oppened"



search_name_AI = AI_builder("""Você é um assistente que só responde com a posicao de um objeto.
        Dado um dicionário com objetos e suas posições, responda apenas com a posicao (uma tupla de dois pares de coordenadas).

        Exemplo:
        Input: {'people': [['Marina Sanches', ((10,20),(20,13)), 'Berlin'], ['Tiago Delgado', ((11,34),(14,23)), 'Brazil']]}
        Pergunta: “Qual a posicao onde o nome da pessoa é Marina?”

        Sua resposta deve ser apenas: ((10, 20), (20, 13))
        Also make sure to put the name of the closest one. for example, if the user says 'mother' as the name, and there is a person named 'mother' and another named 'friend's mother' then the correct one is 'mother'""")
# app_search.
def sendMessageOnWhatsApp(conversation_name, messages):
    """This functions params are 'conversation_names' : str and 'messages' : list.
    It sends the messages, in order, to the target conversation. 
    The messages cannot be sent by the AI pretending to be the user, when writing the message, make sure to specify that it's you writing, by saying "Hello, it's -Name- here! etcetera. 
    Make sure to write the messages normally, but please try to always write a lot of text instead of a little bit.
    Usually prefer to separate the messages in a bunch of messages, instead of writing a single message. Please usually send a bunch of messages.
    The function does not oppens the whatsappApp by itself. So make sure to open the app before calling this function.
    Final reminder: This function does not send messages to multiple people at once, in case you want to send messages to more than one person, make sure to call it twice and set the parameters to the two different functions.
    Returns if the message was sent or not."""
    global search_name_AI
    screen = yf.getCurrentScreenImage()
    predictions = yf.getModelPrediction("WhatsApp",screen)
    # element_classes = yf.getTextFromImage(screen, predictions)
    if "search_conversation_bar" not in predictions.keys():
        # print("No search bar found")
        raise KeyError("No search bar found. This likely means that the app is not open. Make sure to open the app before calling this function.")
    Search_bar = predictions["search_conversation_bar"][0]
    yf.clickOnElement(Search_bar)
    writeText(conversation_name)
    screen = yf.getCurrentScreenImage()

    predictions = yf.getModelPrediction("WhatsApp",screen)
    element_classes = yf.getTextFromImage(screen, predictions)
    people = element_classes["conversation_box"]

    answer = search_name_AI.message(f"""input: {people} 
                               pergunta: Qual a posicao onde o nome da pessoa é {conversation_name}?""")

    # print(answer)

    textList = list(answer)
    count_a = 0
    count_b = 0
    for i in textList:
        if i == "(":
            count_a += 1
        if i == ")":
            count_b += 1
    
    while count_a > 3:
        textList.remove("(")
        count_a-= 1
    
    # while count_b > 4:  
    #     textList.remove(")")
    #     count_b-= 1

    anw = "".join(textList)

    def extract_tuple(text):
        numbers = list(map(int, re.findall(r'\d+', text)))
        if len(numbers) == 4:
            return ((numbers[0], numbers[1]), (numbers[2], numbers[3]))
        else:
            print(text)
            raise ValueError("Couldn't find exactly 4 numbers in the text. This likely means that the conversation name was not found. Please check the name and try again or tell the user.")

    pos = extract_tuple(anw)
    # print(anw)
    # input()
    # pos = ast.literal_eval(anw)
    yf.clickOnElement(pos)
    if "send_message_bar" not in predictions.keys():
        predictions = yf.getModelPrediction("WhatsApp",screen)
        if "send_message_bar" not in predictions.keys():
            print("No send message area found")
            raise KeyError("No send message area found. This likely means that the app is not open. Make sure to open the app before calling this function.")
    send_area = predictions["send_message_bar"][0]
    # print(send_area)
    # input()
    if isinstance(messages, list):
        for message in messages:
            yf.clickOnElement(send_area)
            writeText(message)
            gui.press("enter")
            time.sleep(0.25)
        return "messages sent"
    
    yf.clickOnElement(send_area)
    writeText(messages)
    gui.press("enter")
    time.sleep(0.25)
    return "message sent"

functions = [addNumbers, multiplyNumbers,sendMessageOnWhatsApp, openApp]

if __name__ == "__main__":
    # sendMessageOnWhatsApp("Marina", "Hello, this is another test message from the AI")
    # openApp("WhatsApp", "mac")
    sendMessageOnWhatsApp("Marina", "Hello, this is a test message from the AI")
     # image = yf.getCurrentScreenImage()
    # print(type(image))
    # predictions = yf.getModelPrediction("WhatsApp",image)
    # element_classes = yf.getTextFromImage(image, predictions)
    # for key in element_classes.keys():
    #     for element in element_classes[key]:
    #         yf.clickOnElement(element)
    #         time.sleep(1)

# hya there friendo, could you please send a message to mag just saying hi? my name is liz btw