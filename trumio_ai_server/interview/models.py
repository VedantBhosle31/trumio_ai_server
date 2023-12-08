from django.db import models
import chromadb
import numpy as np
from chromadb.utils import embedding_functions
from django.conf import settings

HOST = settings.VECTOR_HOST
PORT = settings.VECTOR_PORT

class VectorStore:

    def __init__(self):
        self.client = chromadb.HttpClient(host=HOST, port=PORT)
        self.embed = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        # self.collection = self.client.get_collection()
        print('IT raan')

    def get_collection(self, name):

        return self.client.get_collection(name=name, embedding_function=self.embed)

    def add_to_profile(self, uid, text):

        col = self.get_collection("profiles")
        text_embed = self.embed(text)

        col.add(
            embeddings = text_embed,
            ids = [uid]
        )

    def add_to_projects(self, uid, text):

        col = self.get_collection("projects")
        text_embed = self.embed(text)

        col.add(
            embeddings = text_embed,
            ids = [uid]
        )

    def add_to_teams(self, uids,id):

        col = self.get_collection("students")

        embeds = col.get(ids=uids, include=['embeddings'])['embeddings']

        teams = self.get_collection("teams")   
        teams.add(
            embeddings = np.mean(embeds, axis=0),
            ids = [str(id)]
        )

    


store = VectorStore()