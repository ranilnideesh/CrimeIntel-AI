from typing import Dict, Any, List, Tuple
from app.neo4j_db import get_graph_db

# Try loading networkx for graph analysis, fallback gracefully
try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

class InvestigationGraphAnalyzer:
    """Simulates Graph Neural Network link prediction, connection finding, and anomaly detection."""
    
    def generate_evidence_graph_nodes(self, case_id_or_number: str) -> Dict[str, Any]:
        """Fetch all nodes and edges linked to a specific case context."""
        graph_db = get_graph_db()
        full_graph = graph_db.get_graph()
        
        # Filter nodes and edges associated with this case
        # For simplicity in local mode, we return the entire seed graph centered on the cases
        # but structured cleanly for frontend D3 / SVG renderers.
        nodes = []
        edges = []
        
        # Convert dictionary to list format for D3
        for n_id, n_meta in full_graph["nodes"].items():
            nodes.append({
                "id": n_id,
                "label": n_meta.get("name") or n_meta.get("plate") or n_meta.get("type") or n_id,
                "type": n_meta.get("label"), # Case, Suspect, Vehicle, Location, Weapon
                "properties": n_meta
            })
            
        for edge in full_graph["edges"]:
            edges.append({
                "source": edge["source"],
                "target": edge["target"],
                "type": edge["type"]
            })
            
        return {"nodes": nodes, "links": edges}

    def predict_link_probabilities(self, case_id: str) -> List[Dict[str, Any]]:
        """Simulates Graph Neural Network link prediction to predict suspect connections."""
        # Returns simulated predictions of connection probability based on shared attributes
        return [
            {"source": "SUSP_RAJESH", "target": "WEAP_GAS_CUTTER", "probability": 0.88, "reason": "Associated with 2 prior safe breaking offenses using gas cutters."},
            {"source": "SUSP_VICKY", "target": "LOC_CP", "probability": 0.94, "reason": "Owned vehicle DL-3C-AS-9988 was logged near Connaught Place 15 mins post-heist."},
            {"source": "SUSP_RAJESH", "target": "LOC_NOIDA", "probability": 0.72, "reason": "Co-offender Vicky has verified safehouses in Noida."}
        ]

    def calculate_case_risk_score(self, case_details: Dict[str, Any], evidence_items: List[Dict[str, Any]]) -> float:
        """
        Calculate an actionable case risk score from 0 to 100.
        Factors:
        - Financial impact (Crores / Millions mentioned in description)
        - Threat indicators (gas cutters, guns, ransomware, poison)
        - Evidence volume (chain-of-custody counts)
        - Density of relationship graph connections
        """
        score = 20.0 # Base risk
        desc = case_details.get("description", "").lower()
        
        # 1. Financial Impact
        if "crore" in desc or "cr" in desc or "lakh" in desc:
            score += 25.0
        elif "btc" in desc or "bitcoin" in desc or "ransom" in desc:
            score += 20.0
            
        # 2. Weapon / Violence Severity
        if "gun" in desc or "pistol" in desc or "revolver" in desc:
            score += 25.0
        elif "poison" in desc or "drugged" in desc:
            score += 20.0
        elif "gas cutter" in desc or "torch" in desc:
            score += 15.0
            
        # 3. Evidence quantity
        score += min(len(evidence_items) * 4.0, 20.0)
        
        # 4. Cap at 100.0, minimum 10.0
        return min(max(score, 10.0), 98.0)

# Instantiate analyzer
graph_analyzer = InvestigationGraphAnalyzer()

def get_graph_analyzer():
    return graph_analyzer
