from typing import List, Union

import numpy as np
from django.conf import settings
import chromadb
from chromadb.utils import embedding_functions
from django.db import models


from .kg import SubGrapher

HOST = settings.VECTOR_HOST
PORT = settings.VECTOR_PORT


class VectorStore:
    """
    A class for managing vector storage using chromadb.

    Attributes:
        client: chromadb.HttpClient
            Chromadb HTTP client for communication with the vector database.
        embed: embedding_functions.SentenceTransformerEmbeddingFunction
            Sentence transformer embedding function for creating text embeddings.
    """


    def __init__(self) -> None:
        """
        Initializes the VectorStore.

        Sets up the chromadb HTTP client and the Sentence Transformer embedding function.
        """
        
        self.client = chromadb.HttpClient(host=HOST, port=PORT)
        self.embed = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=settings.EMBEDDING)

    def get_collection(self, name: str) -> chromadb.Collection:
        """
        Retrieves or creates a collection with the specified name.

        Parameters:
            name (str): Name of the collection.

        Returns:
            chromadb.Collection: The requested or created collection.
        """
        return self.client.get_or_create_collection(name=name, embedding_function=self.embed, metadata={"hnsw:space": "cosine"})

    def add_to_profile(self, uid: str, text: str) -> None:
        """
        Adds a text entry to the 'profiles' collection.

        Parameters:
            uid (str): User ID.
            text (str): Text data to be stored.

        Returns:
            None
        """
        col = self.get_collection("profiles")
        
        text_embed = self.embed([text])

        col.add(
            embeddings=text_embed,
            ids=[uid]
        )

    def add_to_projects(self, uid: str, text: str) -> None:
        """
        Adds a text entry to the 'projects' collection.

        Parameters:
            uid (str): User ID.
            text (str): Text data to be stored.

        Returns:
            None
        """
        col = self.get_collection("projects")
        text_embed = self.embed([text])

        col.add(
            embeddings=text_embed,
            ids=[uid]
        )

    def add_to_teams(self, uids: List[str], team_id: Union[str, int], project_id: str) -> None:
        """
        Adds team members to the 'teams' collection.

        Parameters:
            uids (List[str]): List of user IDs.
            team_id (Union[str, int]): ID of the team.
            project_id (str): ID of the associated project.

        Returns:
            None
        """
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