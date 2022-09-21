# Muses
The intent of this program is to produce long open-ended fiction using cloud based AI engines like OpenAI and NLP Cloud Playground.

The code expects your tokens to be stored in environment variables as OPENAI_API_KEY or NLPCLOUD_API_KEY, or both.

start the program with
% python muses.py

1. The program has been primed with a previous_scene, characters, summary, and protagonist. The main loop writes 14 paragraphs to avoid writing forever, but the loop could be increased or decreased.
    - previous scene - what happened last. If you are going to restart the program to pickup where it left off, start with a short previous scene summary instead of the long text produced as a AI response.
    - characters - you can add a name and short description of your character. The program will continue to add to this description as the story continues and things happen to your characters.
    - summary - an ongoing summarization of what has happened.
    - protagonist - a name of a character who cannot die. Prompt is written to not kill or injure this character.

2. The output will be written to the file story.txt. It will also clear this file on every restart.

3. The last generated scene will be written to SceneOutput. It will also clear this directory/folder on every restart.

4. The program will insert randomness to drive the story in different directions using a plot queue. These are simple little text strings that are something like: someone in this story is battling with a past mistake. This helps the program to generate an open-ended ongoing story with some variety from scene to scene.

5. Main Loop

- Create a new scene using the previous scene, characters, plot, summary, and protagonist data
- This program supports parallelism, and can call the AI cloud engine simulaneously multiple times for the same scene generation. The intent is to pick the best of X scene generations. Best is determined by text length. Meaning the longest text length will be selected. Default is best of 3 attempts. Parallel calls work fine for openAI, but you will want to scale the parallelism down for NLP Cloud to probably 1 to avoid errors.
- once the longest scene text is generated, it is sent again to the cloud AI engine to enhance the scene description with sensory and vivid details. This  increases the text length with further  sensory details while keeping within the original intent of the scene.
- there is logic to avoid duplicate text or repeating sentences in future scenes if it's already been said.
- Next the program determines if any new characters have been added to the story by the AI engine
- Character details are updated based on what just happened in this scene, and any duplicate character descriptions are summarized to the character and any duplication removed.
