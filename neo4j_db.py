import json
import os
import threading
from typing import Dict, Any, List, Tuple
from app.config import settings

class JSONGraphDB:
    """A thread-safe local JSON Graph Store to simulate Neo4j using NetworkX-like structure."""
    def __init__(self, filepath: str = "./crimeintel_graphdb.json"):
        self.filepath = filepath
        self.lock = threading.Lock()
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump({"nodes": {}, "edges": []}, f)

    def _read(self) -> Dict[str, Any]:
        with open(self.filepath, "r") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> str:
        with self.lock:
            data = self._read()
            properties["id"] = node_id
            properties["label"] = label
            data["nodes"][node_id] = properties
            self._write(data)
            return node_id

    def add_edge(self, source_id: str, target_id: str, relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        with self.lock:
            data = self._read()
            if source_id not in data["nodes"] or target_id not in data["nodes"]:
                return False
            
            # Prevent duplicate edges
            for edge in data["edges"]:
                if edge["source"] == source_id and edge["target"] == target_id and edge["type"] == relationship_type:
                    return True
            
            data["edges"].append({
                "source": source_id,
                "target": target_id,
                "type": relationship_type,
                "properties": properties or {}
            })
            self._write(data)
            return True

    def get_graph(self) -> Dict[str, Any]:
        with self.lock:
            return self._read()

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        with self.lock:
            data = self._read()
            neighbors = []
            for edge in data["edges"]:
                if edge["source"] == node_id:
                    target_node = data["nodes"].get(edge["target"])
                    if target_node:
                        neighbors.append({"relationship": edge["type"], "node": target_node})
                elif edge["target"] == node_id:
                    source_node = data["nodes"].get(edge["source"])
                    if source_node:
                        neighbors.append({"relationship": edge["type"], "node": source_node})
            return neighbors

    def find_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        """BFS implementation for finding shortest path between nodes."""
        with self.lock:
            data = self._read()
            if start_id not in data["nodes"] or end_id not in data["nodes"]:
                return []
            
            # Build adjacency list
            adj = {n_id: [] for n_id in data["nodes"]}
            for edge in data["edges"]:
                s, t = edge["source"], edge["target"]
                adj[s].append(t)
                adj[t].append(s)
            
            # BFS
            queue = [[start_id]]
            visited = {start_id}
            
            while queue:
                path = queue.pop(0)
                node = path[-1]
                if node == end_id:
                    return path
                for neighbor in adj.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = list(path)
                        new_path.append(neighbor)
                        queue.append(new_path)
            return []

# Initialize graph database connection (Dual Mode)
if settings.NEO4J_URI:
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
        print("Connected successfully to Neo4j database.")
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}. Falling back to Local JSON Graph DB.")
        driver = JSONGraphDB()
else:
    print("No NEO4J_URI provided. Operating in Local JSON Graph DB Mode.")
    driver = JSONGraphDB()

def get_graph_db():
    return driver
