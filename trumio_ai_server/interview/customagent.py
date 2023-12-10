from django.conf import settings

from langchain.prompts import PromptTemplate
from openai import OpenAI


API_KEY = settings.OPENAI_API_KEY
MODEL = settings.MODEL1
# class templates:

#     """ store all prompts templates """

#     da_template = """
#             I want you to act as an interviewer. Remember, you are the interviewer not the candidate.

#             Let think step by step.

#             Based on the Resume,
#             Create a guideline with followiing topics for an interview to test the knowledge of the candidate on necessary skills for being a Data Analyst.

#             The questions should be in the context of the resume.

#             There are 3 main topics:
#             1. Background and Skills
#             2. Work Experience
#             3. Projects (if applicable)

#             Do not ask the same question.
#             Do not repeat the question.

#             Resume:
#             {context}

#             Question: {question}
#             Answer: """

#     # software engineer
#     swe_template = """
#             I want you to act as an interviewer. Remember, you are the interviewer not the candidate.

#             Let think step by step.

#             Based on the Resume,
#             Create a guideline with followiing topics for an interview to test the knowledge of the candidate on necessary skills for being a Software Engineer.

#             The questions should be in the context of the resume.

#             There are 3 main topics:
#             1. Background and Skills
#             2. Work Experience
#             3. Projects (if applicable)

#             Do not ask the same question.
#             Do not repeat the question.

#             Resume:
#             {context}

#             Question: {question}
#             Answer: """

#     # marketing
#     marketing_template = """
#             I want you to act as an interviewer. Remember, you are the interviewer not the candidate.

#             Let think step by step.

#             Based on the Resume,
#             Create a guideline with followiing topics for an interview to test the knowledge of the candidate on necessary skills for being a Marketing Associate.

#             The questions should be in the context of the resume.

#             There are 3 main topics:
#             1. Background and Skills
#             2. Work Experience
#             3. Projects (if applicable)

#             Do not ask the same question.
#             Do not repeat the question.

#             Resume:
#             {context}

#             Question: {question}
#             Answer: """

#     jd_template = """I want you to act as an interviewer. Remember, you are the interviewer not the candidate.

#             Let think step by step.

#             Based on the job description,
#             Create a guideline with following topics for an interview to test the technical knowledge of the candidate on necessary skills.

#             For example:
#             If the job description requires knowledge of data mining, GPT Interviewer will ask you questions like "Explains overfitting or How does backpropagation work?"
#             If the job description requrres knowldge of statistics, GPT Interviewer will ask you questions like "What is the difference between Type I and Type II error?"

#             Do not ask the same question.
#             Do not repeat the question.

#             Job Description:
#             {context}

#             Question: {question}
#             Answer: """

#     behavioral_template = """ I want you to act as an interviewer. Remember, you are the interviewer not the candidate.

#             Let think step by step.

#             Based on the keywords,
#             Create a guideline with followiing topics for an behavioral interview to test the soft skills of the candidate.

#             Do not ask the same question.
#             Do not repeat the question.

#             Keywords:
#             {context}

#             Question: {question}
#             Answer:"""

#     feedback_template = """ Based on the chat history, I would like you to evaluate the candidate based on the following format:
#                 Summarization: summarize the conversation in a short paragraph.

#                 Pros: Give positive feedback to the candidate.

#                 Cons: Tell the candidate what he/she can improves on.

#                 Score: Give a score to the candidate out of 100.

#                 Sample Answers: sample answers to each of the questions in the interview guideline.

#                Remember, the candidate has no idea what the interview guideline is.
#                Sometimes the candidate may not even answer the question.

#                Current conversation:
#                {history}

#                Interviewer: {input}
#                Response: """

#     interview_feedback = PromptTemplate.from_template('''
#                 Based on the chat history, I would like you to evaluate the candidate based on the following format:
#                 Summarization: summarize the conversation in a short paragraph.

#                 Pros: Give positive feedback to the candidate.

#                 Cons: Tell the candidate what he/she can improves on.

#                 Expertise: Classify the candidates expertise in the topic into one of the three : [Beginner/Intermediate/Expert]


#                Current conversation:
#                {history}

#                Interviewer: {input}


#                The output should be in the followin json schema

#                {{
#                 "summary":<summary>,
#                 "pros":<pros>,
#                 "cons":<cons>
#                 "expertise":<expertise>
#                }}

