from app import app
import logging

# Set up logging for easier debugging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
