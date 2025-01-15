import os
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User , HousewiseSolutions, HousewiseSolutionRequest
from datetime import datetime
from collections import defaultdict



def init_routes(app):
    
    @app.route("/", methods=["GET"])
    def homepage():
        return render_template("homepage.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(user_name=username).first()
            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["is_customer"] = user.is_customer
                session["is_service_professional"] = user.is_service_professional
                session["username"] = username

                if user.is_service_professional:
                    user_type = "service_professional"
                    if not user.is_approved:
                        flash("Please wait for admin approval", "danger")
                        return redirect(url_for("login"))
                    if user.service_id is None:
                        flash(
                            "Your requested service ID is not available. Please create a new account with a different service ID.",
                            "danger",
                        )
                        return redirect(url_for("login"))
                    return redirect("/" + user_type + "_dashboard")

                if user.is_customer:
                    user_type = "customer"
                    flash("Login successful", "success")
                    return redirect("/" + user_type + "_dashboard")

            flash(
                "Login unsuccessful, please check username and password",
                "danger")
        return render_template("login.html")

    # Customer routes
    @app.route("/register_customer", methods=["GET", "POST"])
    def reg_customer():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            address = request.form["address"]
            pincode = request.form["pincode"]

            user = User.query.filter_by(user_name=username).first()
            if user:
                flash("User already exists", category="error")
                return redirect(url_for("register_customer"))

            hashed_pass = generate_password_hash(password)
            user = User(
                user_name=username,
                email_id=email,
                password=hashed_pass,
                address=address,
                pincode=pincode,
                is_customer=True,
                is_approved=True,
            )
            db.session.add(user)
            db.session.commit()
            flash("User registered successfully. Please login.", "success")
            return redirect(url_for("login"))

        return render_template("register_customer.html")

    @app.route("/customer_dashboard", methods=["GET", "POST"])
    def customer_dashboard():
        if not session.get("is_customer"):
            flash("Please login first", "danger")
            return redirect(url_for("login"))

        customer = User.query.filter_by(
            user_name=session.get("username")).first()
        services = HousewiseSolutions.query.all()
        ser_history = HousewiseSolutionRequest.query.filter_by(
            customer_id=customer.id
        ).all()
        return render_template(
            "customer_dashboard.html",
            services=services,
            ser_history=ser_history)

    @app.route(
        "/customer_dashboard/create_service_request/<int:service_id>",
        methods=["GET", "POST"],
    )
    def create_service_request(service_id):
        if not session.get("is_customer"):
            flash("Please login first", "danger")
            return redirect(url_for("login"))

        if request.method == "POST":
            service_professional_username = request.form.get(
                "service_professional")
            desc = request.form.get("desc", "")
            status = request.form.get("status", "pending")
            deadline_str = request.form.get("deadline")
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            date_created_str = request.form.get("date_created")
            date_created = datetime.strptime(date_created_str, "%Y-%m-%d")

            service_professional = User.query.filter_by(
                user_name=service_professional_username
            ).first()
            if not service_professional:
                flash("Service professional not found", "danger")
                return redirect(url_for("customer_dashboard"))

            customer = User.query.filter_by(
                user_name=session["username"]).first()
            service_request = HousewiseSolutionRequest(
                customer_id=customer.id,
                deadline=deadline,
                service_professional_id=service_professional.id,
                service_id=service_id,
                desc=desc,
                request_type="private",
                status=status,
                date_created=date_created,
            )

            db.session.add(service_request)
            db.session.commit()
            flash("Service request created successfully", "success")
            return redirect(url_for("customer_dashboard"))

        service = HousewiseSolutions.query.get(service_id)
        service_professional = (
            User.query.join(HousewiseSolutions)
            .filter(
                User.is_service_professional,
                User.is_approved,
                HousewiseSolutions.id == service_id,
            )
            .all()
        )

        return render_template(
            "create_service_request.html",
            service=service,
            service_professional=service_professional,
        )

    @app.route("/customer_dashboard/edit_request/<int:request_id>",methods=["GET", "POST"])
    def edit_request(request_id):
        if not session.get("is_customer"):
            flash("Please login first", "danger")
            return redirect(url_for("login"))

        service_request = HousewiseSolutionRequest.query.get(request_id)
        if request.method == "POST":
            desc = request.form.get("desc")
            service_request.desc = desc
            db.session.commit()
            flash("Service request updated successfully", "success")
            return redirect(url_for("customer_dashboard"))

        return render_template(
            "edit_request.html",
            service_request=service_request)

    @app.route("/customer_dashboard/delete_request/<int:request_id>",methods=["GET", "POST"])
    def delete_request(request_id):
        if not session.get("is_customer"):
            flash("Please login first", "danger")
            return redirect(url_for("login"))

        service_request = HousewiseSolutionRequest.query.get(request_id)
        db.session.delete(service_request)
        db.session.commit()
        flash("Service request deleted successfully", "success")
        return redirect(url_for("customer_dashboard"))

    @app.route("/customer_dashboard/search", methods=["GET", "POST"])
    def search():
        if not session.get("is_customer"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service = HousewiseSolutions.query.first()

        search_type = request.args.get("search_type")
        search_query = request.args.get("search_query")

        query = HousewiseSolutions.query.join(
            User, HousewiseSolutions.id == User.service_id
        ).filter(User.is_approved)

        if search_type and search_query:
            if search_type == "pincode":
                query = query.filter(User.pincode.like("%" + search_query))
            elif search_type == "service_name":
                query = query.filter(HousewiseSolutions.service_name.like("%" + search_query))
            elif search_type == "username":
                query = query.filter(User.user_name.like("%" + search_query))
            elif search_type == "address":
                query = query.filter(User.address.like("%" + search_query))

        services = query.all()

        return render_template("customer_search.html",services=services,
                customer_name=session["username"])
    
    @app.route("/customer_dashboard/rate_request/<int:request_id>",methods=["GET", "POST"])
    def rate_request(request_id):
        if not session.get("is_customer"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service_request = HousewiseSolutionRequest.query.get(request_id)
        if not service_request:
            flash("service request not found", "danger")
            return redirect(url_for("customer_dashboard"))

        if request.method == "POST":
            review = request.form["review"]
            rating = request.form["rating"]

            service_request.status = "closed"
            service_request.ratingby_customer = float(rating)
            service_request.reviewby_customer = review
            service_request.date_closed = datetime.now().date()

            cont_reviewupdate = User.query.get(service_request.customer_id)
            temp = cont_reviewupdate.rating_count
            cont_reviewupdate.rating_count = cont_reviewupdate.rating_count + 1
            cont_reviewupdate.avgrating = (cont_reviewupdate.avgrating * temp + float(rating)) / (temp + 1)
            service_request.is_rated = True
            db.session.commit()

            flash("Thank you for your review", "success")
            return redirect(url_for("customer_dashboard"))


        service_professional = service_request.service_professional.user_name
        customer = service_request.customer.user_name
        service = service_request.service.service_name
        return render_template("rate_request.html",request_id=request_id,service_request=service_request,customer=customer,service_professional=service_professional,
        service=service,)


    @app.route("/customer_dashboard/close_request/<int:request_id>",methods=["GET", "POST"])
    def close_request(request_id):
        if not session.get("is_customer"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service_request = HousewiseSolutionRequest.query.get(request_id)
        if not service_request:
            flash("service request not found", "danger")
            return redirect(url_for("customer_dashboard"))

        if request.method == "POST":
            service_request.status = "closed"
            db.session.commit()
            flash("Request closed successfully", "success")
            return redirect(url_for("customer_dashboard"))

        return render_template(
        "close_request.html",
        request_id=request_id,
        service_request=service_request)


    @app.route("/customer_dashboard/summary", methods=["GET", "POST"])
    def summary():
        if not session.get("is_customer"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        user_id = session.get("user_id")
        customer = User.query.get(user_id)
        ser_history = HousewiseSolutionRequest.query.filter_by(customer_id=customer.id ).all()

        requests_per_month = defaultdict(int)
        for request in ser_history:
            month = request.date_created.strftime("%Y-%m")
            requests_per_month[month] += 1

        ratings_and_reviews = []
        for request in ser_history:
            if request.ratingby_customer:
                ratings_and_reviews.append((request.service_professional.user_name,
                    request.ratingby_customer,
                    request.reviewby_customer,))

        return render_template(
        "customer_summary.html",
        requests_per_month=dict(requests_per_month),
        ratings_and_reviews=ratings_and_reviews,
    )


# Service professional routes
    @app.route("/register_service_professional", methods=["GET", "POST"])
    def register_service_professional():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            address = request.form.get("address")
            pincode = request.form.get("pincode")
            ser_pro_file = request.files.get("ser_pro_file")
            ser_pro_exp = request.form.get("ser_pro_exp")
            service = request.form.get("service")

            if not all([username, password, address, pincode,ser_pro_file, ser_pro_exp, service]):
                flash(
                "All fields are required. Please fill out the entire form.",
                "danger")
            return redirect(url_for("register_service_professional"))

        service_obj = HousewiseSolutions.query.filter_by(
            service_name=service).first()
        if not service_obj:
            flash("Selected service not found", "danger")
            return redirect(url_for("register_service_professional"))

        user = User.query.filter_by(user_name=username).first()
        if user:
            flash(
                "User already exists, please choose a different username",
                "danger")
            return redirect(url_for("register_service_professional"))

        file_name = secure_filename(ser_pro_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]
            renamed_file = f"{username}{file_ext}"
            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                flash("Invalid file extension.", "danger")
                return redirect(url_for("register_service_professional"))
            ser_pro_file.save(
                os.path.join(
                    app.config["UPLOAD_PATH"],
                    renamed_file))
        else:
            renamed_file = None

            new_user = User(
            user_name=username,
            email_id= email,
            password=generate_password_hash(password),
            is_service_professional=True,
            address=address,
            pincode=pincode,
            ser_pro_file=renamed_file,
            ser_pro_exp=ser_pro_exp,
            service_id=service_obj.id,
            is_approved=False,

            )
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful, please login", "success")
            return redirect(url_for("login"))
        services = HousewiseSolutions.query.all()
        return render_template("register_service_professional.html", services=services)


    @app.route("/service_professional_dashboard", methods=["GET", "POST"])
    def service_professional_dashboard():
        if not session.get("is_service_professional"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        print("Session username:", session.get("username"))
        print("Session is_service_professional:",
        session.get("is_service_professional"))

        service_professional = User.query.filter_by(user_name=session.get("username")).first()
        if not service_professional.is_approved:
            flash("please wait for admin approval", "danger")
            return redirect(url_for("login"))

        pending_req = HousewiseSolutionRequest.query.filter_by(service_professional_id=service_professional.id, status="pending").all()

        accepted_req = HousewiseSolutionRequest.query.filter_by(service_professional_id=service_professional.id, status="accepted").all()
        closed_req = HousewiseSolutionRequest.query.filter_by(service_professional_id=service_professional.id, status="closed").all()

        return render_template( "service_professional_dashboard.html",pending_req=pending_req, accepted_req=accepted_req, closed_req=closed_req, )



    @app.route("/service_professional_dashboard/accept_req/<int:request_id>",methods=["GET", "POST"],)
    def accept_req(request_id):

        service_request = HousewiseSolutionRequest.query.get(request_id)
        if service_request:

            service_request.status = "accepted"
            db.session.commit()
            flash("Request accepted successfully", "success")
        else:
            flash("Request not found", "danger")
            return redirect(url_for("service_professional_dashboard"))
   

    @app.route("/service_professional_dashboard/reject_req/<int:request_id>",methods=["GET", "POST"],)
    def reject_req(request_id):

        service_request = HousewiseSolutionRequest.query.get(request_id)
        if request.method == "POST":

            service_request.status = "rejected"
            db.session.commit()
            flash("Request rejected successfully", "success")
        else:
            flash("Request not found", "danger")
        return redirect(url_for("service_professional_dashboard"))


    @app.route("/service_professional_dashboard/search", methods=["GET", "POST"])
    def ser_search():
        if not session.get("is_service_professional"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        service = HousewiseSolutions.query.first()
        print(service.__dict__)

        search_type = request.args.get("search_type")
        search_query = request.args.get("search_query")

        print(f"search type :{search_type}, search query :{search_query}")
        query = HousewiseSolutions.query.join(User, HousewiseSolutions.id == User.service_id).filter(User.is_approved)
        if search_query:
            if search_type == "pincode":
                query = query.filter(User.pincode.like("%" + search_query))
            elif search_type == "service_name":
                query = query.filter(
                HousewiseSolutions.service_name.like("%" + search_query))
            elif search_type == "username":
                query = query.filter(User.user_name.like("%" + search_query))
            elif search_type == "address":
                query = query.filter(User.address.like("%" + search_query))
        services = query.all()

        print(f"found:{services}")
        return render_template(
        "ser_pro_search.html",
        services=services,
        customer_name=session["username"])


    @app.route( "/service_professional_dashboard/rate_customer/<int:request_id>", methods=["GET", "POST"])
    def rate_customer(request_id):
        if not session.get("is_service_professional"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service_request = HousewiseSolutionRequest.query.get(request_id)
        if not service_request:
            flash("Service request not found", "danger")
            return redirect(url_for("service_professional_dashboard"))

        if request.method == "POST":
            rating = request.form["rating"]
            review = request.form["review"]

            service_request.ratingby_service_professional = float(rating)
            service_request.reviewby_service_professional = review
            db.session.commit()

            flash("Customer rated successfully", "success")
            return redirect(url_for("service_professional_dashboard"))

        return render_template("rate_customer.html",request_id=request_id,service_request=service_request)


# admin routes
    @app.route("/hws_admin", methods=["GET", "POST"])
    def hws_admin():
        if request.method == "POST":
            session.clear()
            username = request.form["username"]
            password = request.form["password"]

            admin = User.query.filter_by(user_name=username).first()
        
            if admin and check_password_hash(admin.password, password):
                session["username"] = username
                session["password"] = password
                session["is_admin"] = True

                print("Admin session set:", session.get("is_admin"))

                print("Admin logged in!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                print("Incorrect username or password", "danger")
                print("Admin login failed - Invalid credentials or user not found")

        return render_template("hws_admin.html")


    @app.route("/admin_dashboard", methods=["GET", "POST"])
    def admin_dashboard():
        if not session.get("is_admin"):
            flash("Please login first", "danger")
            return redirect(url_for("hws_admin"))

        services = HousewiseSolutions.query.all()
        requests = HousewiseSolutionRequest.query.all()
        unapproved_service_professionals = User.query.filter_by(is_service_professional=True, is_approved=False).all()
        approved_service_professionals = User.query.filter_by(is_service_professional=True, is_approved=True).all()
        registered_customers = User.query.filter_by(is_customer=True, is_approved=True).all()
        blocked_customers = User.query.filter_by(is_customer=True, is_blocked=True).all()
        blocked_service_professionals = User.query.filter_by(
        is_service_professional=True, 
        is_blocked=True ).all()
        return render_template(
        "admin_dashboard.html",
        services=services,
        requests=requests,
        approved_service_professionals=approved_service_professionals,
        unapproved_service_professionals=unapproved_service_professionals,
        registered_customers=registered_customers,
        blocked_customers=blocked_customers,
        blocked_service_professionals=blocked_service_professionals,
    )


    @app.route("/admin_dashboard/create_service", methods=["GET", "POST"])
    def create_service():
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        if request.method == "POST":
            service_name = request.form["service_name"]
            service_desc = request.form["service_desc"]
            baseprice = request.form["baseprice"]
            time_req = request.form["time_req"]

            new_service = HousewiseSolutions(
            service_name=service_name,
            service_desc=service_desc,
            baseprice=baseprice,
            time_req=time_req,
        )

            db.session.add(new_service)
            db.session.commit()
            flash("Service created successfully", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("create_service.html")


    @app.route("/edit_service/<int:service_id>", methods=["GET", "POST"])
    def edit_service(service_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        service = HousewiseSolutions.query.get(service_id)
        if request.method == "POST":
            service.service_name = request.form["service_name"]
            service.service_desc = request.form["service_desc"]
            service.baseprice = request.form["baseprice"]
            service.time_req = request.form["time_req"]
            db.session.commit()
            flash("Service updated successfully", "success")
            return redirect(url_for("admin_dashboard"))

        return render_template("edit_service.html", service=service)


    @app.route("/delete_service/<int:service_id>", methods=["GET", "POST"])
    def delete_service(service_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service = HousewiseSolutions.query.get(service_id)
        approved_service_professionals = User.query.filter_by(is_approved=True, is_service_professional=True, service_id=service_id).all()
        for service_professional in approved_service_professionals:
            service_professional.is_approved = False
            db.session.delete(service)
            db.session.commit()
            flash("Service deleted successfully", "success")
            return redirect(url_for("admin_dashboard"))


    @app.route("/admin_dashboard/view_service_professional/<int:service_professional_id>",methods=["GET", "POST"] )
    def view_service_professional(service_professional_id):
            if not session.get("is_admin"):
                flash("please login first", "danger")
                return redirect(url_for("login"))
            service_professional = User.query.get(service_professional_id)
            reviews = HousewiseSolutionRequest.query.filter_by(service_professional_id=service_professional_id ).all()
            return render_template(
        "view_service_professional.html",
        service_professional=service_professional,
        reviews=reviews,
    )


    @app.route(
    "/admin_dashboard/approve_service_professional/<int:service_professional_id>",
    methods=[
        "GET",
        "POST"],
)
    def approve_service_professional(service_professional_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service_professional = User.query.get(service_professional_id)
        if service_professional is None:
            flash("Service professional not found", "danger")
            return redirect(url_for("admin_dashboard"))

        try:
            service_professional.is_approved = True
            db.session.commit()
            flash("Service professional approved successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash("Service professional approval failed", "danger")
            

        return redirect(url_for("admin_dashboard"))


    @app.route( "/admin_dashboard/reject_service_professional/<int:service_professional_id>",methods=["POST"])
    def reject_service_professional(service_professional_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service_professional = User.query.get(service_professional_id)
        pdf_file = service_professional.ser_pro_file
        pathfile =None
        if pdf_file:
            pathfile = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file)
        if os.path.exists(pathfile):
            try:
                os.remove(pathfile)
                print("file deleted successfully")
            except Exception as e:
                print("Error while deleting file:", e)
        else:
            print("File does not exist")
        db.session.delete(service_professional)
        db.session.commit()
        flash("Service professional rejected successfully", "success")

        return redirect(url_for("admin_dashboard"))


    @app.route("/admin_dashboard/block_service_professional/<int:service_professional_id>", methods=["GET"])
    def block_service_professional(service_professional_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        service_professional = User.query.get(service_professional_id)
        if service_professional:
            service_professional.is_approved = False
            service_professional.is_blocked = True
            db.session.commit()
            flash("service proffesional blocked successfully", "success")
            return redirect(url_for("admin_dashboard"))


    @app.route("/admin_dashboard/unblock_service_professional/<int:service_professional_id>", methods=["POST"]  )
    def unblock_service_professional(service_professional_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))

        service_professional = User.query.get(service_professional_id)
        if service_professional:
            service_professional.is_blocked = False
            db.session.commit()
            flash("Service professional unblocked successfully", "success")
        return redirect(url_for("admin_dashboard"))


    @app.route("/admin_dashboard/view_customer/<int:customer_id>",methods=["GET", "POST"])
    def view_customer(customer_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        customer = User.query.get(customer_id)
        return render_template("view_customer.html", customer=customer)

    @app.route("/admin_dashboard/block_customer/<int:customer_id>", methods=["POST"])
    def block_customer(customer_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        customer = User.query.get(customer_id)
        if customer:
            customer.is_blocked = True
            db.session.commit()
        flash("customer blocked successfully", "success")
        return redirect(url_for("admin_dashboard"))


    @app.route("/admin_dashboard/unblock_customer/<int:customer_id>",methods=["POST"])
    def unblock_customer(customer_id):
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        customer = User.query.get(customer_id)
        if customer:
            customer.is_blocked = False
            db.session.commit()
        flash("customer unblocked successfully", "success")
        return redirect(url_for("admin_dashboard"))


    @app.route("/search", methods=["GET", "POST"])
    def admin_search():
        if not session.get("is_admin"):
            flash("please login first", "danger")
            return redirect(url_for("login"))
        service = HousewiseSolutions.query.first()
        
        search_type = request.form.get("search_type")
        search_query = (
            request.form.get("search_query").strip()
            if request.form.get("search_query")
            else None )
        query = HousewiseSolutions.query.join(User, HousewiseSolutions.id == User.service_id ).filter(User.is_approved)
        if search_type == "service_professional":
            query = User.query.filter(
            User.is_service_professional,
            User.user_name.like("%" + search_query))
        if search_type == "customer":
            query = User.query.filter( User.is_customer, User.user_name.like("%" + search_query))

        services = query.all()

        return render_template("admin_search.html",services=services,results=services,search_type=search_type,customer_name=session["username"])

    @app.route("/logout")
    def logout():
        session.pop("username", None)
        session.pop("is_admin", None)
        session.pop("is_service_professional", None)
        session.pop("is_customer", None)
        flash("logged out successfully", "success")
        return redirect(url_for("homepage"))
