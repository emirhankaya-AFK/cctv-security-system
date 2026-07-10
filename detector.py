import cv2
import numpy as np
from ultralytics import YOLO

class SecurityDetector:
    def __init__(self, model_path, target_classes=[0]):
        """
        target_classes: COCO dataset classes to detect (default is [0] which is 'person')
        """
        self.model = YOLO(model_path)
        self.target_classes = target_classes

    def detect(self, frame):
        """
        Runs YOLO model detection on the given frame.
        Returns:
            detections: List of dicts, e.g., [{'box': [x1, y1, x2, y2], 'class': id, 'conf': score}]
        """
        results = self.model(frame, verbose=False)[0]
        detections = []
        
        for box in results.boxes:
            class_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            
            # Filter by target classes
            if class_id in self.target_classes:
                # Bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                detections.append({
                    'box': [x1, y1, x2, y2],
                    'class': class_id,
                    'conf': conf,
                    'name': results.names[class_id]
                })
        return detections

    def is_inside_polygon(self, box, polygon_points):
        """
        Checks if the bottom-center (feet) of the bounding box is inside the polygon.
        polygon_points: List of [x, y] coordinates
        """
        if not polygon_points or len(polygon_points) < 3:
            return False
            
        x1, y1, x2, y2 = box
        # Calculate bottom-center (feet position of the person)
        bottom_center = (int((x1 + x2) / 2), int(y2))
        
        # Convert polygon points to numpy array
        poly_arr = np.array(polygon_points, dtype=np.int32)
        
        # cv2.pointPolygonTest returns:
        # +1: inside, 0: on edge, -1: outside
        result = cv2.pointPolygonTest(poly_arr, bottom_center, False)
        
        return result >= 0
