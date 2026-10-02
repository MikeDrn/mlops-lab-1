import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import torch
from torchvision import transforms
import mlflow.pyfunc

app = FastAPI(title="Food11 Classification API")

# Read MLflow tracking URI from environment, defaulting to local server
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Class labels for Food11 dataset
CLASS_NAMES = [
    "Bread", "Dairy product", "Dessert", "Egg", "Fried food", 
    "Meat", "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit"
]

# Standard image transformations matching PyTorch training pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Global model container
model = None

@app.on_event("startup")
def load_registered_model():
    global model
    try:
        # Load the registered model version pointing to @champion
        model = mlflow.pyfunc.load_model("models:/food11@champion")
        print("Successfully loaded model from MLflow Registry with alias '@champion'")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor_image = transform(image).unsqueeze(0)  # Add batch dimension

        # Run inference through MLflow PyFunc model
        preds = model.predict(tensor_image.numpy())
        probabilities = torch.softmax(torch.tensor(preds), dim=1)[0]
        predicted_idx = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_idx].item()

        return {
            "prediction": CLASS_NAMES[predicted_idx],
            "confidence": round(confidence, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image processing: {str(e)}")