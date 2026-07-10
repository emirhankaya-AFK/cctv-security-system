import cv2
import json
import time
import os
from datetime import datetime
from detector import SecurityDetector
from telegram_notifier import TelegramNotifier

# Paths
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
ALERTS_DIR = os.path.join(os.path.dirname(__file__), "alerts")

# Global variables for mouse callback
drawing_points = []
window_name = "Guvenlik Bolgesi Secimi"

def mouse_callback(event, x, y, flags, param):
    global drawing_points
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing_points.append([x, y])
        print(f"Nokta eklendi: [{x}, {y}]")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] Config dosyasi bulunamadi: {CONFIG_PATH}")
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)
    print("[INFO] Yeni ayarlar config.json dosyasina kaydedildi.")

def get_polygon_from_user(video_source):
    global drawing_points
    drawing_points = []
    
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"[ERROR] Video kaynagi acilamadi: {video_source}")
        return []
        
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("[ERROR] Ilk kare okunamadi. Pencere acilamiyor.")
        return []
        
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print("\n=== GÜVENLİK BÖLGESİ ÇİZİM KILAVUZU ===")
    print("1. Fare sol tiklamasiyla yasakli bolgenin koselerini belirle.")
    print("2. Secimleri sifirlamak icin 'c' tusuna bas.")
    print("3. Cizimi onaylayip kaydetmek icin 's' veya 'ENTER' tusuna bas.")
    print("4. Cikis yapmak icin 'q' tusuna bas.")
    
    while True:
        temp_frame = frame.copy()
        
        # Draw points and lines of the polygon
        if len(drawing_points) > 0:
            for pt in drawing_points:
                cv2.circle(temp_frame, tuple(pt), 5, (0, 0, 255), -1)
            if len(drawing_points) > 1:
                for i in range(len(drawing_points) - 1):
                    cv2.line(temp_frame, tuple(drawing_points[i]), tuple(drawing_points[i+1]), (0, 255, 0), 2)
                # Close the polygon visually
                cv2.line(temp_frame, tuple(drawing_points[-1]), tuple(drawing_points[0]), (0, 255, 0), 1)
                
        cv2.imshow(window_name, temp_frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            drawing_points = []
            print("[INFO] Secimler temizlendi.")
        elif key == ord('s') or key == 13: # 's' or Enter
            if len(drawing_points) >= 3:
                print(f"[INFO] {len(drawing_points)} noktali bolge onaylandi.")
                break
            else:
                print("[WARN] En az 3 nokta secmelisiniz!")
        elif key == ord('q'):
            print("[INFO] Secim iptal edildi.")
            drawing_points = []
            break
            
    cv2.destroyWindow(window_name)
    return drawing_points

def main():
    # Make alerts directory
    if not os.path.exists(ALERTS_DIR):
        os.makedirs(ALERTS_DIR)
        
    config = load_config()
    if not config:
        return
        
    video_source = config.get("video_source", 0)
    polygon_points = config.get("polygon_points", [])
    
    # If polygon is not set, ask the user to draw one
    if not polygon_points or len(polygon_points) < 3:
        print("[INFO] Guvenlik bolgesi tanimli degil. Lutfen cizim yapin.")
        polygon_points = get_polygon_from_user(video_source)
        if not polygon_points:
            print("[INFO] Guvenlik bolgesi secilmedigi icin program sonlandiriliyor.")
            return
        config["polygon_points"] = polygon_points
        save_config(config)
        
    # Initialize components
    detector = SecurityDetector(model_path=config.get("model_path", "yolov8n.pt"))
    notifier = TelegramNotifier(token=config.get("telegram_token", ""), chat_id=config.get("telegram_chat_id", ""))
    
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"[ERROR] Video kaynagi baslatilamadi: {video_source}")
        return
        
    print("\n[INFO] Guvenlik sistemi baslatildi. Cikis yapmak icin 'q', bolgeyi yeniden cizmek icin 'r' tusuna basabilirsiniz.")
    
    last_alert_time = 0
    cooldown = config.get("cooldown_seconds", 10)
    
    main_window_name = "CCTV Guvenlik Sistemi"
    cv2.namedWindow(main_window_name)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] Video akisi bitti veya kare okunamadi.")
            break
            
        # Run detection
        detections = detector.detect(frame)
        
        # Check intrusion status
        intrusion_detected = False
        intruder_boxes = []
        
        for det in detections:
            box = det['box']
            is_inside = detector.is_inside_polygon(box, polygon_points)
            if is_inside:
                intrusion_detected = True
                intruder_boxes.append((box, True))
            else:
                intruder_boxes.append((box, False))
                
        # Draw the polygon (RED if intrusion, GREEN if clear)
        poly_color = (0, 0, 255) if intrusion_detected else (0, 255, 0)
        cv2.polylines(frame, [np.array(polygon_points, dtype=np.int32)], True, poly_color, 3)
        
        # Overlay semi-transparent background on the polygon for high-end look
        overlay = frame.copy()
        cv2.fillPoly(overlay, [np.array(polygon_points, dtype=np.int32)], poly_color)
        alpha = 0.15  # transparency factor
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Draw bounding boxes
        for box, is_intruder in intruder_boxes:
            x1, y1, x2, y2 = box
            box_color = (0, 0, 255) if is_intruder else (0, 255, 255)
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            # Label
            label = "IHLALCI" if is_intruder else "Kisi"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
            # Draw feet point
            cv2.circle(frame, (int((x1 + x2) / 2), y2), 5, (255, 0, 0), -1)
            
        # Draw system status text
        status_text = "DURUM: TEHLIKE (IHLAL!)" if intrusion_detected else "DURUM: GUVENLI"
        status_color = (0, 0, 255) if intrusion_detected else (0, 255, 0)
        cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 3)
        
        # Process Alerts
        current_time = time.time()
        if intrusion_detected and (current_time - last_alert_time) > cooldown:
            last_alert_time = current_time
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            alert_filename = f"alarm_{timestamp_str}.jpg"
            alert_path = os.path.join(ALERTS_DIR, alert_filename)
            
            # Save the frame
            cv2.imwrite(alert_path, frame)
            print(f"[ALARM] Sinir ihlali! Görüntü kaydedildi: {alert_path}")
            
            # Send notification
            caption_msg = f"🚨 *GÜVENLİK BÖLGESİ İHLALİ!*\n📅 Tarih/Saat: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n⚠️ Tespit: İhlal Bölgesinde Kişi Mevcut!"
            notifier.send_photo(alert_path, caption=caption_msg)
            
        cv2.imshow(main_window_name, frame)
        
        # Key listener
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Redraw polygon
            print("[INFO] Bolge sifirlaniyor, yeniden cizilecek...")
            cv2.destroyWindow(main_window_name)
            polygon_points = get_polygon_from_user(video_source)
            if polygon_points:
                config["polygon_points"] = polygon_points
                save_config(config)
            else:
                # If draw is cancelled, keep the old one or exit
                polygon_points = config.get("polygon_points", [])
            cv2.namedWindow(main_window_name)
            
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] CCTV Guvenlik Sistemi kapatildi.")

import numpy as np

if __name__ == "__main__":
    main()
