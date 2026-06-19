import os
import random
from typing import Dict, Any, List, Tuple

# Try loading OpenCV and PIL for genuine image marking, fallback gracefully
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Standard simulation detections based on tags in filename or random generation
SIMULATED_OBJECTS = [
    {"class": "Weapon (Handgun)", "confidence": 0.91, "color": (0, 0, 255)}, # Red
    {"class": "Vehicle (White SUV)", "confidence": 0.88, "color": (255, 165, 0)}, # Orange
    {"class": "Suspect (Face)", "confidence": 0.94, "color": (0, 255, 0)}, # Green
    {"class": "Crowbar", "confidence": 0.78, "color": (255, 255, 0)}, # Yellow
    {"class": "License Plate", "confidence": 0.96, "color": (0, 255, 255)} # Cyan
]

class CrimeObjectDetector:
    """Simulates a YOLOv8 / CNN deep learning model for computer vision investigations."""
    
    def analyze_image(self, input_path: str, output_path: str) -> List[Dict[str, Any]]:
        """
        Analyze crime scene image or CCTV frame, detect objects,
        draw bounding boxes on the image and save to output_path.
        """
        detections = []
        
        # Determine items to detect based on filename keywords (semi-deterministic for demo)
        filename = os.path.basename(input_path).lower()
        
        if "weapon" in filename or "gun" in filename or "robbery" in filename:
            detections.append(SIMULATED_OBJECTS[0]) # Weapon
            detections.append(SIMULATED_OBJECTS[2]) # Suspect Face
        elif "vehicle" in filename or "car" in filename or "cctv" in filename:
            detections.append(SIMULATED_OBJECTS[1]) # Vehicle
            detections.append(SIMULATED_OBJECTS[4]) # License Plate
        else:
            # Random selections
            detections = random.sample(SIMULATED_OBJECTS, k=random.randint(1, 3))

        # Perform drawing
        if HAS_OPENCV:
            try:
                img = cv2.imread(input_path)
                if img is not None:
                    h, w, _ = img.shape
                    drawn_detections = []
                    
                    for i, det in enumerate(detections):
                        # Generate random boxes relative to image size
                        ymin, xmin = random.randint(10, int(h/2)), random.randint(10, int(w/2))
                        ymax, xmax = random.randint(ymin + 50, h - 10), random.randint(xmin + 50, w - 10)
                        
                        box = [xmin, ymin, xmax, ymax]
                        color = det["color"]
                        
                        # Draw box
                        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 3)
                        # Draw label background
                        label = f"{det['class']} {int(det['confidence'] * 100)}%"
                        cv2.putText(img, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                        
                        drawn_detections.append({
                            "class": det["class"],
                            "confidence": det["confidence"],
                            "box": box
                        })
                    
                    cv2.imwrite(output_path, img)
                    return drawn_detections
            except Exception:
                pass
                
        if HAS_PIL:
            try:
                img = PILImage.open(input_path)
                draw = ImageDraw.Draw(img)
                w, h = img.size
                drawn_detections = []
                
                for i, det in enumerate(detections):
                    ymin, xmin = random.randint(10, int(h/2)), random.randint(10, int(w/2))
                    ymax, xmax = random.randint(ymin + 50, h - 10), random.randint(xmin + 50, w - 10)
                    
                    box = [xmin, ymin, xmax, ymax]
                    color = det["color"]
                    
                    # Draw rectangle
                    draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=3)
                    # Draw label text
                    label = f"{det['class']} {int(det['confidence'] * 100)}%"
                    draw.text((xmin, ymin - 15), label, fill=color)
                    
                    drawn_detections.append({
                        "class": det["class"],
                        "confidence": det["confidence"],
                        "box": box
                    })
                
                img.save(output_path)
                return drawn_detections
            except Exception:
                pass
                
        # If image libs are missing, just return the mock JSON coordinate array
        return [
            {
                "class": det["class"],
                "confidence": det["confidence"],
                "box": [random.randint(50, 200), random.randint(50, 200), random.randint(300, 500), random.randint(300, 500)]
            }
            for det in detections
        ]

# Instantiate detector
detector = CrimeObjectDetector()

def get_object_detector():
    return detector
