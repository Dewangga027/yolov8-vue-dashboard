from ultralytics import YOLO

# Load the model
model = YOLO('yolov8n.pt')  # or your custom-trained .pt model

# Access the class names
class_names = model.names

# Print the class names
for class_id, class_name in class_names.items():
    print(f"{class_id}: {class_name}")
