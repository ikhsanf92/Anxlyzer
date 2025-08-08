import os
import requests

MODEL_PATH = "model_rf_sm.pkl"
URL = "https://drive.google.com/uc?export=download&id=1XgdO-VzZZZ1z7jk6MdzlBRfjYuI3z_BD"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model file...")
        r = requests.get(URL, stream=True)
        with open(MODEL_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Download complete.")
    else:
        print("Model already exists.")

if __name__ == "__main__":
    download_model()
