from app import create_app
from download_model import download_model

download_model()
app = create_app()

if __name__ == '__main__':
    app.run()
