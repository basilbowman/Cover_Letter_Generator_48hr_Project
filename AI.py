#This handles (I think) all of the AI related stuffOpenAI calls and prompts
import openai
import os
from globals import current_prompt_variables
from dotenv import load_dotenv


# set up prompt templates
active_prompt = None
predefined_prompts = {
    'job_description_summary': """
        You are an HR expert and very experienced at identifying the most pertinent, important, and interesting elements of a job description.
        You also know what are the most difficult skills or qualities to find when hiring for a position.
        You are also an expert in natural language processing.
        Summarize the following job description for use by an LLM to write a cover letter: {{complete_job_description}}',
        """,
    'extract_job_description': """
        You are an expert in web scraping and text extraction. Your task is to find and extract the job description 
        from this HTML content: {{scraped_content_for_extraction}}. Please return only the text that appears to be the 
        job description, excluding any other elements like navigation, ads, or footers.
        """,
    'csv_details_extraction': """
        Given the following job description, please identify key details.  Do not lie, and only include information from the job description.  
        If the information isn't included in the job description, always say "unknown" - NEVER include anything not directly from the Job Description.
        Job Description:
        {{complete_job_description}}
        1. What is the job title mentioned in the job description?  
        Job Title:
        2. Which company is offering this position?
        Company:
        3.) If a salary or salary range is mentioned in the job description, include it below, otherwise say "unknown"
        Salary:
        4.) Indicate if the position is hybrid, remote, or in-office.  If this information is not in the job description, say "unknown"
        Office Status:
        """,
    'job_qualification_analysis': """
        You are a highly experienced HR expert and tech recruiter, with special experience in remote work.  You never lie, and your evaluations are always exactly fair.
        Given the following resume and job description, please provide an analysis of how well the candidate's qualifications match the job requirements.  
        Offer a qualification rating on a scale from 1-10, where 1 is not qualified at all and 10 is exceptionally qualified.  
        Pay special attention to any requirements that would obviously disqualify the candidate.  If an obvious disqualification is found, automatically rate the candidate 1 and summarize the lacking criteria in exactly 10 words.
        Do NOT include any rationale for this qualification.
        Do NOT give a list of pros and cons of the candidate.
        NEVER respond with any information except the numeral rating and obvious disqualifications if there are any.  If there are not any obvious disqualifications, say "N/A"
        Qualification Rating:  {{rating}}
        Obvious Disqualifications: {{Disqualification summary}}
        Resume:
        {{complete_resume}}
        Job Description: {{complete_job_description}}
        """,
    'job_duties_extract': """
        You are an HR expert and very experienced at understanding what the most important job duties are of any given role.
        You can also read between the lines and imply what a writer is really trying to say.
        Extract top 3 duties you think are most important from the following job description: {{complete_job_description}}',
        """,
    'job_requirements_extract': """
       You are an HR expert and very experienced at understanding what the most important requirements to perform a job are of any given role.
       You can also read between the lines and imply what a writer is really trying to say.
       Extract top 3 requirements from the following job description: {{complete_job_description}}
       """,
    'resume_analysis': """
        You are an HR expert and an experienced technical recruiter who is phenomenal at capturing the essence of how a candidate will perform in any given role.
        Analyze the following resume in the context of this job description {{job_description_summary}}: '{{complete_resume}}'
        """,
    'cover_letter_generation': """
        You are remarkably good at writing compelling and convincing cover letters, surprising your readers by knowing exactly what hiring managers want to hear.
        Nathan Bowman is applying for a job.  Write a cover letter as if it was written by Nathan Bowman, using this summary of the job he is applying for: {{job_description_summary}}. 
        Write the cover letter by following these instructions for voice and tone and style: {{cover_letter_analysis}}. DON'T BE ARROGANT.
        Do not lie, and use lots of references from this analysis of Nathan's resume and past experiences: {{resume_analysis}}.  Here is his actual resume too, in case you need
        more information or specific statistics and achievments: {{complete_resume}}
        Do not lie and you do not make anything up.  You always tell the truth as best as you know it, and you often include parenthetical comments to Nathan for his review 
        by including them in square brackets and marking them for NATHAN TO READ.
        """,
    'cover_letter_analysis': """
        You are an expert ghostwriter, world-class at capturing your client's authorial voice. 
        You are also an expert in natural language processing. Below is a cover letter applying for a job that was 
        written by your client. Please use natural language processing to create a paragraph that describes
        key characteristics of only your client's voice. 
        Do not include any mention of the specific job that this letter is written about, do not make anything up, and 
        do not include any specifics about your client's background. Refer to your client as "the writer."
        You should  only talk about HOW they write this letter, the tone, character, vocabulary, and any other stylistic
        elements so that an LLM could write in a similar voice using only the paragraph as input. 
        Cover Letter to be Analyzed: {{complete_example_cover_letter}}
    """,
}

# Initialize the OpenAI API client
load_dotenv()

openai.api_key = os.getenv("OpenAI_api_key") 

######    Functions    #####
# Make a call to openAI
def make_openai_api_call(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",  
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        output_text = response['choices'][0]['message']['content'].strip()

        if not output_text:
            raise ValueError("API response is empty.")

        return output_text

    except Exception as e:
        print(f"An error occurred with the OpenAI call: {e}")
        return "An error has occurred. Please try again."


# this inserts variables into a prompt
def insert_variables_into_prompt(prompt, variables):
    print ("inserting variables into the prompt")
    for variable, value in variables.items():
        placeholder = f'{{{{{variable}}}}}'  
        prompt = prompt.replace(placeholder, value)
    return prompt

# this creates the prompts that we'll send to openAI
def create_prompt(prompt_key, variables):
    global active_prompt
    
    predefined_prompt = predefined_prompts.get(prompt_key, "")
    prompt_with_variables = insert_variables_into_prompt(predefined_prompt, variables)
    
    active_prompt = prompt_with_variables
    print(prompt_with_variables)
    return prompt_with_variables


#This is the way I came up with to run prompt chains - but I should probably look at it again, 
#I don't think I'm using results anywhere that I couldn't just use current_prompt_variables
#so I could refactor it and make it cleaner.  Meh.
def run_workflow(prompt_keys):
    print("running a prompt chain")
    global current_prompt_variables
    results = {}
    for key in prompt_keys:
        try:
            # Generate the prompt
            print(key)
            prompt = create_prompt(key, current_prompt_variables)
        except Exception as e:
            print(f"Error creating prompt for key {key}: {e}")
            messagebox.showerror("Error", f"Failed to create prompt for {key}.")
            return None

        try:
            # Make the API call
            response = make_openai_api_call(prompt)
        except Exception as e:
            print(f"Error during API call for key {key}: {e}")
            messagebox.showerror("Error", f"Failed during API call for {key}.")
            return None
        
        results[key] = response
        current_prompt_variables[key] = response

    return results
   