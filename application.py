
from __future__ import print_function
import os
import openai
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import re
import pyaudio
import wave
from pydub import AudioSegment
from deepgram import Deepgram
import json
import os
import sounddevice as sd
import soundfile as sf
import streamlit as st
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
st.title("Welcome to our application! 🤗")
st.markdown("Please tell us about what you would make the form ... 📝")
# Enregistrement audio
if st.button("Start Recording.."):
    # Paramètres d'enregistrement
    sample_rate = 44100
    duration = 10  # Durée d'enregistrement en secondes

    # Enregistrement audio
    audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1)
    sd.wait()  # Attendez la fin de l'enregistrement

    # Enregistrez le fichier audio temporaire
    temp_file = "temp.wav"
    sf.write(temp_file, audio, sample_rate)

    if st.success("Recording saved "):
        # Traitement audio
        #if os.path.exists("temp.wav"):
            #st.audio("temp.wav", format="audio/wav")

        #st.info("Wait for us a minute please ....")

        #############################
        dg_key = '5d1fdcf0fd456264b0906048643058a76072a4a2'
        dg = Deepgram(dg_key)
        MIMETYPE = 'wav'
        def transcribe_audio(audio_file):
            options = {
                "punctuate": True,
                "model": 'general',
                "tier": 'enhanced',
                #"language": 'fr-FR'
            }

            if audio_file.endswith(MIMETYPE):
                output_file = os.path.join(os.path.dirname(audio_file), f"{os.path.basename(audio_file)[:-4]}.json")
                with open(audio_file, "rb") as f:
                    source = {"buffer": f, "mimetype": 'audio/' + MIMETYPE}
                    try:
                        res = dg.transcription.sync_prerecorded(source, options)
                        with open(output_file, "w") as transcript:
                            json.dump(res, transcript)
                        return output_file
                    except Exception as e:
                        print("Error occurred during transcription:", str(e))
            else:
                print("Invalid audio file format. Supported formats:", MIMETYPE)
            return None


        # Example usage
        audio_file = "temp.wav"  # Replace with the recorded audio file name
        transcription_output = transcribe_audio(audio_file)
        if transcription_output:
            print("Transcription output file:", transcription_output)


        # Set this variable to the path of the output file you wish to read
        OUTPUT = r'temp.json'


        # The JSON is loaded with information, but if you just want to read the
        # transcript, run the code below!
        def print_transcript(transcription_file):
            with open(transcription_file, "r") as file:
                    data = json.load(file)
                    result = data['results']['channels'][0]['alternatives'][0]['transcript']
                    result = result.split('.')
                    return result[0]

        Text_=print_transcript(OUTPUT)

        mot_cle = "form"
        # Trouver l'index du mot clé
        index_mot_cle = Text_.index(mot_cle)
        # Extraire la phrase à partir de l'index du mot clé
        phrase = Text_[index_mot_cle:]
        st.write(" You want make a: "+phrase +"? " )
        st.write("if not ❌, please retry the recording !")
        # Load your API key from an environment variable or secret management service
        #openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = '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'

        def resumer(text):
            return openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.5,
            max_tokens=2000
            ).choices[0].text.strip()
        requests="Give me 10 questions Listed (1,2,3,..) with possible answers in the format of couples with the type of answers (text box, multiple choice, single choice) and the answers are separated by commas in the same line of the question to build a form"
        input=requests+phrase
        response=resumer(input)
        #print(response)
        SCOPES = "https://www.googleapis.com/auth/forms.body"
        DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

        store = file.Storage('token.json')
        
        credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/drive'])
        

        # Request body for creating a form
        NEW_FORM = {
            "info": {
                "title": "form",
            }
        }
        form_service = build('forms', 'v1', credentials=credentials)
        form = form_service.forms().create(
        body=NEW_FORM 
        ).execute()
        #Build questions with type of response
        Single_Choice=[]
        Text_Box=[]
        Multiple_Choice=[]
        Single_Choice_question=[]
        Text_Box_question=[]
        Multiple_Choice_question=[]

        for question in response.split('\n'):
            type_ = re.search(r'\((.*?)\)', str(question)).group(1)
            if type_=="Single Choice":
                Single_Choice.append(question)
            if type_=="Text Box":
                Text_Box.append(question)
            if type_=="Multiple Choice":
                Multiple_Choice.append(question)

        for e in Single_Choice:
            start_index = e.index('.') + 2
            end_index = e.index('?')
            extracted_text = e[start_index:end_index].strip()+"?"
            start_index = e.index(')') + 1
            options_liste = e[start_index:].strip().split(',')[:-1]
            options = [{"value": item} for item in options_liste]
            q={
            "requests": [{
                "createItem": {
                    "item": {
                        "title": extracted_text,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": options,
                                    "shuffle": True
                                }
                            }
                        },
                    },
                    "location": {
                        "index": 0
                    }
                }
            }]
        }
            Single_Choice_question.append(q)
            

        for e in Text_Box:
            start_index = e.index('.') + 2
            end_index = e.index('?')
            extracted_text = e[start_index:end_index].strip()+"?"
            q={
            "requests": [{
                "createItem": {
                    "item": {
                        "title":extracted_text ,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {}
                            }
                        }
                    },
                    "location": {
                        "index": 0
                    }
                }
            }]
        }
            Text_Box_question.append(q)


        for e in Multiple_Choice:
            start_index = e.index('.') + 2
            end_index = e.index('?')
            extracted_text = e[start_index:end_index].strip()+"?"
            start_index = e.index(')') + 1
            options_liste = e[start_index:].strip().split(',')[:-1]
            options = [{"value": item} for item in options_liste]
            q={
            "requests": [{
                "createItem": {
                    "item": {
                        "title": extracted_text,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "CHECKBOX",
                                    "options": options,
                                    "shuffle": True
                                }
                            }
                        },
                    },
                    "location": {
                        "index": 0
                    }
                }
            }]
        }
            Multiple_Choice_question.append(q)

        # Group the question with a liste format
        Questions=Single_Choice_question+Text_Box_question+Multiple_Choice_question    
        # Request body to add a multiple-choice question


        # Creates the initial form
        result = form_service.forms().create(body=NEW_FORM).execute()

        # Adds the question to the form
        for question in Questions:
            question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=question).execute()
        # Prints the result to show the question has been added
        get_result = form_service.forms().get(formId=result["formId"]).execute()
        st.info("Wait for us a minute please ....")
        st.title("Congratulations 🥳 ! You got your form ready to share and explore it")
        st.info(get_result["responderUri"])

        #print(Multiple_Choice_question)
