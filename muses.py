#!/usr/bin/python
# -*- coding: utf-8 -*-

import concurrent.futures
import os
import random
import re
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep, time
from uuid import uuid4
import shutil

import nlpcloud # NLP Cloud Playground https://www.nlpcloud.com
import nltk.data # NLP sentence parser used to remove any duplicate word for word sentence output from AI response
import openai # OpenAI https://www.openai.com

# Environment Variables on the Mac
### SAVE IN User home directory
# SceneSimulation % nano ~/.bash-profile
#   export OPENAI_API_KEY=<key>
#   export NLPCLOUD_API_KEY=<key>
#   Ctrl-X to save
### Load the variables in the terminal
# SceneSimulation % source ~/.bash-profile

# OPENAI ENGINE SETUP
AI_ENGINE_OPENAI = 'openai'
open_ai_api_key = os.getenv('OPENAI_API_KEY') # not needed, but for clarity
# NLP CLOUD PLAYGROUND SETUP
AI_ENGINE_NLPCLOUD = 'nlpcloud'
nlp_cloud_api_key = os.getenv('NLPCLOUD_API_KEY') 
# SETUP WHAT AI ENGINE TO USE
SELECTED_AI_ENGINE = AI_ENGINE_OPENAI
# parallelism makes concurrent simulataneous calls to the AI Engine
# From those responses, the best text is determined by length 
# If you want to choose the best of 3 calls for the same next scene, then enter 3 below.
AI_ENGINE_MAX_PARALLELISM = 3

