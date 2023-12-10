from .base_model import Model
from .imports import *
from tqdm.auto import tqdm
from langchain.prompts import PromptTemplate
import json

model = GPT_4





class InterviewAgent:
    def __init__(self, topic, keywords):
        self.model = Model(GPT_4,system=self.make_sys_interviewer(topic,keywords),return_json=True)
        self.next_sys = "Let's begin the interview. Ask a simple question."
        self.prev = ''
        self.history = []
        self.streak = 0
        self.max_streak = 5
        self.max_len = 3

    def make_sys_interviewer(self, topic,keywords):
        sys = f"""\
        You'll be the interviewer. Your role is to ask questions, not answer them.
        You'll receive the conversation so far.
        Don't answer for the candidate.

        Ask only one question at a time and don't repeat questions.
        Your goal is to test the candidate's knowledge on being a SME in {topic}.
        Start with easy questions and increase difficulty as they answer correctly. 
        After they answer, give feedback and ask the next question.
        Don't ask them to write code.

        Keywords:
        {keywords}

        Other Instructions:
        The input and output will in JSONs.
        Input:
        {{
        'system':  '<System Instruction ignore if blank>'
        'message': '<Students Answer/Message>'
        }}  

        Output:
        {{
        'correctness': <'correct' or 'incorrect'>
        'skills': [{{'name': '<Skill Name>',
                    'level': '<Skill Level> Novice,Beginner, Intermediate, Expert'}}
                    ...more skills]
        'thoughts': <Your feedback on student's answer>
        'message': <Message Back to the student>
        }}

        """
        return sys

    def make_message(self, sys, msg):
        return str({'system': sys,'message': msg})

    def __call__(self,msg):
        returns = json.loads(self.model(self.make_message(self.next_sys ,msg)))
        if returns['correctness'] == 'incorrect':
            self.next_sys = "The student made a mistake last time. Next question must be a bit easier. Also update skill-level accordingly."
            self.streak = 0
        if returns['correctness'] == 'correct':
            if self.streak<self.max_streak:
                self.next_sys = "The student answered correctly. Next question must be a bit harder. It may be a follow up question only if approperiate. Else more on to different topic."
            else:
                self.next_sys = "The student answered everything on this topic correctly so far. Let's move on to a different keyword mentioned."
                self.streak = 0
            self.streak += 1

        # print(len(self.history))
        if len(self.history)>self.max_len:
                self.next_sys = "You can stop the interview. Put a thank you note. Say TERMINATE"
            


        self.prev = msg
        self.history.append({'student':msg,
                             'interviewer':returns['message'],
                             'correctness':returns['correctness'],
                             'skills':returns['skills'],
                             'interviewer_thoughts': returns['thoughts']})
        return returns['message']


    def get_feedback(self, subtopics, model_name=GPT_4):

        history = self.history
        feedback_model = Model(model_name,'FeedBack',return_json=True)
        prompt = PromptTemplate.from_template("""\

    Based on the chat history, I would like you to evaluate the expertise of the candidate in the domains based on the following format:
    The domains are 
                    {subtopics}

    Summarization: summarize the conversation in a short paragraph.

    Pros: Give positive feedback to the candidate.

    Cons: Tell the candidate what he/she can improves on.

    Expertise: Classify the candidates expertise in the topic into one of the five : [Basic/Proficient/Advanced/Expert/Master]


    Current conversation:
    {history}


    The output should be in the followin json schema

    {{
    "summary":<summary>,
    "pros":<pros>,
    "cons":<cons>,
    "expertise":
    [
    {{
        "id":<id>,
        "skill":<skill name>,
        "expertise":<expertise>
    }},
    {{
        "id":<id>
        "skill":<skill name>
        "expertise":<expertise>
    }},
    ],
    "communication": <communication skills look for grammer errors and things for accessing this.>
    }}

    """)
        # "expertise":[ {{"Skill":<skill>, "Level":<level>,"Reason":<reason>,"Feedback":<feedback>}},..and other skills identified]"


        feedback = json.loads(feedback_model(prompt.format(history=history, subtopics=json.dumps(subtopics))))
        return feedback

# def get_feedback(self, model_name=GPT_4):
    
#     history = self.history
#     feedback_model = Model(model_name,'FeedBack',return_json=True)
#     prompt = PromptTemplate.from_template("""\

#         Based on the chat history, I would like you to evaluate the candidate based on the following format:
#         Summarization: summarize the conversation in a short paragraph.

#         Pros: Give positive feedback to the candidate.

#         Cons: Tell the candidate what he/she can improves on.

#         Expertise: Classify the candidates expertise in the topic into one of the three : [Basic/Proficient/Advanced/Expert/Master]


#         Current conversation:
#         {history}


#         The output should be in the followin json schema

#         {{
#         "summary":<summary>,
#         "pros":<pros>,
#         "cons":<cons>,
#         "expertise":<expertise>,
#         "communication": <communication skills look for grammer errors and things for accessing this.>
#         }}

#     """)

#     feedback = json.loads(feedback_model(prompt))
#     feedback['raw_skills'] = get_all_skills(history)
#     return feedback