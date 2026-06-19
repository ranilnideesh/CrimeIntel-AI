import re
from typing import Dict, Any, List

# Regular expressions for entity mining
REGEX_PATTERNS = {
    "Vehicle": r"\b([A-Z]{2}[-\s]?\d{2}[-\s]?[A-Z]{1,2}[-\s]?\d{4})\b|(?i)\b(Mahindra|Maruti|Hyundai|Honda|Toyota|SUV|Sedan|Truck|Pickup|Bike|Scooter)\b",
    "Weapon": r"(?i)\b(gas cutter|torch|pistol|revolver|gun|knife|dagger|crowbar|axe|rifle|bomb|explosive|hammer)\b",
    "Time": r"\b(\d{1,2}[:.]\d{2}\s*(?:AM|PM|am|pm)?|\d{2}\s*hours|\d{1,2}\s*(?:o'clock))\b",
    "Event": r"(?i)\b(heist|robbery|burglary|theft|ransomware|hijack|assault|murder|phishing|extortion|fraud|cyberattack)\b",
}

# Simple dictionary lists for Name and Location extraction
KNOWN_PERSONS = ["Rajesh", "Vicky", "Ashok", "Sharma", "Verma", "Das", "Singh", "Rajesh alias Scar", "Vicky alias Gas-Cutter", "Ashok Kale"]
KNOWN_LOCATIONS = ["Connaught Place", "Delhi", "Noida", "Gurgaon", "Bengaluru", "Lonavala", "Mumbai", "Pune Expressway", "Navi Mumbai", "Haryana"]

class ForensicOcrNlpEngine:
    """Simulates OCR document scanning and a spaCy / BERT Transformer Named Entity Recognition pipeline."""
    
    def extract_text_from_file(self, filepath: str) -> str:
        """Simulate extracting raw text from PDF/Image using OCR."""
        basename = filepath.lower()
        if "fir" in basename or "cp_heist" in basename:
            return (
                "FIRST INFORMATION REPORT. Under Section 379/457 of Indian Penal Code. "
                "Police Station: Connaught Place, New Delhi. Date: 2026-06-19. "
                "Complainant: Ramesh Khanna, owner of Khanna Jewelers. "
                "Accused: Two unidentified males. Modus Operandi: Safe cracking using gas cutters and torches. "
                "Witness saw suspect Rajesh alias Scar and another accomplice Vicky fleeing in a white Mahindra pickup "
                "with registration plate DL-3C-AS-9988 at approximately 02:30 AM."
            )
        elif "witness" in basename or "statement" in basename:
            return (
                "Witness Statement of Security Guard Satish Kumar. "
                "I was on duty at Connaught Place jewelry block when I saw a suspicious white Mahindra SUV. "
                "Two guys got out holding gas cylinders and tools. I was held at gunpoint. "
                "One guy was called Vicky and the other had a visible scar on his hand. "
                "They cut the vault gate in 15 minutes. They left toward Noida Expressway at 02:45 AM."
            )
        elif "ransomware" in basename or "cyber" in basename:
            return (
                "Incident Report: PayNext Fintech Server Encryption. "
                "Server log highlights breach via compromised workstation. System files encrypted by ransomware. "
                "Attacker left readme.txt demanding 5 BTC. Key IPs logged: 185.220.101.44. "
                "Time of execution: 11:45 PM on June 18."
            )
        
        return "Anonymized police record. Standard investigation folder details and logs recorded."

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Perform entity extraction using regex patterns and dictionary lookups."""
        entities = {
            "Person": [],
            "Place": [],
            "Time": [],
            "Vehicle": [],
            "Weapon": [],
            "Event": []
        }
        
        # 1. Dictionary extraction for Person and Place
        for name in KNOWN_PERSONS:
            if re.search(r"\b" + re.escape(name) + r"\b", text, re.IGNORECASE):
                if name not in entities["Person"]:
                    entities["Person"].append(name)
                    
        for loc in KNOWN_LOCATIONS:
            if re.search(r"\b" + re.escape(loc) + r"\b", text, re.IGNORECASE):
                if loc not in entities["Place"]:
                    entities["Place"].append(loc)
                    
        # 2. Regex pattern extraction
        for label, pattern in REGEX_PATTERNS.items():
            matches = re.finditer(pattern, text)
            for m in matches:
                val = m.group(0).strip()
                if val and val not in entities[label]:
                    # Clean double matches
                    entities[label].append(val)
                    
        return entities

# Instantiate engine
ocr_nlp_engine = ForensicOcrNlpEngine()

def get_ocr_nlp_engine():
    return ocr_nlp_engine
