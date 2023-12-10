# dependencies install: pip3 install typing torch json numpy transformers django

from typing import List, Dict
from bisect import insort
import json

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers import AutoTokenizer, AutoModel
from django.conf import settings


torch.set_grad_enabled(False)

MODEL = f"sentence-transformers/{settings.EMBEDDING}"


class SubGrapher:
    """
    Performs subgraph analysis on a given graph using sentence embeddings

    Usage:
    sub_grapher = SubGrapher(graph_filename, threshold)
    sub_grapher.load_people(json_filename)
    sub_graphs = sub_grapher.get_subgraphs()
    sub_grapher.to_json(sub_graphs, json_filename)

    Benchmarks:
    get_subgraphs(): ~0.4s per person
    get_subgraph(): ~0.4s per call
    """

    def __init__(self, graph_filename: str, threshold: float = 0.5):
        """
        Initializes the SubGrapher instance.

        Parameters:
            graph_filename (str): The filename of the graph JSON file.
            threshold (float): Similarity threshold for subgraph analysis.

        Returns:
            None
        """

        """
        Initializes the SubGrapher instance.

        Parameters:
            graph_filename (str): The filename of the graph JSON file.
            threshold (float): Similarity threshold for subgraph analysis.

        Returns:
            None
        """
        self.threshold = threshold
        self.load_model()
        self.cosine = nn.CosineSimilarity(dim=1)
        self.load_graph(graph_filename)
        self.check_graph()
        self.encode_node_values()
        self.set_max_depth()
        self.set_max_breadth()
        self.set_topic_nodes()

    def check_graph(self):
        """
        Checks if the graph is properly structured for faster evaluation.

        Returns:
            None
        """
        for i, node in enumerate(self.graph["nodes"]):
            if int(node["id"]) != i + 1:
                raise ValueError("Nodes not set properly")
        for edge in self.graph["edges"]:
            if int(edge["source"]) >= int(edge["target"]):
                raise ValueError("Edges not set properly")

    def mean_pooling(self, model_output, attention_mask):
        """
        Mean pools on the model output with attention mask.

        Parameters:
            model_output: The output from the transformer model.
            attention_mask: The attention mask for the input.

        Returns:
            torch.Tensor: The mean-pooled tensor.
        """
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    def load_model(self):
        """
        Loads the transformer model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModel.from_pretrained(MODEL)

    def encode(self, sentences: List[str]):
        """
        Encodes a list of sentences into sentence embeddings.

        Args:
            sentences (List[str]): List of sentences to encode.

        Returns:
            torch.Tensor: The unnormalized sentence embeddings.
        """
        encoded_input = self.tokenizer(
            sentences, padding=True, truncation=True, return_tensors="pt"
        )
        model_output = self.model(**encoded_input)
        sentence_embeddings = self.mean_pooling(
            model_output, encoded_input["attention_mask"]
        )
        return sentence_embeddings

    def load_people(self, filename: str) -> List[Dict]:
        """
        Loads a JSON file containing information about a list of people.

        Args:
            filename (str): The filename of the JSON file.

        Returns:
            List[Dict]: Sequential loaded list of all the people.
        """
        with open(filename, "r") as file:
            self.people = json.load(file)
        return self.people

    def load_person(self, filename: str) -> Dict:
        """
        Loads a JSON file containing information about a person.

        Args:
            filename (str): The filename of the JSON file.

        Returns:
            Dict: The loaded person.
        """
        with open(filename, "r") as file:
            self.person = json.load(file)
        return self.person

    def load_graph(self, filename: str) -> Dict:
        """
        Loads the supergraph from a JSON file.

        Parameters:
            filename (str): The filename to load the JSON file.

        Returns:
            Dict: The loaded graph.
        """
        with open(filename, "r") as file:
            self.graph = json.load(file)
            self.nodes = self.graph["nodes"]
            self.edges = self.graph["edges"]
            self.node_values = [node["skill"] for node in self.nodes]
        return self.graph

    def encode_node_values(self):
        """
        Encodes node values into sentence embeddings.

        Returns:
            None
        """
        self.node_encoding = self.encode(self.node_values)

    def get_similar_nodes(self, resume_vec):
        """
        Retrieves nodes similar to a given sentence embedding.

        Args:
            resume_vec (torch.Tensor): The sentence embedding.

        Returns:
            np.ndarray: Array of node indices that are similar.
        """
        similarities = F.threshold(
            self.cosine(resume_vec, self.node_encoding),
            self.threshold,
            0,
        )
        return np.where(similarities >= self.threshold)[-1] + 1

    def set_topic_nodes(self):
        """
        Sets topic nodes based on graph edges.

        Returns:
            None
        """
        self.topic_nodes = []
        for edge in self.edges:
            if edge["source"] == "1":
                self.topic_nodes.append(self.nodes[int(edge["target"]) - 1])

    def get_topic_proficiency(self, nodes: List[int], head: str = "1"):
        """
        Computes topic proficiency based on a set of nodes.

        Args:
            nodes (List[int]): List of node indices.
            head (str): The head node identifier.

        Returns:
            Dict: Proficiency information for each topic.
        """
        proficiency = {}
        for topic_node in self.topic_nodes:
            id = topic_node["id"]
            topic = topic_node["skill"]
            proficiency[topic] = []
            for edge in self.edges:
                if (
                    edge["source"] == id
                    and self.binary_search(nodes, int(edge["target"])) != -1
                ):
                    proficiency[topic].append(
                        self.nodes[int(edge["target"]) - 1]["skill"]
                    )
            if len(proficiency[topic]) == 0:
                del proficiency[topic]
        return proficiency

    def get_similar_edges(self, nodes: List[int]):
        """
        Retrieves edges that connect similar nodes.

        Args:
            nodes (List[int]): List of node indices.

        Returns:
            List[Tuple[int, int]]: List of edge tuples.
        """
        sim_edges = []
        for edge in self.edges:
            idx = self.binary_search(nodes, int(edge["source"]))
            if idx == -1:
                continue
            idx2 = self.binary_search(nodes, int(edge["target"]))
            if idx2 == -1:
                continue
            sim_edges.append((nodes[idx], nodes[idx2]))
        return sim_edges

    def binary_search(self, arr: List[int], target: int) -> int:
        """
        Performs binary search on a sorted array.

        Args:
            arr (List[int]): The sorted array.
            target (int): The target value to search.

        Returns:
            int: Index of the target value or -1 if not found.
        """
        start = 0
        end = len(arr) - 1

        while start <= end:
            mid = (start + end) // 2
            current = arr[mid]

            if current == target:
                return mid
            if current > target:
                end = mid - 1
            else:
                start = mid + 1

        return -1

    def get_subgraph(self, resume_vec):
        """
        Generates a subgraph based on a given resume vector.

        Args:
            resume_vec (torch.Tensor): The resume vector.

        Returns:
            Dict: Subgraph information.
        """
        sim_nodes = self.get_similar_nodes(resume_vec)
        sim_edges = self.get_similar_edges(sim_nodes)
        rec_nodes, breadth = self.get_uncompleted_nodes_breadth(sim_nodes, "1")
        proficiency = self.get_topic_proficiency(sim_nodes)
        depth = self.get_depth(sim_nodes)
        subgraph = {
            "nodes": [],
            "edges": [],
            "recommended": [],
            "breadth": str(breadth),
            "depth": str(depth),
            "proficiency": proficiency,
        }
        for node in self.nodes:
            if self.binary_search(sim_nodes, int(node["id"])) != -1:
                subgraph["nodes"].append(node)
            elif self.binary_search(rec_nodes, int(node["id"])) != -1:
                subgraph["recommended"].append(node)
        for edge in sim_edges:
            subgraph["edges"].append({"source": str(edge[0]), "target": str(edge[1])})
        return subgraph

    def get_subgraphs(self, people=None):
        """
        Generates subgraphs for a list of people.

        Args:
            people (Optional[List[Dict]]): List of dictionaries containing information about people.

        Returns:
            List[Dict]: List of subgraph information.
        """
        if people == None:
            people = self.people
        subgraphs = []
        for person in people:
            subgraphs.append(self.get_subgraph(person))
        return subgraphs

    def to_json(self, object, filename: str):
        """
        Writes a dictionary object to a JSON file.

        Args:
            object (Dict): The dictionary object.
            filename (str): The filename of the JSON file.

        Returns:
            None
        """
        with open(filename, "w") as file:
            json.dump(object, file)

    def get_uncompleted_nodes_breadth(self, nodes: List[int], breadth_head: str = "1"):
        """
        Computes uncompleted nodes and breadth for a set of nodes.

        Args:
            nodes (List[int]): List of node indices.
            breadth_head (str): The head node identifier for breadth calculation.

        Returns:
            Tuple[List[int], float]: Tuple containing uncompleted nodes and breadth ratio.
        """
        prob_nodes = []
        one_step_nodes = []
        breadth = 0
        for edge in self.graph["edges"]:
            idx = self.binary_search(nodes, int(edge["source"]))
            idx2 = self.binary_search(nodes, int(edge["target"]))
            if edge["source"] == breadth_head:
                if idx2 != -1:
                    breadth += 1

            if idx == -1 or idx2 != -1:
                continue
            idx = int(edge["target"])
            if self.binary_search(prob_nodes, idx) == -1:
                insort(prob_nodes, idx)
            prob_nodes.remove(idx)
            insort(one_step_nodes, idx)
        return one_step_nodes, breadth / self.max_breadth

    def get_depth(self, nodes):
        """
        Computes depth for a set of nodes.

        Args:
            nodes (List[int]): List of node indices.

        Returns:
            float: Depth value.
        """
        distance = 0
        for node in nodes:
            distance += self.graph["nodes"][int(node) - 1]["distance"]
        try:
            return distance / (len(nodes) * self.max_depth)
        except:
            return 0

    def set_max_depth(self):
        """
        Sets the maximum depth of the graph.

        Iterates through the nodes in the graph and sets the maximum depth based on the
        "distance" attribute of each node.

        Returns:
            None
        """
        self.max_depth = 0
        for node in self.graph["nodes"]:
            self.max_depth = max(self.max_depth, node["distance"])

    def set_max_breadth(self):
        """
        Sets the maximum breadth of the graph.

        Iterates through the edges in the graph and increments the maximum breadth
        each time an edge originates from the source node "1".

        Returns:
            None
        """
        self.max_breadth = 0
        for edge in self.graph["edges"]:
            if edge["source"] == "1":
                self.max_breadth += 1

    def _save_supergraph(self, filename: str):
        """
        Saves supergraph with processed metadata

        Parameters:
         - filename (str): file to save the supergraph.

        Returns:
            None
        """
        self.graph["max_depth"] = self.max_depth
        self.graph["inv_max_breadth"] = 1 / self.max_breadth
        self.graph["subdomains"] = self.topic_nodes
        self.to_json(self.graph, filename)
