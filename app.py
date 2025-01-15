from flask import Flask
from config import Config
from models import db
from models import User
from routes import init_routes 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

        
with app.app_context():
    
    User.create_admin(app)
    db.create_all()

init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
    





