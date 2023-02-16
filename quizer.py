# This section imports the required modules and libraries
from __future__ import print_function
import random
from googleapiclient.discovery import build
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

import random
import os.path


# This function reads words from a file and returns them as a list
def populate_words_list(filename):
    words = []
    with open(filename, 'r', encoding='utf8') as f:
        for line in f:
            words.append(line.strip())
    return words

# This section gets the path of the current directory and reads words from the file 'words.txt'
dir_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
words = populate_words_list(dir_path+"\\" +'words.txt')


# This section authenticates with Google and initializes the Google Drive API
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# This line sets the URL of the discovery document for the Forms API
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

# This line builds a client object for the Forms API using the discovery.build() method
# It uses the credentials obtained earlier
form_service = discovery.build('forms', 'v1', credentials=gauth.credentials, discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# This section creates a new quiz with a title
NEW_FORM = {
    "info": {
        "title": "Words quiz",
    }
}   



# This section sets the settings for the quiz
SET_SETTINGS = {
"requests": [{
    "updateSettings": {    
    "settings": { 
    "quizSettings": { 
        "isQuiz": "True" }
    },
    "updateMask": "*"

    }

}]      
}

# This function reads questions from a file and returns them as a list of dictionaries
def populate_questions_list(filename):
    questions = []
    with open(filename, 'r', encoding='utf8') as f:
        for line in f:
            question, correct_answer = line.strip().split(',')
            questions.append({
                "question": question,
                "options": [correct_answer],
                "correct_answer": correct_answer
            })
    return questions

# This section reads questions from the file 'questions.txt'
questions = populate_questions_list(dir_path+"\\" +'questions.txt')


# This section creates a dictionary object containing the questions and options for the quiz
NEW_QUESTION = {
    "requests": []
}



# This loop iterates over the list of questions and creates a dictionary for each question
for i, question in enumerate(questions):
    # This line selects a random sample of 7 words from the list of words
    options = random.sample(words, k=7)
    # This line appends the correct answer to the list of options
    options.append(question["correct_answer"])
    # This line shuffles the order of the options
    random.shuffle(options)
    # This line removes duplicate options
    options = list(set(options))
    # next lines append the question and options to the dictionary for the quiz
    NEW_QUESTION["requests"].append({
        "createItem": {
            "item": {
                "title": question["question"],
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [{"value": option} for option in options],
                            "shuffle": True
                        },
                        "grading": {
                            "pointValue": "1",
                            "correctAnswers": {
                                "answers": [{"value": question["correct_answer"]}]
                            }
                        }
                    }
                }
            },
            "location": {
                "index": i
            }
        }
    })


# Creates the initial quiz
result = form_service.forms().create(body=NEW_FORM).execute()

# Sets quiz settings
form_service.forms().batchUpdate(formId=result["formId"], body=SET_SETTINGS).execute()


#print(NEW_QUESTION) 
result = form_service.forms().batchUpdate(formId=result["formId"], body=NEW_QUESTION).execute()

# Prints the result to show the question has been added
#get_result = form_service.forms().get(formId=result["formId"]).execute()
#print(get_result)
