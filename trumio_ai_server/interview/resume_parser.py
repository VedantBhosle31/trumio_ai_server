#pip3 install requests PyPDF2 openai django
from PyPDF2 import PdfReader
from openai import OpenAI
from io import BytesIO
from django.conf import settings
from typing import List, Union
import requests

# Retrieve settings for the AI model and API key from Django's settings module.
MODEL = settings.MODEL1
API_KEY = settings.OPENAI_API_KEY


class ResumeParser:
    """
    ResumeParser class for parsing and categorizing information from resumes.

    Attributes:
    - system_prompt (str): Prompt instructing the AI on how to parse resume text.
    - resume_evaluation (str): Prompt instructing the AI on how to classify resume skills.
    - pdf_url (str): URL link to the resume PDF.
    - client (OpenAI): Instance of OpenAI client initialized with the API key.
    - resume_text (str): Extracted text content from the resume PDF.
    """

    # Starter text for guiding the text extraction AI.
    system_prompt = """
    You are a bot that parses resume/CV text(given to you) to give some information(listed below) about a candidate. Under every heading Give the subheading and all the text also.

    1) Education
    2) Past Experience/Work Experience (list all points under each experience)
    3) Projects
    4) Programming languages/frameworks

    The output should be in the following json schema

    {
    "Education": [{"institute":<instituteName>, "course":<courseName>, "grade":<grade>}],
    "WorkEx":[{"companyName":<companyName>, "position":<position>, "duration":<duration>, "description":<description>}],
    "Projects:[{"projectName":<projectName>, "description":<description>}],
    "Languages/Frameworks":[<lang/framework>, <lang/framework>]
    }

    {}
    """

    # Starter text for guiding the skills classification AI.
    resume_evaluation = """ You are a bot that classifies a given resume into a set of categories. 
    Given a set of categories and a resume, for each category you have to give 1 if the resume indicates skill corresponding to the category and 0 otherwise.

    The output should be in the following json schema
    {
      <category>: <1/0>
    }

    The categories are

    1. Frontend Development
    2. Backend Development
    3. Machine learning
    4. Computer Vision
    5. Natural Language Processing
    6. Reinforcement Learning
    """


    def __init__(self, pdf_url:str):
        """
        Initializes the ResumeParser with a PDF URL and sets up the OpenAI client.

        Parameters:
        - pdf_url (str): The URL to the PDF resume to parse.
        """
        self.pdf_url = pdf_url
        self.client = OpenAI(api_key=API_KEY)   # Setting up the OpenAI client with the given API key.
        self.resume_text: str = self.extract_text(self.pdf_url) # Extracts text from the given PDF URL.


    # def get_pdf_text(self, pdf: str) -> str:
    #     reader = PdfReader(pdf)
    #     page = reader.pages[0]
    #     text = page.extract_text()

    #     return text

    def extract_text(self, pdf_url):
        """
        Extracts text from a PDF located at a specified URL.

        Parameters:
        - pdf_url (str): URL to the PDF from which to extract text.

        Returns:
        - str: Extracted text from PDF or None if an error occurs.
        """

        try:
            response = requests.get(pdf_url)    # Send a GET request to download the PDF.

            # Create a file-like object using BytesIO for PdfReader to read from.
            pdf_reader = PdfReader(BytesIO(response.content))

            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() # Extract and concatenate text from each page.

            return text

        except Exception as e:
            print(f"Error: {e}")
            return None     # Return None in case of any error during text extraction.


    def get_content(self) -> str:
        """
        Gets parsed resume content by using the OpenAI Chat API.

        Returns:
        - str: JSON-formatted string with parsed resume content.
        """
        user_prompt = f"Parse the following resume. \n\n {self.resume_text}"

        # Feeds prompts to the model and retrieves the parsed content.
        completion = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                {"role": "system", "content": self.system_prompt},  # System prompt
                {"role": "user", "content": user_prompt}    # User prompt with resume text
                ],
                response_format={ "type": "json_object" }   # Specifies the expected response format.
            )

        return completion.choices[0].message.content    # Return the content of the response.



    def get_skills(self) -> str:
      """
        Classifies the skills in the resume by using the OpenAI Chat API.

        Returns:
        - str: JSON-formatted string with classified skills from the resume.
        """
        # Feeds resume text and evaluation prompts to the model.
      completion = self.client.chat.completions.create(
              model=MODEL,
              messages=[
              {"role": "system", "content": self.resume_evaluation}, # Resume evaluation prompt
              {"role": "user", "content": f"Classify the following resume. \n\n {self.resume_text}"}
              ],
              response_format={ "type": "json_object" } # Specifies the expected response format.
          )
      
      return completion.choices[0].message.content  # Return the classified skills.
