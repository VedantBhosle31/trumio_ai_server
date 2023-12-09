from django.db import models
import chromadb
import numpy as np
from typing import List, Union
from chromadb.utils import embedding_functions
from django.conf import settings

HOST = settings.VECTOR_HOST
PORT = settings.VECTOR_PORT


class VectorStore:

    def __init__(self) -> None:
        self.client = chromadb.HttpClient(host=HOST, port=PORT)
        self.embed = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    def get_collection(self, name: str) -> chromadb.Collection:
        return self.client.get_or_create_collection(name=name, embedding_function=self.embed, metadata={"hnsw:space": "cosine"})

    def add_to_profile(self, uid: str, text: str) -> None:
        col = self.get_collection("profiles")
        text_embed = self.embed(text)

        col.add(
            embeddings=text_embed,
            ids=[uid]
        )

    def add_to_projects(self, uid: str, text: str) -> None:
        col = self.get_collection("projects")
        text_embed = self.embed(text)

        col.add(
            embeddings=text_embed,
            ids=[uid]
        )

    def add_to_teams(self, uids: List[str], team_id: Union[str, int]) -> None:
        col = self.get_collection("students")

        embeds = col.get(ids=uids, include=['embeddings'])['embeddings']

        teams = self.get_collection("teams")
        teams.add(
            embeddings=np.mean(embeds, axis=0),
            ids=[str(team_id)]
        )
    


store = VectorStore()