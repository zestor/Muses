#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import random
import shutil
from python.MusesHelper import MusesHelper

# Environment Variables on the Mac
### SAVE IN User home directory
# SceneSimulation % nano ~/.bash-profile
#   export OPENAI_API_KEY=<key>
#   export NLPCLOUD_API_KEY=<key>
#   Ctrl-X to save
### Load the variables in the terminal
# SceneSimulation % source ~/.bash-profile

# SETUP WHAT AI ENGINE TO USE
SELECTED_AI_ENGINE = MusesHelper.AI_ENGINE_OPENAI
AI_ENGINE_MAX_PARALLELISM = 3

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
        plot_twists = MusesHelper.openFile('sceneGenData/plotqueues.txt').splitlines()
        plot_twist = random.choice(plot_twists)

        # CREATE A NEW SCENE
        prompt = MusesHelper.openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_scene_next.txt').replace('<<PREVIOUS>>',previous_scene).replace('<<CHARACTERS>>',characters).replace('<<SUMMARY>>',summary).replace('<<PLOT>>', plot_twist).replace('<<PROTAGONIST>>', protagonist)

        longest_text = MusesHelper.getLongestText(SELECTED_AI_ENGINE, prompt, previous_scene, AI_ENGINE_MAX_PARALLELISM)

        # add vivid sensory
        prompt = MusesHelper.openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_story_sensory.txt').replace('<<STORY>>',longest_text)
        longest_text = MusesHelper.callAIEngine(SELECTED_AI_ENGINE, prompt)

        # remove any previous scene verbatim lines if they are reintroduced with vivid sensory
        longest_text = MusesHelper.removeAnyPreviousLines(longest_text, previous_scene)

        previous_scene = longest_text
        MusesHelper.mkDirIfNotExists('SceneOutput')
        MusesHelper.saveFile('SceneOutput/%d.txt' % i, longest_text)

        # ================================== NEW CHARACTERS ==================================
        prompt = MusesHelper.openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_character_finder.txt').replace('<<CHARACTERS>>',characters).replace('<<SCENE>>',previous_scene)

        new_characters = MusesHelper.callAIEngine(SELECTED_AI_ENGINE,prompt)
        #print('\n====NEW CHARS=======> \n%s' % (new_characters)) 
        new_characters = MusesHelper.cleanUpAIengineOutput(new_characters)
        #print('\n====NEW CHARS=======> \n%s' % (new_characters)) 
        characters = characters + '\r\n' + new_characters
        print('\n====NEW CHARS=======> \n%s' % (characters)) 

        # ================================== CHARACTER DETAILS ==================================
        prompt = MusesHelper.openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_character_details.txt').replace('<<CHARACTERS>>',characters).replace('<<SCENE>>',previous_scene)

        new_characters = MusesHelper.callAIEngine(SELECTED_AI_ENGINE,prompt)
        #print('\n====CHAR DETAILS=======> \n%s' % (new_characters)) 
        characters = MusesHelper.cleanUpAIengineOutput(new_characters)
        print('\n====CHAR DETAILS=======> \n%s' % (characters)) 

        file1 = open('story.txt', 'a')  # append mode
        #file1.write('===== CHARS =====\r\n')
        #file1.write(longest_text + '\r\n')
        #file1.write('===== STORY =====\r\n')
        file1.write(longest_text + '\r\n')
        file1.close()

        prompt = MusesHelper.openFile('PromptTemplates/' + SELECTED_AI_ENGINE + '/prompt_story_summary.txt').replace('<<STORY>>',summary + '\r\n' + longest_text)
        summary = MusesHelper.callAIEngine(SELECTED_AI_ENGINE,prompt)
