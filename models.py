from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash
# from werkzeug.utils import secure_filename


db = SQLAlchemy()


class HousewiseSolutions(db.Model):
    __tablename__ = 'housewisesolutions'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(80), unique=True, nullable=False)
    service_desc = db.Column(db.String(80), nullable=False)
    baseprice = db.Column(db.Integer, nullable=False)
    time_req = db.Column(db.Integer, nullable=False)
    
    service_professionals = db.relationship('User', back_populates='service')
    requests = db.relationship('HousewiseSolutionRequest', back_populates='service')  

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email_id = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(80), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_customer = db.Column(db.Boolean, default=False)
    is_service_professional = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    avgrating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    ser_pro_file = db.Column(db.String(80), nullable=True)
    ser_pro_exp = db.Column(db.String(80), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('housewisesolutions.id'), nullable=True)

    service = db.relationship('HousewiseSolutions', back_populates='service_professionals')  
    customer_requests = db.relationship('HousewiseSolutionRequest', back_populates='customer', foreign_keys='HousewiseSolutionRequest.customer_id') 
    service_professional_requests = db.relationship('HousewiseSolutionRequest', back_populates='service_professional', foreign_keys='HousewiseSolutionRequest.service_professional_id')
    @staticmethod 
    def create_admin(app):
        with app.app_context():
            admin_user = User.query.filter_by(is_admin = True).first()
            if not admin_user:
                admin_user = User(user_name = 'admin',email_id = 'mahagaonkarneha11@gmail.com', password = generate_password_hash("neha"), address = "Aurangabad", pincode ='431001', is_admin = True, is_approved = True )
                db.session.add(admin_user)
                db.session.commit()
                print("Admin User created Succesfully") 
 
        
class HousewiseSolutionRequest(db.Model):
    __tablename__ = 'housewisesolutionrequest'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('housewisesolutions.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    request_type = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.DateTime,default = datetime.now())
    deadline = db.Column(db.DateTime, nullable=True)
    date_closed = db.Column(db.DateTime,default = datetime.now())
    is_rated = db.Column(db.Boolean, default=False)
    ratingby_customer = db.Column(db.Float, default=0.0)
    ratingby_service_professional = db.Column(db.Float, default=0.0)
    reviewby_customer = db.Column(db.String(80), nullable=True)
    timetaken = db.Column(db.String(80), nullable=True)
    total_cost = db.Column(db.Integer, nullable=True)

    
    service = db.relationship('HousewiseSolutions', back_populates='requests')
    customer = db.relationship('User', back_populates='customer_requests', foreign_keys=[customer_id])
    service_professional = db.relationship('User', back_populates='service_professional_requests', foreign_keys=[service_professional_id])
    


    
