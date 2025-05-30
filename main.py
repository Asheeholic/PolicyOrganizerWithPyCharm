from config.config import create_app
from routes.main_routes import main
from routes.file_routes import file_bp
from routes.auth_routes import auth

app = create_app()

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(file_bp)
app.register_blueprint(auth)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)