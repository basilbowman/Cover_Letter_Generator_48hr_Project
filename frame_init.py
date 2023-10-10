#frame_initializations
#This actually handles a lot more of the logic than I was planning, because most of the functions/calls happen as the user moves through the frames.

#Installed/Default Imports - I'm not sure if all of these are necessary, they're included because the theme docs said to...
from tkinter import ttk, Text, StringVar, filedialog, messagebox
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedTk
import csv
import os
import json
import re
from datetime import date, datetime
import pandas as pd


#Local Imports - is that what they're called?
from AI import run_workflow
from globals import current_prompt_variables, preloaded_defaults
from utils import read_word_file

#Classes
class CurrentResumeText:
    def __init__(self):
        self.resume_text = ""

    def set_resume_text(self, new_text):
        self.resume_text = new_text

class CurrentExampleCoverLetterText:
    def __init__(self):
        self.cover_letter_text = ""

    def set_cover_letter_text(self, new_text):
        self.cover_letter_text = new_text

class CurrentJobDescriptionText:
    def __init__(self):
        self.job_description_text = ""

    def set_job_description_text(self, new_text):
        self.job_description_text = new_text

#region - Variables

#misc variables
results = {}  #I can't remember if I need this or not, but I'm keeping it just in case...

#collected text variables
current_resume_text = CurrentResumeText()
current_example_cover_letter_text = CurrentExampleCoverLetterText()
current_job_description_text = CurrentJobDescriptionText()

#widget variables - these are what live in the frames
job_description_input_text_widget = None
job_description_input = None
resume_output_text_widget = None
example_output_text_widget = None
confirm_job_description_output_text_widget = None
everything_output_text_widget = None
url_input_entry = None
#endregion

#File Handling Functions
def export_cover_letter_to_txt(letter_text, job_title, company_name, qualification_rating, disqualification_reason):
    try:
        base_folder = "letters"
        date_folder = f"exported_{date.today().strftime('%B %dst, %Y')}"
        
        # Extract just the relevant portions from the job title and company name
        clean_job_title = job_title.split('__')[-1]
        clean_company_name = company_name.split('__')[-1]

        filename = f"{clean_job_title}_{clean_company_name}_Q{qualification_rating}"
        if disqualification_reason != "N/A":
            filename += f"_{disqualification_reason}"
        filename += ".txt"
        #basefolder        
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        
        os.chdir(base_folder)
        
        # datefolder
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        
        os.chdir(date_folder)
        
        # Write the coverletter text to a file
        with open(filename, "w") as text_file:
            text_file.write(letter_text)
        
        # Navigate back to the original directory
        os.chdir(os.path.join("..", ".."))
        
        full_path = os.path.abspath(os.path.join(base_folder, date_folder, filename))
        return full_path  # this goes to the CSV export


    except Exception as e:
        print(f"An error occurred while exporting the cover letter: {e}")
        messagebox.showerror("Error", "An error occurred while exporting the cover letter.")
        return None  

