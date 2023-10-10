# 
# Initialize the dictionary that will hold the current prompt variables.
# This is very badly named and I think should be changed - it's not just holding prompt variables, it's also holding responses and a bunch of other
# session data.  It really ought to be something like "current_session_data" or something like that.  Maybe one day.
current_prompt_variables = {
    'complete_resume': '',
    'complete_example_cover_letter': '',
    'complete_job_description': ''
}

# These are the default resumes and cover letters that are scanned and loaded in during the initial setup
# they're stored in /context/resumes and /context/cover_letters, respectively.
# I should probably make it able to handle PDFs, but for right now it's just word files (*.docx)
preloaded_defaults = {'resumes': {}, 'cover_letters': {}}
