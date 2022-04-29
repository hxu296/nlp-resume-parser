import pdftotext
import openai
import re
import logging

class ResumeParser():
    def __init__(self, OPENAI_API_KEY):
        # set GPT-3 API key from the environment vairable
        openai.api_key = OPENAI_API_KEY
        # GPT-3 completion question for basic user information
        self.basic_info_questions = \
"""Summarize the resume text into key-value pairs with all of the following keys: first name, last name, full name, email, U.S. phone number, location, portfolio website URL, LinkedIn URL, GitHub main page URL, university, education level (BS or MS), graduation year, graduation month, majors, GPA. Following the format of the partial example below:
first name: first
last name: last
full name: name
graduation year: 2022
graduation month: 5
education level: BS
GPA: 3.8
"""
        # GPT-3 completion question for work experiences
        self.work_experience_questions = \
"""
Write tables to summarize all experiences from the resume with the following titles: Job Title, Job Organization, Job Location, Job Duration, Job Description. Summarize as many experiences as possible.
"""
        # set up this parser's logger
        logging.basicConfig(filename='logs/parser.log', level=logging.DEBUG)
        self.logger = logging.getLogger()

    def pdf2string(self: object, pdf_path: str) -> str:
        """
        Extract the content of a pdf file to string.
        :param pdf_path: Path to the PDF file.
        :return: PDF content string.
        """
        with open(pdf_path, "rb") as f:
            pdf = pdftotext.PDF(f)
        pdf_str = "\n\n".join(pdf)
        pdf_str = re.sub('\s[,.]', ',', pdf_str)
        pdf_str = re.sub('[\n]+', '\n', pdf_str)
        pdf_str = re.sub('[\s]+', ' ', pdf_str)
        pdf_str = re.sub('http[s]?(://)?', '', pdf_str)
        return pdf_str

    def query_completion(self: object,
                        prompt: str,
                        engine: str = 'text-curie-001',
                        temperature: float = 0.0,
                        max_tokens: int = 100,
                        top_p: int = 1,
                        frequency_penalty: int = 0,
                        presence_penalty: int = 0) -> object:
        """
        Base function for querying GPT-3. 
        Send a request to GPT-3 with the passed-in function parameters and return the response object.
        :param prompt: GPT-3 completion prompt.
        :param engine: The engine, or model, to generate completion.
        :param temperature: Controls the randomnesss. Lower means more deterministic.
        :param max_tokens: Maximum number of tokens to be used for prompt and completion combined.
        :param top_p: Controls diversity via nucleus sampling.
        :param frequency_penalty: How much to penalize new tokens based on their existence in text so far.
        :param presence_penalty: How much to penalize new tokens based on whether they appear in text so far.
        :return: GPT-3 response object
        """
        self.logger.info(f'query_completion: using {engine}')
        estimated_prompt_tokens = int(len(prompt.split()) * 1.6)
        self.logger.info(f'estimated prompt tokens: {estimated_prompt_tokens}')
        estimated_answer_tokens = 2049 - estimated_prompt_tokens
        if estimated_answer_tokens < max_tokens:
            self.logger.warning('estimated_answer_tokens lower than max_tokens, changing max_tokens to', estimated_answer_tokens)
        response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=min(4096-estimated_prompt_tokens, max_tokens),
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
        )
        return response

    def query_basic_info(self: object, pdf_str: str) -> dict:
        """
        Query basic user information and return a well-origanized dictionary.
        Send request to GPT-3 via query_completion and parse the response object.
        :param pdf_str: PDF content string.
        :param questions: Question question for the GPT-3 completion task.
        :return: A dictionary with keys (name, email, U.S. phone number, location, 
        personal website url, university, graduation time, majors, GPA)
        """
        questions = self.basic_info_questions
        prompt = questions + '\n' + pdf_str
        max_tokens = 500
        for engine in ['text-davinci-002']:
            try:
                response = self.query_completion(prompt,engine=engine,max_tokens=max_tokens)
                response_text = response['choices'][0]['text'].strip()
                response_list = response_text.split('\n')
                response_dict = {pair[0].strip():pair[1].strip() for pair in [tuple(entry.split(':')) for entry in response_list] if len(pair) > 1}
                if response_dict: break
            except Exception as e:
                self.logger.error(f'query_basic_info failed with the following exception: {e}')
                self.logger.error(f'response_text:\n{response_text}')
                return {}
        # split majors into list
        response_dict['majors'] = [major.strip() for major in response_dict['majors'].split(',')]
        # website sanity check
        if 'portfolio website URL' not in response_dict or not re.match(r"(\w+\.)?\w+\.\w+(\/\w*)?", response_dict['portfolio website URL']):
            response_dict['portfolio website URL'] = None
        if 'LinkedIn URL' not in response_dict or not re.match(r"(\w+\.)?\w+\.\w+(\/\w*)?", response_dict['LinkedIn URL']):
            response_dict['LinkedIn URL'] = None
        if 'GitHub main page URL' not in response_dict or not re.match(r"(\w+\.)?\w+\.\w+(\/\w*)?", response_dict['GitHub main page URL']):
            response_dict['GitHub main page URL'] = None

        # email sanity check
        if 'email' not in response_dict or not re.match(r"^\w+.*@(.+)\.([a-z]{2,4}|\d+)$", response_dict['email']):
            response_dict['email'] = None
        # Experimental 
        # ensure that all personal information in the response_dict are present in the pdf_str
        #for info in ['first name', 'last name', 'email', 'U.S. phone number', 'location', 'personal website URL', 'university', 'graduation time', 'GPA']:
        #    if info not in response or not self.resume_contains_info(pdf_str, response_dict[info]):
        #        response_dict[info] = None  # if not, invalidate the value

        return response_dict

    def query_work_experience(self: object, pdf_str: str) -> list:
        """
        Query work experience and return a well-origanized dictionary.
        Send request to GPT-3 via query_completion and parse the response object.
        :param pdf_str: PDF content string.
        :param questions: Question question for the GPT-3 completion task.
        :return: A list of dictionaries, where each dictory is a work experience with keys
        (Jon Title, Company, Location, Duration, Job Content)
        """
        questions = self.work_experience_questions
        prompt = questions + '\n' + pdf_str + '\n'
        max_tokens = 1500
        engine = 'text-davinci-002'
        response = self.query_completion(prompt,engine=engine,max_tokens=max_tokens)
        response_text = response['choices'][0]['text'].strip()
        try:
            jobs = []
            for job in response_text.split('Job Title: '):
                if not job.strip(): continue
                partition = job.split('Job Organization: ')
                job_title = partition[0].strip()
                partition = partition[1].split('Job Location: ')
                company = partition[0].strip()
                partition = partition[1].split('Job Duration: ')
                location = partition[0].strip()
                partition = partition[1].split('Job Description:')
                duration = partition[0].strip()
                job_content = partition[1].strip()
                jobs.append({'Job Title':job_title,
                    'Job Organization':company,
                    'Job Location':location,
                    'Job Duration':duration,
                    'Job Description':job_content})
            print(prompt)
            print(response_text)
            return jobs
        except Exception as e:
            self.logger.error(f'query_work_experience failed with the following exception:\n {e}')
            self.logger.error(f'response_text:\n {response_text}')
            return []

    def resume_contains_info(self: object, pdf_str: str, info: str) -> bool:
        """
        Check if the resume contains the information.
        :param pdf_str: PDF content string.
        :param info: Information to be checked.
        :return: True if the resume contains the information, False otherwise.
        """
        # normalize pdf_str and info: remove all spaces, special characters, and punctuations
        pdf_str = re.sub(r'\s+', '', pdf_str)
        pdf_str = re.sub(r'[^\w\s]', '', pdf_str)
        info = re.sub(r'\s+', '', info)
        info = re.sub(r'[^\w\s]', '', info)
        # check if the pdf_str contains the info
        return info in pdf_str

    def query_resume(self: object, 
                    pdf_path: str, 
                    query_info: bool = True, 
                    query_work: bool = True) -> dict:
        """
        Query GPT-3 for the work experience and / or basic information from the resume at the PDF file path.
        :param pdf_path: Path to the PDF file.
        :param query_info: True if we want to query basic info, False otherwise
        :param query_work: True if we want to query work experience, False otherwise
        :return dictionary of resume with keys (basic_info, work_experience). See the documentation for
        query_basic_info and query_work_experience for value types.
        """
        resume = {}
        pdf_str = self.pdf2string(pdf_path)
        if query_info: 
            basic_info = self.query_basic_info(pdf_str)
            resume['basic_info'] = basic_info
        if query_work: 
            work_experience = self.query_work_experience(pdf_str)
            resume['work_experience'] = work_experience
        return resume