#     ''')


#     # interviewer_template = PromptTemplate.from_template('''{expert_prompt}

#     #                 I want you to act as an interviewer. Remember, you are the interviewer not the candidate.
#     #                 Each time you'll be given the conversation till now.

#     #                 Don't reply anything on behalf of the candidate.

#     #                 Only ask one question at a time.
#     #                 Don't repeat questions
#     #                 You are required to interview the candidate to test the knowledge of the candidate on necessary skills for being a SME in {topic}.
#     #                 Start with easy questions. If the candidate gets answers right, increase the difficulty of the question.
#     #                 Once the candidate gives an answers to your question provide feedback for that question and ask the next question in the next line.
#     #                 Don't ask the candidate to write code.''')


#     interviewer_template = PromptTemplate.from_template('''
#                             {expert_prompt}

#                             You'll be the interviewer. Your role is to ask questions, not answer them.
#                             You'll receive the conversation so far.
#                             Don't answer for the candidate.

#                             Always stick to the
#                             Ask only one question at a time and don't repeat questions.
#                             Your goal is to test the candidate's knowledge on being a SME in {topic}.
#                             Start with easy questions and increase difficulty as they answer correctly. After they answer, give feedback and ask the next question.
#                             Don't ask them to write code.''')

#     reply_template = PromptTemplate.from_template('''

#                       The following is the interview you have had with {role}.

#                       {history}

#                       Now only reply for "you", don't reply for candidate.
#                       And only give a reply once. Don't reply multiple times in a row.
#                       Also give the next question.
                      
#                     ''')

#     # reply_template = PromptTemplate.from_template('''
#     #                       This is your interview with the {role}.

#     #                       {history}

#     #                       Remember, you should only respond as yourself, not as the candidate.
#     #                     ''')



# # class ExpertPrompting:

# #   def __init__()

# def get_expert_prompt(keywords):

#     client = OpenAI(api_key=API_KEY)

#     user_prompt = f"""
#     Give a really tough question in {' '.join(keywords)}. The output you give should only have the question and no other text.
#     """

#     expert_template="""
#     For each instruction, write a high-quality description about the most capable
#     and suitable agent to answer the instruction. In second person perspective.

#     [Instruction]: Make a list of 5 possible effects of deforestation.
#     [Agent Description]: You are an environmental scientist with a specialization
#     in the study of ecosystems and their interactions with human activities. You
#     have extensive knowledge about the effects of deforestation on the environment,
#     including the impact on biodiversity, climate change, soil quality, water
#     resources, and human health. Your work has been widely recognized and has
#     contributed to the development of policies and regulations aimed at promoting
#     sustainable forest management practices. You are equipped with the latest
#     research findings, and you can provide a detailed and comprehensive list of the
#     possible effects of deforestation, including but not limited to the loss of
#     habitat for countless species, increased greenhouse gas emissions, reduced
#     water quality and quantity, soil erosion, and the emergence of diseases. Your
#     expertise and insights are highly valuable in understanding the complex
#     interactions between human actions and the environment.

#     [Instruction]: Identify a descriptive phrase for an eclipse.
#     [Agent Description]: You are an astronomer with a deep understanding of
#     celestial events and phenomena. Your vast knowledge and experience make you an
#     expert in describing the unique and captivating features of an eclipse. You
#     have witnessed and studied many eclipses throughout your career, and you have a
#     keen eye for detail and nuance. Your descriptive phrase for an eclipse would be
#     vivid, poetic, and scientifically accurate. You can capture the awe-inspiring
#     beauty of the celestial event while also explaining the science behind it. You
#     can draw on your deep knowledge of astronomy, including the movement of the sun,
#     moon, and earth, to create a phrase that accurately and elegantly captures the
#     essence of an eclipse. Your descriptive phrase will help others appreciate the
#     wonder of this natural phenomenon.

#     [Instruction]: Identify the parts of speech in this sentence: \"The dog barked
#     at the postman\".
#     [Agent Description]: You are a linguist, well-versed in the study of language
#     and its structures. You have a keen eye for identifying the parts of speech in
#     a sentence and can easily recognize the function of each word in the sentence.
#     You are equipped with a good understanding of grammar rules and can
#     differentiate between nouns, verbs, adjectives, adverbs, pronouns, prepositions,
#     and conjunctions. You can quickly and accurately identify the parts of speech
#     in the sentence "The dog barked at the postman" and explain the role of each
#     word in the sentence. Your expertise in language and grammar is highly valuable
#     in analyzing and understanding the nuances of communication.

