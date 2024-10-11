from flask import Flask
from source_websites.source_website_routes import source_website_bp

app = Flask(__name__)

# Register the blueprint for source website routes
app.register_blueprint(source_website_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)