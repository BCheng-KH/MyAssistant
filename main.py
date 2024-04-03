import os
from os import system
from dotenv import load_dotenv
import speech_recognition as sr
import sys, whisper, warnings, time, json
from openai import OpenAI

from tools import tools, restricted_tools, execute_tool

import pyttsx3
engine = pyttsx3.init()
# Wake word variables
WAKE_WORD = "sushi"

# Initialize the OpenAI API
load_dotenv(override=True)
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
)
device = 'USB 2.0 Camera: Audio (hw:2,0)'
#device = 'Blue Snowball: USB Audio (hw:3,0)'

r = sr.Recognizer()
tiny_model = whisper.load_model('tiny.en')
base_model = whisper.load_model('base.en')
listening_for_wake_word = True
#print("using snowball:", device in sr.Microphone.list_microphone_names())
source = sr.Microphone(device_index=sr.Microphone.list_microphone_names().index(device)) 
warnings.filterwarnings("ignore", category=UserWarning, module='whisper.transcribe', lineno=114)


messages = [{"role": "system", "content": "You are a helpfull assistant named Sushi. When responding to the user, please perform all function calls before providing a text response."}]


def speak(text):

    engine.say(text)
    engine.runAndWait()

def listen_for_wake_word(audio):
    global listening_for_wake_word
    with open("wake_detect.wav", "wb") as f:
        f.write(audio.get_wav_data())
    result = base_model.transcribe('wake_detect.wav', initial_prompt=f'Please look for a clear instance of the keyword: {WAKE_WORD}')
    text_input = result['text']
    if WAKE_WORD in text_input.lower().strip():
        print("Listening")
        speak('Listening')
        listening_for_wake_word = False



def gpt_chat_loop(question):
    global messages
    messages.append({"role": "user", "content": question})
    response = None
    clear_history = False
    while response == None or response.choices[0].message.content == None:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            temperature=0.5,
            max_tokens=500,
            tools=tools,
            tool_choice="auto"
        )
        if response.choices[0].message.tool_calls != None:
            for tool_call in response.choices[0].message.tool_calls:
                print("Calling: ", tool_call.function.name)
                if tool_call.function.name == "clear_chat_history":
                    clear_history = True
                    messages.append({"role": "system", "content": "The chat history has been wiped."})
                else:
                    messages.append(execute_tool(tool_call))
        messages.append({"role": "system", "content": "Once you have executed all the nessesary functions, or need to prompt the user for more information, please provide the user with a textual response."})
    response_text = response.choices[0].message.content
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=500,
        tools=restricted_tools,
        tool_choice={"type": "function", "function": {"name": "speak"}}
    )
    spoken_response = json.loads(response.choices[0].message.tool_calls[0].function.arguments)["text"]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=500,
        tools=restricted_tools,
        tool_choice={"type": "function", "function": {"name": "continue_chat"}}
    )
    get_followup = (json.loads(response.choices[0].message.tool_calls[0].function.arguments)["wait_for_followup"] == "True")
    if clear_history:
        messages = messages[:1]
    return response_text, spoken_response, get_followup




def prompt_gpt(audio):
    global listening_for_wake_word
    try:
        with open("prompt.wav", "wb") as f:
            f.write(audio.get_wav_data())
        audio_file= open("prompt.wav", "rb")
        result = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        prompt_text = result.text
        if len(prompt_text.strip()) == 0:
            print("Empty prompt. Please speak again.")
            speak("Empty prompt. Please speak again.")
            listening_for_wake_word = True
        else:
            print("Asking:", prompt_text)
            response_text, spoken_response, get_followup = gpt_chat_loop(prompt_text)
            print("Assistant:", response_text)
            speak(spoken_response)
            listening_for_wake_word = not(get_followup)
            if get_followup:
                print("Listening")
                speak('Listening')

    except Exception as e:
        print("Prompt error: ", e)

def callback(recognizer, audio):
    global listening_for_wake_word
    if listening_for_wake_word:
        listen_for_wake_word(audio)
    else:
        prompt_gpt(audio)

def start_listening():
    r.dynamic_energy_ratio *= 3
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    r.dynamic_energy_threshold = True
    r.pause_threshold = 1
    print(f'\nSay {WAKE_WORD} to wake me up. \n')
    r.listen_in_background(source, callback, phrase_time_limit=60)
    while True:
        time.sleep(0.1)

if __name__ == '__main__':
    start_listening() 