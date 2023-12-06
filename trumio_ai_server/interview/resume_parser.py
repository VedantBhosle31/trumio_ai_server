from PyPDF2 import PdfReader
from openai import OpenAI
from django.conf import settings

MODEL = settings.MODEL1
API_KEY = settings.OPENAI_API_KEY


class ResumeParser:

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
    5. Reinforcement Learning
    """


    def __init__(self, pdf):
        self.pdf_file = pdf
        self.client = OpenAI(api_key=API_KEY)
        self.resume_text = self.get_pdf_text(self.pdf_file)


    def get_pdf_text(self, pdf):
        reader = PdfReader(pdf)
        page = reader.pages[0]
        text = page.extract_text()

        return text


    def get_content(self):

        user_prompt = f"Parse the following resume. \n\n {self.resume_text}"


        completion = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" }
            )

        return completion.choices[0].message.content


    def get_skills(self):

      completion = self.client.chat.completions.create(
              model=MODEL,
              messages=[
              {"role": "system", "content": self.resume_evaluation},
              {"role": "user", "content": f"Classify the following resume. \n\n {self.resume_text}"}
              ],
              response_format={ "type": "json_object" }
          )
      
      return completion.choices[0].message.content


