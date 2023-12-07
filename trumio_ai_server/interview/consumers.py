import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .customagent import Agent


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        
        # Join room group
        # await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # await self.set_agents()

    async def set_agents(self, topic, subtopics):
        self.inter = Agent(subtopics, topic, role="assistant")
        self.user = Agent(role="user")
        await self.send(text_data=json.dumps({"info":"agent initialized"}))


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg_type = text_data_json['type']

        if msg_type=="chat":
            message = text_data_json["message"]


        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat.message", "message": message}
        # )

            await self.send_msg(message)

            

            await sync_to_async(self.user.send)(message, self.inter, request_reply=True)

            reply = self.user.messages[self.inter][-1]['content']

            if len(self.user.messages[self.inter])>10:
                print("Interview Done")
                await self.get_feedback(self.inter)

            await self.send_msg(reply)

            

        elif msg_type=="topic":

            topic = text_data_json['topic']
            subs = text_data_json['subtopics']

            await self.set_agents(topic, subs)



    async def send_msg(self, message):
        await self.send(text_data=json.dumps({"message": message}))

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def get_feedback(self, agent):
        feedback = await sync_to_async(self.user.feedback)(agent)
        print(json.loads(feedback))


