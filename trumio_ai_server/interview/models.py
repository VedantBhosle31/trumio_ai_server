from django.db import models
import chromadb
import numpy as np
from typing import List, Union
from chromadb.utils import embedding_functions
from django.conf import settings


from .kg import SubGrapher

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
        
        text_embed = self.embed([text])

        col.add(
            embeddings=text_embed,
            ids=[uid]
        )

    def add_to_projects(self, uid: str, text: str) -> None:
        col = self.get_collection("projects")
        text_embed = self.embed([text])

        col.add(
            embeddings=text_embed,
            ids=[uid]
        )

    def add_to_teams(self, uids: List[str], team_id: Union[str, int], project_id: str) -> None:
        col = self.get_collection("profiles")

        embeds = col.get(ids=uids, include=['embeddings'])['embeddings']

        print(embeds)

        teams = self.get_collection("teams")
        teams.add(
            embeddings=[list(np.mean(embeds, axis=0))],
            ids=[str(team_id)],
            metadatas=[{"project_id":project_id}]
            )
    


store = VectorStore()

subgraphers = dict({
    'ai':SubGrapher('ai.json', 0.25),
    'frontend':SubGrapher('frontend.json', 0.25),
    'backend':SubGrapher('backend.json', 0.25)
})