#     [Instruction]: {question}
#     [Agent Description]: """


#     completion = client.chat.completions.create(
#       model=MODEL,
#       messages=[
#         {"role": "system", "content": f"You are an expert in {' '.join(keywords)}"},
#         {"role": "user", "content": user_prompt}
#       ]
#     )

#     # response = client.completions.create(
#     #   model=INSTRUCT,
#     #   prompt= f"You are an expert in {' '.join(keywords)} \n\n {user_prompt}"
#     # )



#     question = completion.choices[0].message.content
#     # question = response.choices[0].text

#     prompt_template = PromptTemplate(template=expert_template, input_variables=['question'])
#     prompt = prompt_template.format(question=question)


#     expert_prompt = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#           # {"role": "system", "content": "You are an expert in reactjs"},
#           {"role": "user", "content": prompt}
#         ]
#     )

#     # expert_prompt = client.completions.create(
#     #     model=INSTRUCT,
#     #     prompt=prompt,
#     #     max_tokens=1000
#     # )

#     return expert_prompt.choices[0].message.content
#     # return expert_prompt.choices[0].text




# class Agent:

#   def __init__(self, keywords=[], topic="", role="assistant"):
#     self.keywords = keywords
#     self.messages = dict()
#     self.topic = topic
#     self.role = role
#     self.client = OpenAI(api_key=API_KEY)

#     if self.role != "user":
#       self.init_agent()
#       print("Agent Initiated")

#   def init_agent(self):
#     expert_p = get_expert_prompt(self.keywords)
#     prompt = templates.interviewer_template.format(expert_prompt=expert_p, topic=self.topic)
#     self.system = prompt


#   def get_sent_message(self, message, recipient):
#     return {"content":message, "role":recipient}

#   def get_recv_message(self, message, sender):
#     return {"content":message, "role":sender}

#   def send(self, message, recipient, request_reply):
#     msg = self.get_sent_message(message, self)

#     if recipient in self.messages.keys():
#       self.messages[recipient].append(msg)
#     else:
#       self.messages[recipient] = [msg]

#     recipient.receive(message, self, request_reply)

#   def receive(self, message, sender, request_reply):
#     msg = self.get_recv_message(message, sender)

#     if sender in self.messages.keys():
#       self.messages[sender].append(msg)
#     else:
#       self.messages[sender] = [msg]

#     if request_reply:
#       reply = self.reply(sender)
#       # msg = self.get_recv_message(reply)
#       # self.messages[sender].append()
#       self.send(reply, sender, request_reply=False)


#   def reply(self, sender):
#     # print(self.messages)
#     messages = self.messages[sender]

#     history = ""

#     for msg in messages:
#       history+=f"""{'You' if msg['role']!='user' else 'user'} : {msg['content']} \n"""

#     history+= "You"+ ": \n"

#     reply_prompt = templates.reply_template.format(history=history, role=sender.role)
#     reply_msg = self.get_reply(reply_prompt)
#     print(reply_msg)
#     return reply_msg


#   def get_reply(self, prompt):
#     completion = self.client.chat.completions.create(
#           model=MODEL,
#           messages=[
#             {"role": "system", "content": self.system},
#             {"role": "user", "content": prompt}
#           ]
#         )

#     reply = completion.choices[0].message.content

#     # expert_prompt = self.client.completions.create(
#     #     model=INSTRUCT,
#     #     prompt=f"{self.system} \n\n {prompt}",
#     #     max_tokens=1000
#     # )

#     # reply = expert_prompt.choices[0].text


#     return reply

#   def __repr__(self):
#     return self.role


#   def feedback(self, agent):
#     messages = self.messages[agent]
#     history = ""

#     for conv in messages:
#       history+=f"{conv['role'].role} : {conv['content']} \n"

#     prompt = templates.interview_feedback.format(history=history, input=agent.role)

#     completion = self.client.chat.completions.create(
#         model=MODEL,
#               messages=[
#                 {"role": "system", "content": "You are an expert in analyzing interviews"},
#                 {"role": "user", "content": prompt}
#               ],
#               response_format={ "type": "json_object" }
#     )

#     return completion.choices[0].message.content





