# Honestly, main.py really just handles the initialization, damn near all the logic happens in frame_init
# which is ironic, because that was supposed to just be the initalizations of the frames.  However,
# the frames and their respective buttons are really closely tied to the different steps of the process, 
# so it didn't make sense to try to bring anything back into here if I didn't have to.  I could have split them out
# into another module, but decoupling them actually made it harder to read. 

# AI.py has all the prompts and the openAI functions and logic to actually 'talk' to the AI.  
# However, pretty miuch all the data collection, processing, and exports happens in frame_init, triggered by 
# button presses and file uploads.  
 
# To avoid circular loading, I had to move the session data into it's own file, globals.py
# which just holds a dictionary called current_prompt_variables.  Really though, 
# that contains pretty much all of the global session data, including all the inputs, like the resume,
# example cover letter, and job description.  It also contains some of, but not all, the AI call responses.  

# The one exception where responses don't go into that session data is for the export, because that's 
# actually two separate calls that only happen during that process, one to extract the Job Title and Company and 
# the other to get the qualification data.  I could have dumped all of that into the current_prompt_variables
# as well, but it didn't seem worth it, since that's the end of the process and I don't need any of that
# data anymore.  I just pass it straight into the export function as arguments, and pick a few of the 
# entries from the current_prompt_variables that aren't the results of the openAI calls.  This has the
# other benefit of spreading out the calls to the openAI api, which can take some time, especially when
# you chain a few together.  

# I'd really like to figure out a way to do two more things: scrape LinkedIn/Indeed/etc for appropriate jobs and
# then batch process them, so I could decide if a job was worth applying for based on reading a draft
# of a cover letter.  That feels like a 72 hour project though, so I'll probably tackle that tomorrow.


# Import Required Libraries - I think there might be some redundant imports here, but I don't think it SUPER matters, right?
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedTk
import os

#Import what I assume are called 'local libraries?'
from frame_init import frame_initializers
from globals import current_prompt_variables, preloaded_defaults
from utils import read_word_file

# Housekeeping that I'm not sure if it's necessary or not but the theme refueses to behave without it.
# I don't really understand Python, and I'm not sure if I've got everything installed in the correct directories or not, so
# I just sort of... force me to be in the right place and drag everything else along with it.

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

#variables for setup/config
active_frame = None

class CustomFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.master.geometry('900x600')
        self.master.title("Cover Letter Generator")
        self.master.iconbitmap('F:\Projects\CoverLetterGeneration\images\icon\icon.ico')
        #this grid setup ought to force everything to be centered, and it... kind of works?  I hate tkinter
        for i in range(0, 3):
            self.master.grid_rowconfigure(i, weight=1)
            self.master.grid_columnconfigure(i, weight=1)

def get_preloaded_defaults():
    global preloaded_defaults

    resume_folder = "./context/resumes"
    cover_letter_folder = "./context/cover_letters"

    # Loop through resumes and preload them
    for filename in os.listdir(resume_folder):
        if filename.endswith(".docx"):
            file_path = os.path.join(resume_folder, filename)
            try:
                file_content = read_word_file(file_path)
                if file_content:
                    preloaded_defaults['resumes'][filename] = file_content
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

    if not preloaded_defaults['resumes']:
        preloaded_defaults['resumes'] = "No default resumes available"

    # Loop through cover letters and preload them
    for filename in os.listdir(cover_letter_folder):
        if filename.endswith(".docx"):
            file_path = os.path.join(cover_letter_folder, filename)
            try:
                file_content = read_word_file(file_path)
                if file_content:
                    preloaded_defaults['cover_letters'][filename] = file_content
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

    if not preloaded_defaults['cover_letters']:
        preloaded_defaults['cover_letters'] = "No default cover letters available"

def raise_frame(frame_name):
    global active_frame
    if active_frame:
        active_frame.grid_forget()  # Remove the current frame from the view
    frame = frame_dict[frame_name]
    frame.grid(row=1, column=2, sticky='news')
    active_frame = frame  
    root.title(f"Cover Letter Generator - {frame_name}")  # Update the window title

# Go get the default resumes and cover letters (if any) and populate to current_prompts_variables
get_preloaded_defaults()

# region - build the GUI for the first time
root = tk.Tk()
root.tk.call('source', 'theme/forest-light.tcl')
ttk.Style().theme_use('forest-light')

# configure window
root.geometry("600x600")
root.minsize(600, 600)
root.title("Cover Letter Generator")
root.iconbitmap('F:\Projects\CoverLetterGeneration\images\icon\icon.ico')

#create frames
frame_dict = {}
step_names = ['Title', 'ResumeUpload', 'ResumeConfirm', 'ExampleUpload', 'ExampleConfirm', 'JobDescUpload', 'JobDescConfirm', 'Config', 'Generate', 'Loop']

for step in step_names:
    custom_frame = CustomFrame(root)  
    frame_dict[step] = custom_frame  

# Second loop: Populate frames
for step in step_names:
    if step in frame_initializers:
        frame_initializers[step](frame_dict[step], raise_frame)

# final setup before session begins

raise_frame('Title')

#endregion


#sessionstart
root.mainloop()
