import json
import os
import threading
from typing import Dict, Any, List
from app.config import settings

class JSONDocumentDB:
    """A thread-safe local JSON document store to simulate MongoDB."""
    def __init__(self, filepath: str = "./crimeintel_mongodb.json"):
        self.filepath = filepath
        self.lock = threading.Lock()
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump({"evidence_metadata": {}, "cdr_records": {}, "suspect_profiles": {}}, f)

    def _read(self) -> Dict[str, Any]:
        with open(self.filepath, "r") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        with self.lock:
            data = self._read()
            if collection_name not in data:
                data[collection_name] = {}
            doc_id = str(len(data[collection_name]) + 1)
            document["_id"] = doc_id
            data[collection_name][doc_id] = document
            self._write(data)
            return doc_id

    def find(self, collection_name: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.lock:
            data = self._read()
            collection = data.get(collection_name, {})
            results = list(collection.values())
            if not query:
                return results
            
            filtered = []
            for doc in results:
                match = True
                for k, v in query.items():
                    if doc.get(k) != v:
                        match = False
                        break
                if match:
                    filtered.append(doc)
            return filtered

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        results = self.find(collection_name, query)
        return results[0] if results else None

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        with self.lock:
            data = self._read()
            collection = data.get(collection_name, {})
            target_id = None
            for doc_id, doc in collection.items():
                match = True
                for k, v in query.items():
                    if doc.get(k) != v:
                        match = False
                        break
                if match:
                    target_id = doc_id
                    break
            
            if target_id:
                # Basic update implementation
                if "$set" in update:
                    collection[target_id].update(update["$set"])
                else:
                    collection[target_id].update(update)
                self._write(data)
                return True
            return False

# Initialize dual-mode client
if settings.MONGODB_URL:
    try:
        from pymongo import MongoClient
        client = MongoClient(settings.MONGODB_URL)
        db = client["crimeintel_db"]
        print("Connected successfully to production MongoDB.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}. Falling back to Local JSON Document DB.")
        db = JSONDocumentDB()
else:
    print("No MONGODB_URL provided. Operating in Local JSON Document DB Mode.")
    db = JSONDocumentDB()

def get_mongodb():
    return db