def export_to_excel(all_export_data):  #This is what logs out the completed generations and job descriptions for later finetuning
    try:
        file_name = "drafted_job_applications.xlsx"
        file_exists = os.path.isfile(file_name)
        
        fieldnames = ['Job Title', 'Company Name', 'Qualification Rating', 'Is Remote', 'Salary', 'URL', 'Disqualification Reason', 'Cover Letter Path', 'Date-Time']
        new_data = pd.DataFrame([[
            all_export_data.get('job_title', 'Not Listed'),
            all_export_data.get('company_name', 'Not Listed'),
            all_export_data.get('qualification_rating', 'Not Listed'),
            all_export_data.get('is_remote', 'Not Listed'),
            all_export_data.get('salary', 'Not Listed'),
            all_export_data.get('job_url', 'Not Listed'),
            all_export_data.get('disqualification_reason', 'Not Listed'),
            f"file://{all_export_data.get('cover_letter_filename', 'Not Listed')}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]], columns=fieldnames)
        
        if file_exists:
            df = pd.read_excel(file_name)
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data
        
        df.to_excel(file_name, index=False)
        
        print(f"Job details exported to {file_name}")
        
    except Exception as e:
        print(f"An error occurred while exporting to Excel: {e}")
        messagebox.showerror("Error", "An error occurred while exporting to Excel.")

def export_to_csv(all_export_data):  #This has been replaced by export_to_excel, but I'm leaving it just in case I'm an idiot
    try:
        file_name = "drafted_job_applications.csv"
        file_exists = os.path.isfile(file_name)
        
        with open(file_name, 'a', newline='') as csvfile:
            fieldnames = ['Job Title', 'Company Name', 'Qualification Rating', 'Is Remote', 'Salary', 'URL', 'Disqualification Reason', 'Cover Letter Path', 'Date-Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()  
            
            writer.writerow({
                'Job Title': all_export_data.get('job_title', 'Not Listed'),
                'Company Name': all_export_data.get('company_name', 'Not Listed'),
                'Qualification Rating': all_export_data.get('qualification_rating', 'Not Listed'),
                'Is Remote': all_export_data.get('is_remote', 'Not Listed'),
                'Salary': all_export_data.get('salary', 'Not Listed'),
                'URL': all_export_data.get('job_url', 'Not Listed'),
                'Disqualification Reason': all_export_data.get('disqualification_reason', 'Not Listed'),
                'Cover Letter Path': f"file:///{all_export_data.get('cover_letter_filename', 'Not Listed')}",
                'Date-Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        print(f"Job details exported to {file_name}")
        
    except Exception as e:
        print(f"An error occurred while exporting to CSV: {e}")
        messagebox.showerror("Error", "An error occurred while exporting to CSV.")

def write_to_JSON():   
    #This is exporting a JSON in the openAI format so I can finetune a model later for v2 - right now it's got the prompt and generation as input:output
    # but I'll replace the generation with my edited version manually later - I only need 30-40 for a finetuning run so it's easier to just manually copy/paste inside
    # the JSON later.
    global current_prompt_variables, results

    complete_prompt_template = '''
    Generate a cover letter for Nathan Bowman using this summary of the job {job_description_summary}.
    Use this list of the top 2-3 most important duties: {job_duties_extract} and requirements: {job_requirements_extract}.  
    Write it and follow this guidance: {cover_letter_analysis}. DON'T BE ARROGANT.
    Do not lie, and use references from this analysis of Nathan's resume and past experiences: {resume_analysis}.
    Do not lie and you do not make anything up. You always tell the truth as best as you know it, and you often include parenthetical comments to Nathan for his review 
    by including them in square brackets and marking them for NATHAN TO READ.
    '''

    complete_prompt_for_JSON = complete_prompt_template.format(**current_prompt_variables)
    cover_letter_generation_for_JSON = results.get('cover_letter_generation', "No cover letter generated.")

    json_object = {
        "messages": [
            {"role": "system", "content": None},
            {"role": "user", "content": complete_prompt_for_JSON},
            {"role": "assistant", "content": cover_letter_generation_for_JSON}
        ]
    }

    json_folder = "json_finetuning_data"
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    filename = os.path.join(json_folder, f"finetuning_data_{len(os.listdir(json_folder)) + 1}.json")

    with open(filename, 'w') as json_file:
        json.dump(json_object, json_file, indent=4)

    print(f"Data written to {filename}")

def sanitize_filename(filename):
    return re.sub(r'[^\w\-_]', '_', filename)

# Intake and Frame Display Functions
#
# I could probably have modularized some of these instead of having different functions for different frames/content - but it's easier for me
# to conceptualize right now as separate functions.  Maybe I'll refactor in v2.  Anyways, these mostly go get any input, update the display with that input, and then when 
# the input is confirmed, the input gets loaded into current_prompt_variables (I know it's a bad name).  Also the update functions handle the state of the confirm button.
# the uploads are only used if the default resume/cover letters are NOT used.

def update_resume_text(selected_resume, resume_text_widget, confirm_button):
    # This is the widget text refresher
    print(f"update_resume_text called with {selected_resume}")
    if selected_resume is not None:
        resume_text_widget.delete("1.0", "end")
    
        resume_content = preloaded_defaults['resumes'].get(selected_resume, "")
        if resume_content:
            resume_text_widget.insert("1.0", resume_content)
    
    resume_text_widget.update_idletasks()
    
    content = resume_text_widget.get("1.0", tk.END).strip()
    if content:
        confirm_button.config(state=tk.NORMAL)
    else:
        confirm_button.config(state=tk.DISABLED)

def upload_resume(raise_frame_func, resume_text_widget, confirm_button):   # This is the 'go get the resume' function
    file_path = filedialog.askopenfilename(filetypes=[('Word Document', '*.docx')])
    if file_path:
        resume_text_global = read_word_file(file_path)
        if resume_text_global is not None:
            resume_text_widget.delete("1.0", tk.END)
            resume_text_widget.insert(tk.END, resume_text_global)
            resume_text_widget.update_idletasks()
            update_resume_text(None, resume_text_widget, confirm_button)
        else:
            print("Error: Unable to read the Word document.")

def load_resume_into_prompt_variables(raise_frame_func, resume_text_widget):
    global current_prompt_variables
    
    resume_text = resume_text_widget.get("1.0", tk.END).strip()
    if resume_text:
        current_prompt_variables["complete_resume"] = resume_text
        raise_frame_func('ExampleUpload')
    else:
        print("Error: Resume text is empty.")

#I think this is superfluous and can be removed, but I'm not doing it right now because I'm very tired and don't want to troubleshoot it if I'm wrong :)
#I think that the current_resume_text is from a widget that doesn't exist anymore on a frame that we're not using...  I think...
def confirm_resume():
    global current_resume_text, resume_output_text_widget
    if current_resume_text is not None:
        resume_output_text_widget.delete("1.0", tk.END)  
        resume_output_text_widget.insert(tk.END, current_resume_text.resume_text)
    else:
        resume_output_text_widget.delete("1.0", tk.END)
        resume_output_text_widget.insert(tk.END, "No resume uploaded yet")

def update_cover_letter_text(selected_cover_letter, cover_letter_text_widget, confirm_button):
    if selected_cover_letter is not None:
        cover_letter_text_widget.delete("1.0", "end")
        
        cover_letter_content = preloaded_defaults['cover_letters'].get(selected_cover_letter, "")
        if cover_letter_content:
            cover_letter_text_widget.insert("1.0", cover_letter_content)
    
    cover_letter_text_widget.update_idletasks()
    
    content = cover_letter_text_widget.get("1.0", tk.END).strip()
    if content:
        confirm_button.config(state=tk.NORMAL)
    else:
        confirm_button.config(state=tk.DISABLED)

def upload_example_cover_letter(raise_frame_func, cover_letter_text_widget, confirm_button):
    file_path = filedialog.askopenfilename(filetypes=[('Word Document', '*.docx')])
    if file_path:
        cover_letter_text_global = read_word_file(file_path)
        if cover_letter_text_global is not None:
            cover_letter_text_widget.delete("1.0", tk.END)
            cover_letter_text_widget.insert(tk.END, cover_letter_text_global)
            cover_letter_text_widget.update_idletasks()
            update_cover_letter_text(None, cover_letter_text_widget, confirm_button)
        else:
            print("Error: Unable to read the Word document.")

def load_example_cover_letter_into_prompt_variables(raise_frame_func, cover_letter_text_widget):
    global current_prompt_variables
    
    example_cover_letter_text = cover_letter_text_widget.get("1.0", tk.END).strip()
    
    if example_cover_letter_text:
        current_prompt_variables["complete_example_cover_letter"] = example_cover_letter_text
        raise_frame_func('JobDescUpload')
    else:
        print("Error: No example cover letter text available.")

#I'm 99% sure this is also unnecessary, but I'm tired and again, this is leftover from a refactor and I don't think it matters right now
#I think the current_example_cover_letter_text is from an earlier version where I was using it to pass to a different output widget.
def confirm_example():
    global current_example_cover_letter_text, example_output_text_widget
    if current_example_cover_letter_text is not None:
        # Display the example cover letter text in the output_text_widget
        example_output_text_widget.delete("1.0", tk.END)  # Clear existing text
        example_output_text_widget.insert(tk.END, current_example_cover_letter_text.cover_letter_text)
    else:
        # Handle the case where there is no example cover letter text
        example_output_text_widget.delete("1.0", tk.END)  # Clear existing text
        example_output_text_widget.insert(tk.END, "No example cover letter text available.")

def get_job_description_and_url(raise_frame_func):
    global current_prompt_variables, job_description_input_text_widget, url_input_entry
    
    # Get the input job description and URL
    job_description_input = job_description_input_text_widget.get("1.0", tk.END).strip()
    job_url = url_input_entry.get()

    # Update current_prompt_variables dictionary
    if job_description_input and job_url:  # Both fields are mandatory
        current_prompt_variables['complete_job_description'] = job_description_input
        current_prompt_variables['job_url'] = job_url
        raise_frame_func('Generate')  # Move to the Generate frame (no confirmation and no config right now TBD when we add those)
    else:
        print("Error: Both job description and URL fields must be filled.")

def load_job_description_into_prompt_variables(raise_frame_func):
    global current_prompt_variables

    if current_prompt_variables.get('complete_job_description', ''):
        raise_frame_func('Generate')
    else:
        print("Error: Job description is empty and cannot be loaded into the dictionary. Please enter a valid job description.")

def check_job_desc_and_url(confirm_button, job_description_input_text_widget, url_input_entry):  # Since I don't have an update_job_desc(), I use this to handle the state of the button
    job_desc_content = job_description_input_text_widget.get("1.0", tk.END).strip()
    url_content = url_input_entry.get().strip()

    if job_desc_content and url_content:
        confirm_button.config(state=tk.NORMAL)
    else:
        confirm_button.config(state=tk.DISABLED)

def display_final_draft():
    global results, everything_output_text_widget
    everything_output_text_widget.delete("1.0", tk.END)
    
    if results:
        cover_letter_generation = results.get('cover_letter_generation', 'No generated cover letter available.')
        everything_output_text_widget.insert(tk.END, cover_letter_generation)
    else:
        everything_output_text_widget.insert(tk.END, "No example cover letter text available.")

# AI or export related calls
# 
# this generate_everything is badly named, it really ought to be something like "run_workflow_of_prompt_chain_to_generate_cover_letter"
# Also, I'm pretty sure there's a much better way to implement it, like I don't need to put anything into results, that was an older
# version - but I don't want to refactor it right now, it works and it doesn't really matter if there's an extra variable floating around.
def generate_everything(raise_frame_func):
    global results
    prompt_keys = [
        'job_description_summary',
        'job_duties_extract',
        'job_requirements_extract',
        'resume_analysis',
        'cover_letter_analysis',
        'cover_letter_generation'
    ]
    
    results = run_workflow(prompt_keys)

    raise_frame_func('Loop')

def sanitize_and_extract_details_for_csv(raw_detail_text):
    pattern = r"(?:Job Title: )?(.+?)\n(?:Company: )?(.+?)\n(?:Salary: )?(.+?)\n(?:Office Status: )?(.+)"
    match = re.search(pattern, raw_detail_text)

    if match:
        job_title, company_name, salary, office_status = match.groups()
        
        sanitized_job_title = sanitize_filename(job_title.strip())
        sanitized_company_name = sanitize_filename(company_name.strip())
        sanitized_salary = sanitize_filename(salary.strip())
        sanitized_office_status = sanitize_filename(office_status.strip())

        return {
            'job_title': sanitized_job_title, 
            'company_name': sanitized_company_name, 
            'salary': sanitized_salary, 
            'office_status': sanitized_office_status
        }
    else:
        print("CSV Sanitization failed. Retrying...")
        return None

def run_and_process_csv_detail_extraction():
    # I had to add this retry because the AI occasionally gives me non-standard returns.  I'll finetune it as part of v2, but for now, I just take 
    # five shots at it and it almost always gets one of them right.
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        result = run_workflow(['csv_details_extraction'])
        if 'csv_details_extraction' in result:
            raw_csv_response = result['csv_details_extraction']
            sanitized_and_extracted_data = sanitize_and_extract_details_for_csv(raw_csv_response)
            
            if sanitized_and_extracted_data is not None:
                return sanitized_and_extracted_data

        retry_count += 1
    
    messagebox.showerror("Error", "Something went wrong with the CSV details extraction in run_and_process after maximum retries.")
    return None

def run_and_process_qualification_analysis():
    result = run_workflow(['job_qualification_analysis'])
    print(result)
    
    if 'job_qualification_analysis' in result:
        raw_qualification_text = result['job_qualification_analysis']
        sanitized_data = sanitize_qualification_data(raw_qualification_text)
        return sanitized_data
    else:
        messagebox.showerror("Error", "Something went wrong with the qualification analysis for filename and CSV.")
        return None

def sanitize_qualification_data(api_response):
    sanitized_data = {}
    
    rating_match = re.search(r"Qualification Rating:\s+(\d+)", api_response)
    if rating_match:
        sanitized_data["qualification_rating"] = rating_match.group(1)

    disqualification_match = re.search(r"Obvious Disqualifications:\s+(.+)$", api_response)
    if disqualification_match:
        sanitized_data["disqualification_reason"] = disqualification_match.group(1)
    
    return sanitized_data

def aggregate_and_export_letter_and_CSV():
    # This is the 'put-it-all-together' function that sends a bunch of ai calls, sanitizes the data,
    # and then goes out and exports the files.  It's mostly just the logic around a chain of other functions, although
    # there's some cleverness about the getting the filepath from export_text so I can include a hyperlink in the csv.

    try:
        global current_prompt_variables
        
        # Local dictionary to hold all export data
        all_export_data = {}

        print("running the CSV prompts")
        csv_data = run_and_process_csv_detail_extraction()
        all_export_data.update(csv_data)

        print("running the qualification prompts")
        qualification_data = run_and_process_qualification_analysis()
        all_export_data.update(qualification_data)

        print("exporting to txt")
        
        # Capture the returned filename from export_cover_letter_to_txt
        exported_filename = export_cover_letter_to_txt(
            current_prompt_variables.get('cover_letter_generation', 'No cover letter available'),
            all_export_data['job_title'],
            all_export_data['company_name'],
            all_export_data['qualification_rating'],
            all_export_data.get('disqualification_reason', 'N/A')
        )
        
        # Add the filename and URL to all_export_data
        all_export_data['cover_letter_filename'] = exported_filename
        all_export_data['job_url'] = current_prompt_variables.get('job_url', 'Not Listed')

        print(all_export_data)

        # Export to CSV  - switched to Excel because that's what I was opening it in anyways, but leaving this in case I need it later.
        #print("exporting to csv")
        #export_to_csv(all_export_data)
        
        # Export to Excel
        print ("exporting to Excel")
        export_to_excel(all_export_data)

        # Export to JSON for Finetuning
        print("exporting to JSON")
        write_to_JSON()

        print("export process completed")
        messagebox.showinfo("Success", "File exported")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred during the export process: {e}")



#Frame Initializations
#These hold the GUI and handle input/output and buttons  Each frame is a 'step' in the generation process.
# I also refactored and don't use a few of these frames rn, but I'm leaving them because I have an idea to have them also contain the 
# results from the AI calls about their respective inputs and having the user confirm those calls too.
# Also, I hate tkinter - nothing ever goes where I want it to.

def initialize_title_frame(frame, raise_frame_func):
    
    print("Loading title frame")
    title_label = ttk.Label(
        frame,
        text="Cover Letter Generator",
        font=("Helvetica", 24),
        justify="center",
        anchor="center")
    title_label.grid(row=0, column=0, columnspan=3, pady=20)
  
    description_label = ttk.Label(frame, text="Generate cover letters effortlessly!", font=("Helvetica", 14))
    description_label.grid(row=1, column=0, columnspan=3)

    instructions_label = ttk.Label(
    frame,
    text="Welcome to the Cover Letter Generator.\n\nFollow the steps to create a customized cover letter for your job application.",
    font=("Helvetica", 12),
    wraplength=400,
    justify="center",
    anchor="center"
    )
    instructions_label.grid(row=2, column=1, columnspan=3, rowspan=2, pady=20)

    next_button = ttk.Button(
        frame,
        text="Get Started!",
        style='Accent.TButton',
        command=lambda: raise_frame_func('ResumeUpload'))
    next_button.grid(row=5, column=1, columnspan=2, pady=20)

def initialize_resume_upload_frame(frame, raise_frame_func):
    print("Loading resume upload frame")
    global current_prompt_variables, preloaded_defaults  # Declare the variable as global
    
    default_resume_var = StringVar()
    default_resume_var.set("default setting")

    confirm_button = ttk.Button(frame, text="Confirm", state=tk.DISABLED, command=lambda: load_resume_into_prompt_variables(raise_frame_func, resume_text_widget))
    confirm_button.grid(row=6, column=2, columnspan=2)

    title_label = ttk.Label(frame, text="Resume Upload", font=("Helvetica", 24))
    title_label.grid(row=0, column=0, columnspan=4, pady=20)
    
    instructions_label = ttk.Label(frame, text="Upload your resume in *.docx format. Sorry, can't handle PDFs yet!", font=("Helvetica", 12))
    instructions_label.grid(row=1, column=2, columnspan=2)

    resume_text_widget = Text(frame, wrap='word', width=50, height=20)
    resume_text_widget.grid(row=2, rowspan=8, column=0, columnspan=2, padx=10, pady=10)
    
    default_resumes_menu = ttk.OptionMenu(
    frame, 
    default_resume_var, 
    "Select resume to use",
    *["Select resume to use"] + list(preloaded_defaults.get('resumes', {}).keys()), 
    command=lambda selected: None if selected == "Select resume to use" else update_resume_text(selected, resume_text_widget, confirm_button)
    )
    default_resumes_menu.grid(row=2, column=2, columnspan=2)

    label_text = ttk.Label(frame, text="Select a default resume, or upload a custom one:")
    label_text.grid(row=3, column=2, columnspan=2)

    back_button = ttk.Button(frame, text="Back", command=lambda: raise_frame_func('Title'))
    back_button.grid(row=5, column=2, columnspan=2)

    upload_button = ttk.Button(
    frame, 
    text="Upload Custom Resume", 
    command=lambda: upload_resume(raise_frame_func, resume_text_widget, confirm_button)
    )
    upload_button.grid(row=4, column=2, columnspan=2)

    #confirm_button = ttk.Button(frame, text="Confirm", command=lambda: load_resume_into_prompt_variables(raise_frame_func, resume_text_widget))
    #confirm_button.grid(row=6, column=2, columnspan=2)

def initialize_resume_confirm_frame(frame, raise_frame_func):   # This frame gets skipped right now
  print("loading resume confirmation frame")
  confirmation_label = ttk.Label(frame, text="Confirm your uploaded resume:")
  confirmation_label.grid(row=0, column=0, columnspan=2)

  global resume_output_text_widget
  resume_output_text_widget = tk.Text(frame, width=40, height=10, wrap=tk.WORD, padx=10, pady=10)
  resume_output_text_widget.grid(row=3, column=0, sticky='nsew', pady=10)
  resume_output_text_widget.insert(tk.END, "")
 
  output_label = ttk.Label(frame, text="Extracted Information:")
  output_label.grid(row=2, column=0, sticky='w')
 
  confirm_button = ttk.Button(frame, text="Display Loaded Resume", command=confirm_resume)
  confirm_button.grid(row=1, column=0)

  back_button = ttk.Button(frame, text="Back to Resume Upload", command=lambda: raise_frame_func('ResumeUpload'))
  back_button.grid(row=4, column=0)

  next_button = ttk.Button(frame, text="Confirm Resume Contents", command=lambda: load_resume_into_prompt_variables(raise_frame_func))
  next_button.grid(row=4, column=1)

def initialize_example_upload_frame(frame, raise_frame_func):
    print("loading example cover letter upload frame")
    global current_prompt_variables, preloaded_defaults 
    
    default_cover_letter_var = StringVar()
    default_cover_letter_var.set("default setting")

    confirm_button = ttk.Button(frame, text="Confirm", state=tk.DISABLED, command=lambda: load_example_cover_letter_into_prompt_variables(raise_frame_func, cover_letter_text_widget))
    confirm_button.grid(row=6, column=2, columnspan=2)

    title_label = ttk.Label(frame, text="Cover Letter Upload", font=("Helvetica", 24))
    title_label.grid(row=0, column=0, columnspan=4, pady=20)
    
    instructions_label = ttk.Label(frame, text="Upload your cover letter in *.docx format. Sorry, can't handle PDFs yet!", font=("Helvetica", 12))
    instructions_label.grid(row=1, column=2, columnspan=2)

    cover_letter_text_widget = Text(frame, wrap='word', width=50, height=20)
    cover_letter_text_widget.grid(row=2, rowspan=8, column=0, columnspan=2, padx=10, pady=10)

    default_cover_letters_menu = ttk.OptionMenu(
        frame, 
        default_cover_letter_var, 
        "Select cover letter to use",
        *["Select cover letter to use"] + list(preloaded_defaults.get('cover_letters', {}).keys()), 
        command=lambda selected: None if selected == "Select cover letter to use" else update_cover_letter_text(selected, cover_letter_text_widget, confirm_button)
    )
    default_cover_letters_menu.grid(row=2, column=2, columnspan=2)

    label_text = ttk.Label(frame, text="Select a default cover letter, or upload a custom one:")
    label_text.grid(row=3, column=2, columnspan=2)

    back_button = ttk.Button(frame, text="Back", command=lambda: raise_frame_func('Title'))
    back_button.grid(row=5, column=2, columnspan=2)

    upload_button = ttk.Button(
        frame, 
        text="Upload Custom Cover Letter", 
        command=lambda: upload_example_cover_letter(raise_frame_func, cover_letter_text_widget, confirm_button)
    )
    upload_button.grid(row=4, column=2, columnspan=2)

def initialize_example_confirm_frame(frame, raise_frame_func):   # This frame gets skipped right now
 
  confirmation_label = ttk.Label(frame, text="Confirm your uploaded example cover letter:")
  confirmation_label.grid(row=0, column=0, columnspan=2)

  global example_output_text_widget
  example_output_text_widget = tk.Text(frame, width=40, height=10, wrap=tk.WORD, padx=10, pady=10)
  example_output_text_widget.grid(row=3, column=0, sticky='nsew', pady=10)
  example_output_text_widget.insert(tk.END, "")

  confirm_button = ttk.Button(frame, text="Display Loaded Example Cover Letter", command=confirm_example)
  confirm_button.grid(row=1, column=0)

  output_label = ttk.Label(frame, text="Extracted Information:")
  output_label.grid(row=2, column=0, sticky='w')

  back_button = ttk.Button(frame, text="Back to Cover Letter Example Upload", command=lambda: raise_frame_func('ExampleUpload'))
  back_button.grid(row=4, column=0)
  
  next_button = ttk.Button(frame, text="Confirm Loaded Example Cover Letter", command=lambda: load_example_cover_letter_into_prompt_variables(raise_frame_func))
  next_button.grid(row=4, column=1)

def initialize_job_desc_upload_frame(frame, raise_frame_func):   # I messed around with scraping the job description from the input URL, but everybody uses react, so I'd have to learn Selenium and ain't nobody got time for that
    print("loading job description upload frame")
    global job_description_input_text_widget
    global url_input_entry

    title_label = ttk.Label(frame, text="Job Description Upload", font=("Helvetica", 24))
    title_label.grid(row=0, column=0, columnspan=4, pady=20)

    instructions_label = ttk.Label(
        frame,
        text="Copy and paste the Job Description and its URL below:",
        font=("Helvetica", 12)
    )
    instructions_label.grid(row=1, column=2, columnspan=2)

    confirm_button = ttk.Button(frame, text="Confirm", state=tk.DISABLED, command=lambda: get_job_description_and_url(raise_frame_func))
    confirm_button.grid(row=8, column=2)

    job_description_input_text_widget = tk.Text(frame, width=50, height=20, wrap=tk.WORD)
    job_description_input_text_widget.grid(row=2, rowspan=8, column=0, columnspan=2, padx=10, pady=10)
    job_description_input_text_widget.bind('<Control-z>', lambda event: job_description_input_text_widget.edit_undo())  #This doesn't work, I don't know why
    job_description_input_text_widget.bind("<KeyRelease>", lambda event: check_job_desc_and_url(confirm_button, job_description_input_text_widget, url_input_entry))

    url_label = ttk.Label(frame, text="URL for the job posting:")
    url_label.grid(row=2, column=2)
    
    url_input_entry = tk.Entry(frame, width=60)
    url_input_entry.grid(row=2, column=3, pady=10)
    url_input_entry.insert(0, "")

    url_input_entry.bind("<KeyRelease>", lambda event: check_job_desc_and_url(confirm_button, job_description_input_text_widget, url_input_entry))

    back_button = ttk.Button(frame, text="Back", command=lambda: raise_frame_func('ExampleUpload'))
    back_button.grid(row=5, column=2, columnspan=2)

def initialize_job_desc_confirm_frame(frame, raise_frame_func):  # This frame gets skipped right now
    print("loading job description confirmation frame")
    global current_job_description_text, confirm_job_description_output_text_widget
    
    upload_label = ttk.Label(frame, text="Does this look right?  Go back and fix it if not.")
    upload_label.grid(row=0, column=0, columnspan=2)

    confirm_job_description_output_text_widget = tk.Text(frame, width=40, height=10, wrap=tk.WORD, padx=10, pady=10)
    confirm_job_description_output_text_widget.delete("1.0", tk.END)
    confirm_job_description_output_text_widget.grid(row=3, column=0, sticky='nsew', pady=10)

    back_button = ttk.Button(frame, text="Back to Job Description Upload", command=lambda: raise_frame_func('JobDescUpload'))
    back_button.grid(row=4, column=0)

    next_button = ttk.Button(frame, text="Confirm Loaded Job Description", command=lambda: load_job_description_into_prompt_variables(raise_frame_func))
    next_button.grid(row=4, column=1)

def initialize_config_frame(frame, raise_frame_func):  # This frame gets skipped right now
    #need to add any global variables for config to send out to the AI script
    # I'd like to add like "style of cover letter" with a dropdown menu or 
    # export straight to PDF or stuff like that - checkboxes with configurations.
    #right now this doesn't do anything
    
    print("loading configuration frame")
    upload_label = ttk.Label(frame, text="Configure the cover letter to be generated - TBD")
    upload_label.grid(row=0, column=0, columnspan=2)
    
    back_button = ttk.Button(frame, text="Back to Job Description Upload", command=lambda: raise_frame_func('JobDescUpload'))
    back_button.grid(row=4, column=0)

    next_button = ttk.Button(frame, text="Go to Generate Page", command=lambda: raise_frame_func('Generate'))
    next_button.grid(row=4, column=1)

def initialize_generate_frame(frame, raise_frame_func):
    #need to add any global variables for generation, and all of the logic
    #maybe a progress bar while it just... hangs
    #right now this is just a place for the generate everything button to live
    
    print("loading generation frame")
    upload_label = ttk.Label(frame, text="Generation Frame")
    upload_label.grid(row=0, column=0, columnspan=2)

    back_button = ttk.Button(frame, text="Back to Configuration", command=lambda: raise_frame_func('ResumeUpload'))
    back_button.grid(row=4, column=0)

    next_button = ttk.Button(frame, text="Actually Generate Cover Letter", command=lambda: generate_everything(raise_frame_func))
    next_button.grid(row=4, column=1)

def initialize_loop_frame(frame, raise_frame_func):  
    # I called this loop, because this is where it 'loops' back - if it wouldn't be super confusing, I've have called it output
    upload_label = ttk.Label(frame, text="Loop Frame")
    upload_label.grid(row=0, column=0, columnspan=2)

    global everything_output_text_widget
    everything_output_text_widget = tk.Text(frame, width=40, height=10, wrap=tk.WORD, padx=10, pady=10)
    everything_output_text_widget.grid(row=3, column=0, columnspan=4, sticky='nsew', pady=10)
    everything_output_text_widget.insert(tk.END, "")

    read_button = ttk.Button(frame, text="Click to read cover letter here", command=lambda: display_final_draft())
    read_button.grid(row=1, column=0)

    back_button = ttk.Button(frame, text="Click to re-do cover letter generation", command=lambda: generate_everything(raise_frame_func))
    back_button.grid(row=1, column=2)

    export_button = ttk.Button(frame, text="Export Cover Letter", command=lambda: aggregate_and_export_letter_and_CSV())
    export_button.grid(row=1, column=4)

    back_button = ttk.Button(frame, text="Choose new resume and cover letter", command=lambda: raise_frame_func('ResumeUpload'))
    back_button.grid(row=4, column=0)

    next_button1 = ttk.Button(frame, text="Add a New Job Description", command=lambda: raise_frame_func('JobDescUpload'))
    next_button1.grid(row=4, column=3)


# a dictionary to map frame names to their initialization functions for initial setup in main.py
# this could probably live in globals.py or something like that as well, but this is where I initially had it
# because I thought frame_init was only handling the frame initializations.  Then it ended up handling... everything?
frame_initializers = {
    'Title': initialize_title_frame,
    'ResumeUpload': initialize_resume_upload_frame,
    'ResumeConfirm': initialize_resume_confirm_frame,
    'ExampleUpload': initialize_example_upload_frame,
    'ExampleConfirm': initialize_example_confirm_frame,
    'JobDescUpload': initialize_job_desc_upload_frame,
    'JobDescConfirm': initialize_job_desc_confirm_frame,
    'Config': initialize_config_frame,
    'Generate': initialize_generate_frame,
    'Loop': initialize_loop_frame,
}