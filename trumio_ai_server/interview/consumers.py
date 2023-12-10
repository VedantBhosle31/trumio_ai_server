import json

import requests
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.conf import settings

from interview.agent.customagent import InterviewAgent
# from .customagent import Agent



class ChatConsumer(AsyncWebsocketConsumer):
    
    """
    Class for handling WebSocket communication in a chat room.

    Attributes:
        - room_name (str): The name of the chat room.
        - room_group_name (str): The name of the WebSocket room group associated with the chat room.
    """
    async def connect(self):
        """
        Connect to the WebSocket and initialize necessary attributes.

        Parameters:
            None

        Returns:
            None
        """
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        
        # Join room group
        # await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # await self.set_agents()

    async def set_agents(self, topic: str, subtopics: list[dict], domain: str, user_id: str) -> None:
        """
        Initialize conversation agents for the chat.

        Parameters:
            - topic (str): The main topic of the conversation.
            - subtopics (list): A list of subtopics related to the main topic.

        Returns:
            None
        """
        self.domain = domain
        self.user_id = user_id
        self.subtopics = subtopics

        subtopic_string = f"{subtopics[0]['skill']}"

        for subtopic in subtopics[1:]:
            subtopic_string+=f", {subtopic['skill']}"

        self.inter = InterviewAgent(topic, subtopic_string)
        print("initiated")
        # self.inter = (subtopics, topic, role="assistant")
        # self.user = Agent(role="user")
        await self.send(text_data=json.dumps({"info":"agent initialized"}))


    async def disconnect(self, close_code: int) -> None:
        """
        Disconnect from the WebSocket.

        Parameters:
            - close_code: The close code for the disconnection.

        Returns:
            None
        """
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # Receive message from WebSocket
    async def receive(self, text_data: str) -> None:
        """
        Receive and process messages from the WebSocket.

        Parameters:
            - text_data (str): The received message in JSON format.

        Returns:
            None
        """
        text_data_json = json.loads(text_data)
        msg_type = text_data_json['type']

        if msg_type=="chat":
            message = text_data_json["message"]
            

            # await sync_to_async(self.user.send)(message, self.inter, request_reply=True)
            reply = await sync_to_async(self.get_reply)(message)
            # await self.get_feedback()
            # print("Reply",reply)

            if "TERMINATE" in reply:
                reply = reply.replace("TERMINATE","")
                await self.get_feedback()
                await self.send_msg(reply)

                return

            await self.send_msg(reply)

            

        elif msg_type=="topic":

            topic = text_data_json['topic']
            subs = text_data_json['subtopics']
            domain = text_data_json['domain']
            user_id = text_data_json['user_id']

            await self.set_agents(topic, subs, domain, user_id)



    async def send_msg(self, message: str) -> None:
        """
        Send a message to the WebSocket.

        Parameters:
            - message (str): The message to be sent.

        Returns:
            None
        """
        await self.send(text_data=json.dumps({"message": message}))

    # Receive message from room group
    async def chat_message(self, event: dict) -> None:
        """
        Handle and broadcast chat messages to the room group.

        Parameters:
            - event: The event containing the chat message.

        Returns:
            None
        """
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def get_feedback(self) -> None:
        """
        Get feedback and send it through the WebSocket.

        Parameters:
            - agent: The conversation agent for which feedback is requested.

        Returns:
            None
        """
        print('before', self.subtopics)
        feedback = await sync_to_async(self.inter.get_feedback)(self.subtopics)
        await self.update_score(feedback['expertise'])
        data = dict()
        data['summary'] = feedback['summary']
        data['pros'] = feedback['pros']
        data['cons'] = feedback['cons']
        data['communication'] = feedback['communication']

        await self.send(text_data=json.dumps(data))

    
    def get_reply(self, message):
        return self.inter(message)
        
    async def update_score(self, feedback):

        ranks = ["Basic", "Proficient", "Advanced", "Expert", "Master"]
        data = feedback

        for obj in data:
            obj['expertise'] = 0 if ranks.index(obj['expertise']) < ranks.index('Advanced') else 1

        update_data = dict()

        update_data['nodes'] = data
        update_data['studentId'] = self.user_id
        update_data['domain'] = self.domain

        try:

            response = requests.post(f'{settings.RELATIONAL_BACKEND_URL}/user/updateUserDepthBreadth', update_data)

            print(response.json())

        except Exception as e:
            print(e)

        
