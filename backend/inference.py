from ultralytics import YOLO
import cv2
import os
import time
import uuid
from datetime import datetime

model = YOLO('yolov8n.pt')  # Contoh: 'models/best.pt' atau 'yolov8n_custom.pt'

CUSTOM_LABELS = {
    2: 'car',     # Contoh
    5: 'bus',    # Contoh
    7: 'truck'      # Contoh
}

def run_inference(image_path, conf=0.3, iou=0.5):
    try:
        # Start timing
        start_time = time.time()
        
        # Load gambar
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Get image dimensions
        original_height, original_width = img.shape[:2]
        
        # Path output: dari uploads/nama.jpg → static/result_nama.jpg
        basename = os.path.basename(image_path)
        name, ext = os.path.splitext(basename)
        output_name = f"result_{name}{ext}"
        output_path = os.path.join("static", output_name)

        # Ensure static directory exists
        os.makedirs("static", exist_ok=True)

        # Save original image (without bounding boxes)
        cv2.imwrite(output_path, img)
        
        # ✅ PERBAIKAN: Handle threshold 100% (1.0)
        if conf >= 1.0:
            # Jika threshold 100%, langsung return tanpa deteksi
            total_time = time.time() - start_time
            
            response = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "image_info": {
                    "path": output_path,
                    "url": f"/static/{os.path.basename(output_path)}",
                    "original_name": basename,
                    "dimensions": {
                        "width": original_width,
                        "height": original_height,
                        "aspect_ratio": round(original_width / original_height, 2)
                    },
                    "file_size": round(os.path.getsize(image_path) / 1024, 2)  # KB
                },
                "inference_info": {
                    "model": "custom_3class_model",
                    "confidence_threshold": conf,
                    "iou_threshold": iou,
                    "inference_time": 0,  # Tidak ada inference
                    "total_processing_time": round(total_time * 1000, 2),
                    "model_classes": len(CUSTOM_LABELS)
                },
                "predictions": [],  # Kosong
                "detection_summary": {
                    "total_detections": 0,
                    "class_statistics": {},
                    "confidence_stats": {
                        "min": 0,
                        "max": 0,
                        "avg": 0
                    },
                    "detected_classes": []
                },
                "summary": "No objects detected in the image (confidence threshold: 100%)."
            }
            
            return response
        
        # ✅ PERBAIKAN: Batasi conf maksimal 0.999 untuk model
        # Untuk menghindari edge case dimana model mengembalikan confidence = 1.0
        model_conf = min(conf, 0.999)
        
        # Run inference
        inference_start = time.time()
        results = model(img, conf=model_conf, iou=iou)
        inference_time = time.time() - inference_start

        # Extract predictions in the required format
        predictions = []
        class_counts = {}
        confidence_scores = []
        
        # Check if there are any detections
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            for i, box in enumerate(results[0].boxes):
                cls_id = int(box.cls[0])
                conf_score = float(box.conf[0])
                
                # Validasi class ID (hanya 0, 1, 2 untuk 3 class)
                if cls_id not in CUSTOM_LABELS:
                    print(f"Warning: Detected unknown class ID {cls_id}, skipping...")
                    continue
                
                # ✅ PERBAIKAN: Filter yang lebih strict
                # Gunakan < bukan >= untuk memastikan tidak ada yang lolos saat conf = 1.0
                if conf_score < conf:
                    continue
                
                # Get xyxy coordinates
                xyxy_coords = [float(x) for x in box.xyxy[0]]
                x1, y1, x2, y2 = xyxy_coords
                
                # Convert to center x, y, width, height format
                width = x2 - x1
                height = y2 - y1
                center_x = x1 + (width / 2)
                center_y = y1 + (height / 2)
                
                # Get class name dari custom labels
                class_name = CUSTOM_LABELS[cls_id]
                
                # Generate unique detection ID
                detection_id = str(uuid.uuid4())
                
                prediction = {
                    "x": round(center_x, 1),
                    "y": round(center_y, 1),
                    "width": round(width, 1),
                    "height": round(height, 1),
                    "confidence": round(conf_score, 3),
                    "class": class_name,
                    "class_id": cls_id,
                    "detection_id": detection_id,
                    "area": round(width * height, 1),
                    "xyxy": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "position": get_position_description(center_x, center_y, original_width, original_height),
                    "relative_position": {
                        "x": round(center_x / original_width, 4),
                        "y": round(center_y / original_height, 4),
                        "width": round(width / original_width, 4),
                        "height": round(height / original_height, 4)
                    }
                }
                
                predictions.append(prediction)
                confidence_scores.append(conf_score)
                
                # Count classes
                if class_name in class_counts:
                    class_counts[class_name] += 1
                else:
                    class_counts[class_name] = 1

        # Calculate statistics
        total_time = time.time() - start_time
        
        # Create response in the requested format
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "image_info": {
                "path": output_path,
                "url": f"/static/{os.path.basename(output_path)}",
                "original_name": basename,
                "dimensions": {
                    "width": original_width,
                    "height": original_height,
                    "aspect_ratio": round(original_width / original_height, 2)
                },
                "file_size": round(os.path.getsize(image_path) / 1024, 2)  # KB
            },
            "inference_info": {
                "model": "custom_3class_model",  # Update sesuai nama model Anda
                "confidence_threshold": conf,
                "iou_threshold": iou,
                "inference_time": round(inference_time * 1000, 2),  # milliseconds
                "total_processing_time": round(total_time * 1000, 2),  # milliseconds
                "model_classes": len(CUSTOM_LABELS)
            },
            "predictions": predictions,
            "detection_summary": {
                "total_detections": len(predictions),
                "class_statistics": class_counts,
                "confidence_stats": {
                    "min": round(min(confidence_scores), 3) if confidence_scores else 0,
                    "max": round(max(confidence_scores), 3) if confidence_scores else 0,
                    "avg": round(sum(confidence_scores) / len(confidence_scores), 3) if confidence_scores else 0
                },
                "detected_classes": list(class_counts.keys())
            },
            "summary": generate_detection_summary(class_counts, len(predictions))
        }

        return response
        
    except Exception as e:
        # Return error response
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def get_position_description(center_x, center_y, img_width, img_height):
    """
    Menentukan posisi objek dalam gambar (kiri, tengah, kanan, atas, bawah)
    """
    # Horizontal position
    if center_x < img_width * 0.33:
        h_pos = "left"
    elif center_x < img_width * 0.67:
        h_pos = "center"
    else:
        h_pos = "right"
    
    # Vertical position
    if center_y < img_height * 0.33:
        v_pos = "top"
    elif center_y < img_height * 0.67:
        v_pos = "middle"
    else:
        v_pos = "bottom"
    
    return f"{v_pos}-{h_pos}"

