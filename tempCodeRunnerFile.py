def create_admin():
    
    with app.app_context():
        admin_user = User.query.filter_by(is_admin = True).first()
        if not admin_user:
            admin_user = User(user_name = 'admin',email_id = 'mahagaonkarneha11@gmail.com', password = generate_password_hash("neha"), address = "Aurangabad", pincode ='431001', is_admin = True, is_approved = True )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin User created Succesfully") 
 
        
        
with app.app_context():
    db.create_all()
    create_admin()