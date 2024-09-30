from multiprocessing import freeze_support
from app import app

if __name__ == '__main__':
    freeze_support()
    app.run(debug=True, use_reloader=False)