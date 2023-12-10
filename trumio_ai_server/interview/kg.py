# dependencies install: pip3 install typing torch json numpy transformers django

from typing import List, Dict
import torch
import json
import numpy as np
from torch import nn
from torch.nn import functional as F
from transformers import AutoTokenizer, AutoModel
from bisect import insort

from django.conf import settings

torch.set_grad_enabled(False)

MODEL = f"sentence-transformers/{settings.EMBEDDING}"


class SubGrapher:
    def __init__(self, graph_filename, threshold=0.5):
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
        for i, node in enumerate(self.graph["nodes"]):
            if int(node["id"]) != i + 1:
                raise ValueError("Nodes not set properly")
        for edge in self.graph["edges"]:
            if int(edge["source"]) >= int(edge["target"]):
                raise ValueError("Edges not set properly")

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[
            0
        ]  # First element of model_output contains all token embeddings
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModel.from_pretrained(MODEL)

    def encode(self, sentences: List[str]):
        encoded_input = self.tokenizer(
            sentences, padding=True, truncation=True, return_tensors="pt"
        )
        model_output = self.model(**encoded_input)
        sentence_embeddings = self.mean_pooling(
            model_output, encoded_input["attention_mask"]
        )
        return F.normalize(sentence_embeddings, p=2, dim=1)

    def load_people(self, filename: str) -> List[Dict]:
        with open(filename, "r") as file:
            self.people = json.load(file)
        return self.people

    def load_person(self, filename: str) -> Dict:
        with open(filename, "r") as file:
            self.person = json.load(file)
        return self.person

    def load_graph(self, filename: str) -> Dict:
        with open(filename, "r") as file:
            self.graph = json.load(file)
            self.nodes = self.graph["nodes"]
            self.edges = self.graph["edges"]
            self.node_values = [node["skill"] for node in self.nodes]
        return self.graph

    def write_to_file(self, object: Dict, filename: str) -> None:
        with open(filename, "w") as file:
            json.dump(object, file)

    def encode_node_values(self):
        self.node_encoding = self.encode(self.node_values)

    def get_similar_nodes(self, resume_vec):
        similarities = F.threshold(
            self.cosine(resume_vec, self.node_encoding),
            self.threshold,
            0,
        )
        return np.where(similarities >= self.threshold)[-1] + 1

    def set_topic_nodes(self):
        self.topic_nodes = []
        for edge in self.edges:
            if edge["source"] == "1":
                self.topic_nodes.append(self.nodes[int(edge["target"]) - 1])

    def get_topic_proficiency(self, nodes: List[int], head: str = "1"):
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
        if people == None:
            people = self.people
        subgraphs = []
        for person in people:
            subgraphs.append(self.get_subgraph(person))
        return subgraphs

    def to_json(self, object, filename: str):
        with open(filename, "w") as file:
            json.dump(object, file)

    def get_uncompleted_nodes_breadth(self, nodes: List[int], breadth_head: str = "1"):
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
        distance = 0
        for node in nodes:
            distance += self.graph["nodes"][int(node) - 1]["distance"]
        try:
            return distance / (len(nodes) * self.max_depth)
        except:
            return 0

    def set_max_depth(self):
        self.max_depth = 0
        for node in self.graph["nodes"]:
            self.max_depth = max(self.max_depth, node["distance"])

    def set_max_breadth(self):
        self.max_breadth = 0
        for edge in self.graph["edges"]:
            if edge["source"] == "1":
                self.max_breadth += 1

    def _save_supergraph(self, filename: str):
        self.graph["max_depth"] = self.max_depth
        self.graph["inv_max_breadth"] = 1 / self.max_breadth
        self.graph["subdomains"] = self.topic_nodes
        with open(filename, "w") as file:
            json.dump(self.graph, file)
