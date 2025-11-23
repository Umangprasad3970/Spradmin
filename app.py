from flask import Flask, render_template, request, redirect, url_for, session
from mongodb_setup import init_db, get_all_records, add_record, get_record_by_id, update_record, delete_record, toggle_status
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Add secret key for session management

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== ERROR HANDLING =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_message="404 - Page Not Found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", error_message="500 - Internal Server Error"), 500


# ===== ROUTES =====
@app.route("/", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            if email == "admin@admin.com" and password == "admin123":
                return redirect(url_for("dashboard"))
            else:
                return render_template("error.html", error_message="Invalid credentials")
        return render_template("login.html")
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/dashboard")
def dashboard():
    try:
        # Fetch real data from database
        restaurants = get_all_records("restaurants")
        users = get_all_records("users")

        stats = {
            "restaurants": len(restaurants),
            "total_users": len(users),
            "active_users": len([user for user in users if user.get("status") == "Active"])
        }
        admin = get_admin_data()
        return render_template("dashboard.html", stats=stats, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/user-management")
def user_management():
    try:
        users = get_all_records("users")
        admin = get_admin_data()
        return render_template("user_management.html", users=users, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/restaurant-management")
def restaurant_management():
    try:
        restaurants = get_all_records("restaurants")
        admin = get_admin_data()
        return render_template("restaurant_management.html", restaurants=restaurants, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/notification-management", methods=["GET", "POST"])
def notification_management():
    try:
        if request.method == "POST":
            title = request.form["title"]
            message = request.form["message"]
            target_type = request.form["target_type"]
            target_id = request.form.get("target_id") if request.form.get("target_id") else None
            priority = request.form["priority"]

            add_record("notifications", {
                "title": title,
                "message": message,
                "target_type": target_type,
                "target_id": target_id,
                "priority": priority
            })
            return redirect(url_for("notification_management"))

        notifications = get_all_records("notifications")
        users = get_all_records("users")
        restaurants = get_all_records("restaurants")
        admin = get_admin_data()
        return render_template("notification_management.html", notifications=notifications, users=users, restaurants=restaurants, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/subscription-plan", methods=["GET", "POST"])
def subscription_plan():
    try:
        if request.method == "POST":
            plan_name = request.form["plan_name"]
            description = request.form.get("description", "")
            duration_months = int(request.form["duration_months"])
            price = float(request.form["price"])
            features = request.form.get("features", "")
            max_restaurants = int(request.form.get("max_restaurants", 1))
            max_users = int(request.form.get("max_users", 5))

            add_record("subscription_plans", {
                "plan_name": plan_name,
                "description": description,
                "duration_months": duration_months,
                "price": price,
                "features": features,
                "max_restaurants": max_restaurants,
                "max_users": max_users
            })
            return redirect(url_for("subscription_plan"))

        plans = get_all_records("subscription_plans")
        admin = get_admin_data()
        return render_template("subscription_plan.html", plans=plans, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/subscription-history", methods=["GET", "POST"])
def subscription_history():
    try:
        if request.method == "POST":
            user_id = request.form.get("user_id")
            restaurant_id = request.form.get("restaurant_id")
            plan_id = request.form["plan_id"]
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            payment_amount = float(request.form["payment_amount"])
            payment_method = request.form.get("payment_method", "")
            auto_renew = 1 if request.form.get("auto_renew") else 0

            add_record("subscription_history", {
                "user_id": user_id,
                "restaurant_id": restaurant_id,
                "plan_id": plan_id,
                "start_date": start_date,
                "end_date": end_date,
                "payment_amount": payment_amount,
                "payment_method": payment_method,
                "auto_renew": auto_renew
            })
            return redirect(url_for("subscription_history"))

        history = get_all_records("subscription_history")
        users = get_all_records("users")
        restaurants = get_all_records("restaurants")
        plans = get_all_records("subscription_plans")
        admin = get_admin_data()
        return render_template("subscription_history.html", history=history, users=users, restaurants=restaurants, plans=plans, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    try:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            role_id = request.form["role_id"]
            contact_number = request.form.get("contact_number", "")
            add_record("users", {
                "name": name,
                "email": email,
                "password": password,
                "role_id": role_id,
                "contact_number": contact_number
            })
            return redirect(url_for("user_management"))
        roles = get_all_records("user_roles")
        return render_template("add_user.html", roles=roles)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/add-restaurant", methods=["GET", "POST"])
def add_restaurant():
    try:
        if request.method == "POST":
            restaurant_name = request.form["restaurant_name"]
            owner_id = request.form["owner_id"]
            email = request.form.get("email", "")
            contact_number = request.form.get("contact_number", "")
            address = request.form.get("address", "")
            country_id = request.form["country_id"]
            state_id = request.form["state_id"]
            city_id = request.form["city_id"]
            add_record("restaurants", {
                "restaurant_name": restaurant_name,
                "owner_id": owner_id,
                "email": email,
                "contact_number": contact_number,
                "address": address,
                "country_id": country_id,
                "state_id": state_id,
                "city_id": city_id
            })
            return redirect(url_for("restaurant_management"))
        users = get_all_records("users")
        countries = get_all_records("countries")
        states = get_all_records("states")
        cities = get_all_records("cities")
        return render_template("add_restaurant.html", users=users, countries=countries, states=states, cities=cities)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


@app.route("/admin-profile", methods=["GET", "POST"])
def admin_profile():
    try:
        # For demo purposes, we'll use a hardcoded admin user
        # In a real app, you'd get this from session or database
        admin_data = get_admin_data()

        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            contact_number = request.form.get("contact_number", "")
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            # Handle password change
            if current_password and new_password and confirm_password:
                if new_password != confirm_password:
                    return render_template("admin_profile.html", admin=admin_data, error_message="New passwords do not match")
                if current_password != admin_data.get("password"):
                    return render_template("admin_profile.html", admin=admin_data, error_message="Current password is incorrect")
            # Update password in database
            update_record("users", str(admin_data["_id"]), {"password": new_password})

            # Handle profile image upload
            profile_image_path = admin_data.get("profile_image")
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    profile_image_path = f"/static/uploads/{filename}"

            # Update the database with the new profile information
            update_record("users", str(admin_data["_id"]), {"name": name, "email": email, "contact_number": contact_number, "profile_image": profile_image_path})
            admin_data.update({
                "name": name,
                "email": email,
                "contact_number": contact_number,
                "profile_image": profile_image_path
            })
            return redirect(url_for("dashboard"))

        return render_template("admin_profile.html", admin=admin_data)
    except Exception as e:
        return render_template("error.html", error_message=str(e))


def get_admin_data():
    admin = get_record_by_id("users", "user_id", 2)
    if admin:
        # Fetch role name from user_roles table
        role = get_record_by_id("user_roles", "role_id", admin["role_id"])
        role_name = role["role_name"] if role else "Administrator"
        return {
            "user_id": admin["user_id"],
            "name": admin["name"],
            "email": admin["email"],
            "contact_number": admin["contact_number"],
            "password": admin["password"],  # Include password for validation
            "role": role_name,
            "profile_image": admin["profile_image"] or "https://i.pravatar.cc/150?img=3"  # Default image if none
        }
    else:
        # Fallback to default if no admin found
        return {
            "user_id": 1,
            "name": "Super Admin",
            "email": "admin@admin.com",
            "contact_number": "+1234567890",
            "password": "admin123",  # Include default password
            "role": "Administrator",
            "profile_image": "https://i.pravatar.cc/150?img=3"  # Default image
        }



@app.route("/country", methods=["GET", "POST"])
def country():
    try:
        if request.method == "POST":
            country_name = request.form["country_name"]
            add_record("countries", {"country_name": country_name})
            return redirect(url_for("country"))

        countries = get_all_records("countries")
        admin = get_admin_data()
        return render_template("country.html", countries=countries, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))

@app.route("/state", methods=["GET", "POST"])
def state():
    try:
        if request.method == "POST":
            country_id = request.form["country_id"]
            state_name = request.form["state_name"]
            add_record("states", {"country_id": country_id, "state_name": state_name})
            return redirect(url_for("state"))

        states = get_all_records("states")
        countries = get_all_records("countries")
        admin = get_admin_data()
        return render_template("state.html", states=states, countries=countries, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))

@app.route("/city", methods=["GET", "POST"])
def city():
    try:
        if request.method == "POST":
            country_id = request.form["country_id"]
            state_id = request.form["state_id"]
            city_name = request.form["city_name"]
            add_record("cities", {"country_id": country_id, "state_id": state_id, "city_name": city_name})
            return redirect(url_for("city"))

        cities = get_all_records("cities")
        countries = get_all_records("countries")
        states = get_all_records("states")
        admin = get_admin_data()
        return render_template("city.html", cities=cities, countries=countries, states=states, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))

@app.route("/user-role", methods=["GET", "POST"])
def user_role():
    try:
        if request.method == "POST":
            role_name = request.form["role_name"]
            description = request.form.get("description", "")
            add_record("user_roles", {"role_name": role_name, "description": description})
            return redirect(url_for("user_role"))

        roles = get_all_records("user_roles")
        admin = get_admin_data()
        return render_template("user_role.html", roles=roles, admin=admin)
    except Exception as e:
        return render_template("error.html", error_message=str(e))

import json
from flask import jsonify

@app.route("/debug-data")
def debug_data():
    try:
        users = get_all_records("users")
        restaurants = get_all_records("restaurants")
        notifications = get_all_records("notifications")
        subscription_plans = get_all_records("subscription_plans")
        subscription_history = get_all_records("subscription_history")
        countries = get_all_records("countries")
        states = get_all_records("states")
        cities = get_all_records("cities")
        user_roles = get_all_records("user_roles")

        # Convert ObjectId to string for JSON serialization
        def convert_ids(doc_list):
            for doc in doc_list:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            return doc_list

        data = {
            "users": convert_ids(users),
            "restaurants": convert_ids(restaurants),
            "notifications": convert_ids(notifications),
            "subscription_plans": convert_ids(subscription_plans),
            "subscription_history": convert_ids(subscription_history),
            "countries": convert_ids(countries),
            "states": convert_ids(states),
            "cities": convert_ids(cities),
            "user_roles": convert_ids(user_roles),
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# ===== RUN APP =====
if __name__ == "__main__":
    app.run(debug=True)