# DEFINE SOME HELPER METHODS
def openFile(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def saveFile(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def mkDirIfNotExists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def nlpcloud_completion(prompt):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            sleep(1) # Wait 1 second because NLP Cloud will error with HTTP 429 too many requests
            client = nlpcloud.Client(
                'finetuned-gpt-neox-20b',
                nlp_cloud_api_key,
                gpu=True,
                lang='en')

            engine_output = client.generation(
                prompt,
                min_length=100,
                max_length=256,
                length_no_input=True,
                remove_input=True,
                end_sequence=None,
                top_p=1,
                temperature=0.85,
                top_k=25,
                repetition_penalty=1,
                length_penalty=1,
                do_sample=True,
                early_stopping=False,
                num_beams=1,
                no_repeat_ngram_size=0,
                num_return_sequences=1,
                bad_words=None,
                remove_end_sequence=False
                )

            text = engine_output['generated_text'].strip()
            text = re.sub('\s+', ' ', text)

            # retry incomplete responses once
            # last character is not some type of sentence ending punctuation
            if not text.endswith(('.','!','?','"')):
                sleep(1) # Wait 1 second because NLP Cloud will error with HTTP 429 too many requests
                engine_output = client.generation(
                    prompt+text,
                    min_length=100,
                    max_length=256,
                    length_no_input=True,
                    remove_input=True,
                    end_sequence=None,
                    top_p=1,
                    temperature=0.85,
                    top_k=25,
                    repetition_penalty=1,
                    length_penalty=1,
                    do_sample=True,
                    early_stopping=False,
                    num_beams=1,
                    no_repeat_ngram_size=0,
                    num_return_sequences=1,
                    bad_words=None,
                    remove_end_sequence=False)
                text2 = engine_output['generated_text'].strip()
                text2 = re.sub('\s+', ' ', text2)

                text = text + ' ' + text2
            
            # retry incomplete responses twice
            # last character is not some type of sentence ending punctuation
            if not text.endswith(('.','!','?','"')):
                sleep(1) # Wait 1 second because NLP Cloud will error with HTTP 429 too many requests
                engine_output = client.generation(
                    prompt+text,
                    min_length=100,
                    max_length=256,
                    length_no_input=True,
                    remove_input=True,
                    end_sequence=None,
                    top_p=1,
                    temperature=0.85,
                    top_k=25,
                    repetition_penalty=1,
                    length_penalty=1,
                    do_sample=True,
                    early_stopping=False,
                    num_beams=1,
                    no_repeat_ngram_size=0,
                    num_return_sequences=1,
                    bad_words=None,
                    remove_end_sequence=False)
                text2 = engine_output['generated_text'].strip()
                text2 = re.sub('\s+', ' ', text2)

                text = text + ' ' + text2

            filename = '%s_nlpcloud.txt' % time()

            mkDirIfNotExists('nlpcloud_logs')

            saveFile('nlpcloud_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "NLPCLOUD error: %s" % oops
            print('Error communicating with NLP Cloud:', oops)
            sleep(1)

def gpt3_completion(prompt, engine='text-davinci-002', temp=0.75, top_p=1.0, tokens=256, freq_pen=0.0, pres_pen=0.0, stop=['zxcv']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)

            # retry incomplete responses once
            # last character is not some type of sentence ending punctuation
            if not text.endswith(('.','!','?','"')):
                response = openai.Completion.create(
                    engine=engine,
                    prompt=prompt+text,
                    temperature=temp,
                    max_tokens=tokens,
                    top_p=top_p,
                    frequency_penalty=freq_pen,
                    presence_penalty=pres_pen,
                    stop=stop)
                text2 = response['choices'][0]['text'].strip()
                text2 = re.sub('\s+', ' ', text2)

                text = text + text2

            # retry incomplete responses twice
            # last character is not some type of sentence ending punctuation
            if not text.endswith(('.','!','?','"')):
                response = openai.Completion.create(
                    engine=engine,
                    prompt=prompt+text,
                    temperature=temp,
                    max_tokens=tokens,
                    top_p=top_p,
                    frequency_penalty=freq_pen,
                    presence_penalty=pres_pen,
                    stop=stop)
                text2 = response['choices'][0]['text'].strip()
                text2 = re.sub('\s+', ' ', text2)

                text = text + text2
            
            filename = '%s_gpt3.txt' % time()

            mkDirIfNotExists('openai_logs')

            saveFile('openai_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "OpenAI error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def callAIEngine(prompt):
    scene = ''
    print('\n======================= CALLING AI ENGINE =======================')
    print('\n',prompt)
    if SELECTED_AI_ENGINE == AI_ENGINE_OPENAI:
        scene = gpt3_completion(prompt)
    if SELECTED_AI_ENGINE == AI_ENGINE_NLPCLOUD:
        scene = nlpcloud_completion(prompt)

    print('\n',scene,'\n','=======================')
    return scene

def cleanUpAIengineOutput(text):
    text = re.sub(r'[1-9]+\.\s?', '\r\n', text)
    text = text.replace(': ','-')
    text = os.linesep.join([s for s in text.splitlines() if s])       
    return text

def OnlyFirstParagraph(this_text):
    retval = ''
    this_text = this_text.strip() # remove spaces
    lines = this_text.splitlines()
    if lines[0]:
        retval = lines[0]
    return retval

def removeAnyPreviousLines(this_text, previous_scene):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    thisLines = tokenizer.tokenize(this_text)
    previousLines = tokenizer.tokenize(previous_scene)

    textArray = [];
    for thisLine in thisLines:
        lineGood = True
        for previousLine in previousLines:
            if thisLine == previousLine:
                lineGood = False
        if lineGood:
            textArray.append(thisLine)

    return ' '.join(textArray).strip()

# MAIN PROGRAM
if __name__ == '__main__':

    # SOME TEXT LOOP VARIABLES
    previous_scene = 'Grath was at Greybeard''s magical forge deep within the Azor mountain range.'
    characters = 'Grath Zeras - Orc warrier; master at arms for the Veserak orc clan.'
    summary = 'In Raevel territory there is a village called Debus who makes tribute to a great fire dragon that powers the volcano deep inside Azor mountain.'
    protagonist = 'Grath Zeras'

    # CREATE STORY.TXT, CLEARING IT OUT
    file1 = open('story.txt', 'w')  # write mode
    file1.close()

    if os.path.exists('SceneOutput'):
        shutil.rmtree('SceneOutput', ignore_errors=False, onerror=None)

    # GENERATE PARAGRAPHS
    for i in range(0,15):

        # RANDOM PLOT QUEUES FED INTO THE PROMPT
        plot_twists = openFile('sceneGenData/plotqueues.txt').splitlines()
        plot_twist = random.choice(plot_twists)

        # CREATE A NEW SCENE
        prompt = openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_scene_next.txt').replace('<<PREVIOUS>>',previous_scene).replace('<<CHARACTERS>>',characters).replace('<<SUMMARY>>',summary).replace('<<PLOT>>', plot_twist).replace('<<PROTAGONIST>>', protagonist)

        # HOW MANY TIMES TO REGEN THE SAME PARAGRAPH
        prompts = []
        for j in range (0,AI_ENGINE_MAX_PARALLELISM):
            prompts.append(prompt)

        # MULTIPLE SIMULTANEOUS CONCURRENT CALLS TO AI ENGINE
        prompt_queue = []
        with ThreadPoolExecutor(max_workers=AI_ENGINE_MAX_PARALLELISM) as executor:
            ordinal = 1
            for prompt in prompts:
                prompt_queue.append(executor.submit(callAIEngine, prompt))
                ordinal += 1

        # WAIT FOR ALL SIMULTANEOUS CONCURRENT CALLS TO COMPLETE
        # LOOP TO FIND THE LONGEST PARAGRAPH
        longest_text = ''
        longest_text_length = 0
        for future in concurrent.futures.as_completed(prompt_queue):
            #prompt = prompt_queue[future]
            try:
                generated_text = future.result()

                # NLP CLOUD CREATES USUALLY A GOOD FIRST PARAGRAPH, BUT THEN GARBAGE
                if SELECTED_AI_ENGINE == AI_ENGINE_NLPCLOUD:
                    generated_text = OnlyFirstParagraph(generated_text)


                if not (generated_text.find(previous_scene) > 0):
                    #print('%r generated: %s' % (prompt, generated_text))
                    if generated_text:
                        generated_text = removeAnyPreviousLines(generated_text, previous_scene)
                        len_this_generated_text = len(generated_text)
                        if len_this_generated_text > longest_text_length:
                            longest_text_length = len_this_generated_text
                            longest_text = generated_text
                            print('\n=== BEST SO FAR ====> %d size \n%s' % (len_this_generated_text, generated_text))    
                        else:
                            print('\n=== NOT BEST ========> %d size \n%s' % (len_this_generated_text, generated_text))    
                    else:
                        print('\n\ngenerated blank')
            except Exception as exc:
                print('\n\ngenerated an exception: %s' % (exc))

        if longest_text_length == 0:
            print('generated dupe: %s' % (longest_text))
        else:
            # add vivid sensory
            prompt = openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_story_sensory.txt').replace('<<STORY>>',longest_text)
            longest_text = callAIEngine(prompt)

            # remove any previous scene verbatim lines if they are reintroduced with vivid sensory
            longest_text = removeAnyPreviousLines(longest_text, previous_scene)

            print('\n== CHOSEN LONGEST LENGTH ==> %d size \n%s' % (longest_text_length, longest_text))    
            previous_scene = longest_text
            mkDirIfNotExists('SceneOutput')
            saveFile('SceneOutput/%d.txt' % i, longest_text)

            # ================================== NEW CHARACTERS ==================================
            prompt = openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_character_finder.txt').replace('<<CHARACTERS>>',characters).replace('<<SCENE>>',previous_scene)

            new_characters = callAIEngine(prompt)
            #print('\n====NEW CHARS=======> \n%s' % (new_characters)) 
            new_characters = cleanUpAIengineOutput(new_characters)
            #print('\n====NEW CHARS=======> \n%s' % (new_characters)) 
            characters = characters + '\r\n' + new_characters
            print('\n====NEW CHARS=======> \n%s' % (characters)) 

            #if (SELECTED_AI_ENGINE == AI_ENGINE_OPENAI): # doing this in one shot with NLP CLOUD
            if False:
                # ================================== CHARACTER CLEANUP ==================================
                prompt = openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_character_cleanup.txt').replace('<<CHARACTERS>>',characters)

                new_characters = callAIEngine(prompt)
                #print('\n====CHAR CLEANUP=======> \n%s' % (new_characters)) 
                characters = cleanUpAIengineOutput(new_characters)
                print('\n====CHAR CLEANUP=======> \n%s' % (characters)) 

            # ================================== CHARACTER DETAILS ==================================
            prompt = openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_character_details.txt').replace('<<CHARACTERS>>',characters).replace('<<SCENE>>',previous_scene)

            new_characters = callAIEngine(prompt)
            #print('\n====CHAR DETAILS=======> \n%s' % (new_characters)) 
            characters = cleanUpAIengineOutput(new_characters)
            print('\n====CHAR DETAILS=======> \n%s' % (characters)) 

            file1 = open('story.txt', 'a')  # append mode
            #file1.write('===== CHARS =====\r\n')
            #file1.write(longest_text + '\r\n')
            #file1.write('===== STORY =====\r\n')
            file1.write(longest_text + '\r\n')
            file1.close()

            prompt = openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_story_summary.txt').replace('<<STORY>>',summary + '\r\n' + longest_text)
            summary = callAIEngine(prompt)
