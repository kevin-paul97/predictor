import sys
import os
from pathlib import Path

import torch
from PIL import Image

# Add the submodule to the Python path
SUBMODULE_DIR = str(Path(__file__).resolve().parent.parent / "fantastic-palm-tree")
sys.path.insert(0, SUBMODULE_DIR)

from config import Config
from models import create_location_regressor
from datasets import create_transforms

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")


class Predictor:
    def __init__(self):
        self.config = Config()
        self.device = torch.device("cpu")
        self.model = create_location_regressor(self.config)
        checkpoint = torch.load(MODEL_PATH, map_location=self.device, weights_only=True)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.transform = create_transforms(image_size=64, grayscale=True)

    @torch.no_grad()
    def predict(self, image: Image.Image) -> dict:
        image = image.convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        output = self.model(tensor).squeeze(0)
        longitude, latitude = output[0].item(), output[1].item()
        return {"longitude": longitude, "latitude": latitude}
