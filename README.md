# Cover_Letter_Generator_48hr_Project

Learning project to build a Cover Letter Generator using the openAI API. 

_TL;DR - This is what a motivated absolute novice (with zero coding experience) can do in 48 hours with AI._

## Project Summary:

- This is a small program written in Python to use ChatGPT to write first drafts of cover letters for job applications.  
- I wrote it because I'm looking for a job, and starting cover letters is always a little bit intimidating - so having something to edit is much more helpful. I have no coding background, except AMIGA BASIC when I was 9 - but by working with Claude2, ChatGPT, and Bard, this was the result.

## How it works:

- You can load in your resume and examples of cover letters you've already written, and then load in new job descriptions and it will analyze your resume for context, analyze your cover letter for style, and then find the most applicable skills/experiences you have and write a first draft of a cover letter for you that it saves out to a folder.
- It will also extract some information from the inputted job description and analyze your qualification for the job, filter out any that you're obviously disqualified for and then output an excel file where you can sort by salary, remote/in-office, and qualification.

## How to Configure it:

- You'll need to get an OpenAI API key and load it into the .env file
- (Optional) You can also load your resume(s) and cover letter(s) into the /context folder, so you don't have to upload them each time.  They need to be word files (*.docx) right now, sorry. 

## Other things:

- I also want to finetune a model to better reflect how I would write cover letters, so I had it export a JSON in the format that the OpenAI finetuning upload expects. The JSON has the job description and the generated cover letter as input:output keyvalue pairs, and once I've edited the generated cover letters the way I want them, I'll probably just manually swap the edited ones out for the generated ones.  
- I only need 30-40 examples to run the finetuning process, and I'd like to see how much that improves the initial result.

## To-do:

- Progress Bar during calls to the API - this is big
- PDF input/output - I think this shouldn't be too hard, but it would be nice if it also handled PDFs, not just word files.
- Configuration page - I want to be able to change things like response temperature, set the style to "more professional," generate a PDF instead of a .txt, etc  
- Finetune the model - see above

## Maybe To-do?

- I think I want to use multiple LLMs for this - based on the past six months or so of refining my prompting ability, I've found that I often get better results by frequently swapping between OpenAI, Claude2, and Bard. I can't get API access to Claude2 yet, but I think I could at least use PaLM or something like that.
