import torch

# Check if a GPU is available and use it if possible
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Set the path to your dataset and configuration
data_yaml_path = 'path/to/data.yaml'  # YAML file defining your dataset
model_yaml = 'yolov8n.yaml'  # Choose a model architecture (n, s, m, l, x)

# Load the YOLOv8 model
model = torch.hub.load('ultralytics/yolov8', model=model_yaml, pretrained=True)

# Train the model
model.train(data=data_yaml_path, epochs=50, imgsz=640, batch=16, device=device)

# Save the trained model
model.save('path/to/save/model.pt')