def generate_detection_summary(class_counts, total_detections):
    """
    Generate human-readable summary of detections
    """
    if total_detections == 0:
        return "No objects detected in the image."
    
    summary_parts = []
    for class_name, count in class_counts.items():
        if count == 1:
            summary_parts.append(f"1 {class_name}")
        else:
            # Handle plural forms properly
            plural_name = class_name + ("es" if class_name.endswith(("s", "x", "ch", "sh")) else "s")
            summary_parts.append(f"{count} {plural_name}")
    
    if len(summary_parts) == 1:
        return f"Detected {summary_parts[0]} in the image."
    elif len(summary_parts) == 2:
        return f"Detected {summary_parts[0]} and {summary_parts[1]} in the image."
    else:
        return f"Detected {', '.join(summary_parts[:-1])}, and {summary_parts[-1]} in the image."

def get_model_info():
    """
    Mengembalikan informasi tentang model custom yang digunakan
    """
    return {
        "model_name": "Custom YOLOv8 Model",
        "model_type": "Object Detection",
        "classes": list(CUSTOM_LABELS.values()),
        "total_classes": len(CUSTOM_LABELS),
        "class_mapping": CUSTOM_LABELS,
        "input_size": "640x640",  # Update jika berbeda
        "framework": "Ultralytics",
        "output_format": "xywh_with_confidence"
    }

def verify_model():
    """
    Fungsi untuk memverifikasi model dan menampilkan informasi
    """
    print("=== Model Information ===")
    print(f"Model path: {model.model.__class__.__name__}")
    print(f"Number of classes: {model.model.nc if hasattr(model.model, 'nc') else 'Unknown'}")
    
    # Coba ambil nama class dari model
    if hasattr(model, 'names'):
        print(f"Model class names: {model.names}")
    else:
        print(f"Using custom labels: {CUSTOM_LABELS}")
    
    print("========================")

# Legacy function untuk backward compatibility (jika masih ada kode yang menggunakan format lama)
def run_inference_legacy(image_path, conf=0.3, iou=0.5):
    """
    Legacy function yang return tuple (output_path, boxes) untuk backward compatibility
    """
    result = run_inference(image_path, conf, iou)
    
    if result["success"]:
        # Extract old format
        output_path = result["image_info"]["path"]
        boxes = []
        
        for prediction in result["predictions"]:
            box = {
                "class_id": prediction["class_id"],
                "label": prediction["class"],
                "confidence": prediction["confidence"],
                "xyxy": prediction["xyxy"]
            }
            boxes.append(box)
        
        return output_path, boxes
    else:
        raise Exception(result["error"])

# Alternative: jika ingin tetap menggunakan format tuple tapi dengan data baru
def run_inference_tuple(image_path, conf=0.3, iou=0.5):
    """
    Alternative function yang return tuple (response, status) 
    """
    result = run_inference(image_path, conf, iou)
    status = "success" if result["success"] else "error"
    return result, status

# Test function
if __name__ == "__main__":
    # Verifikasi model saat file dijalankan langsung
    verify_model()
    
    # Test dengan gambar sample jika ada
    test_image = "test.jpg"  # Ganti dengan path gambar test Anda
    if os.path.exists(test_image):
        result = run_inference(test_image)
        if result["success"]:
            print(f"Test successful! Detected {result['detection_summary']['total_detections']} objects")
            print(f"Classes: {result['detection_summary']['detected_classes']}")
        else:
            print(f"Test failed: {result['error']}")