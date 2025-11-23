from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# MongoDB connection URI - Replace with your MongoDB URI
MONGO_URI = "mongodb+srv://Umang_pro:Umang%402001@cluster0.wgfiq3p.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client['restaurant_management']

# Collections
user_roles = db.user_roles
users = db.users
restaurants = db.restaurants
notifications = db.notifications
subscription_plans = db.subscription_plans
subscription_history = db.subscription_history
countries = db.countries
states = db.states
cities = db.cities
admin_activity_log = db.admin_activity_log

# Create indexes if needed
user_roles.create_index("role_name", unique=True)
users.create_index("email", unique=True)
countries.create_index("country_name", unique=True)

def init_db():
    # Clear existing collections (drops all data)
    user_roles.delete_many({})
    users.delete_many({})
    restaurants.delete_many({})
    notifications.delete_many({})
    subscription_plans.delete_many({})
    subscription_history.delete_many({})
    countries.delete_many({})
    states.delete_many({})
    cities.delete_many({})
    admin_activity_log.delete_many({})

    # Insert sample user roles
    user_roles.insert_many([
        {"role_name": "Admin", "description": "Administrator role", "status": "Active", "created_at": datetime.utcnow()},
        {"role_name": "Owner", "description": "Restaurant Owner role", "status": "Active", "created_at": datetime.utcnow()},
    ])

    # Insert sample countries
    countries.insert_many([
        {"country_name": "India", "status": "Active"},
        {"country_name": "USA", "status": "Active"},
    ])

    # Insert sample states
    states.insert_many([
        {"country_id": get_country_id("India"), "state_name": "Maharashtra", "status": "Active"},
        {"country_id": get_country_id("India"), "state_name": "Delhi", "status": "Active"},
        {"country_id": get_country_id("USA"), "state_name": "California", "status": "Active"},
    ])

    # Insert sample cities
    cities.insert_many([
        {"country_id": get_country_id("India"), "state_id": get_state_id("Maharashtra"), "city_name": "Mumbai", "status": "Active"},
        {"country_id": get_country_id("India"), "state_id": get_state_id("Maharashtra"), "city_name": "Pune", "status": "Active"},
        {"country_id": get_country_id("India"), "state_id": get_state_id("Delhi"), "city_name": "New Delhi", "status": "Active"},
        {"country_id": get_country_id("USA"), "state_id": get_state_id("California"), "city_name": "Los Angeles", "status": "Active"},
    ])

    # Insert sample users
    admin_role_id = get_role_id("Admin")
    owner_role_id = get_role_id("Owner")

    users.insert_many([
        {"name": "Super Admin", "email": "admin@admin.com", "password": "admin123", "role_id": admin_role_id, "contact_number": "+1234567890", "status": "Active", "created_at": datetime.utcnow()},
        {"name": "Raj Malhotra", "email": "raj@example.com", "password": "password", "role_id": owner_role_id, "contact_number": "+0987654321", "status": "Active", "created_at": datetime.utcnow()},
        {"name": "Ritika Sharma", "email": "ritika@example.com", "password": "password", "role_id": owner_role_id, "contact_number": "+1122334455", "status": "Active", "created_at": datetime.utcnow()},
        {"name": "Vikram Patel", "email": "vikram@example.com", "password": "password", "role_id": owner_role_id, "contact_number": "+2233445566", "status": "Active", "created_at": datetime.utcnow()},
    ])

    # Insert sample restaurants
    users_map = {user["name"]: user["_id"] for user in users.find({})}
    restaurants.insert_many([
        {"restaurant_name": "Truffle Downtown", "owner_id": users_map.get("Raj Malhotra"), "email": "truffle@restaurant.com", "contact_number": "+1122334455",
         "address": "123 Main St, Bangalore", "country_id": get_country_id("India"), "state_id": get_state_id("Maharashtra"), "city_id": get_city_id("Mumbai"), "status": "Active", "registered_at": datetime.utcnow()},
        {"restaurant_name": "Spice Villa", "owner_id": users_map.get("Ritika Sharma"), "email": "spice@restaurant.com", "contact_number": "+2233445566",
         "address": "456 Elm St, Delhi", "country_id": get_country_id("India"), "state_id": get_state_id("Delhi"), "city_id": get_city_id("New Delhi"), "status": "Active", "registered_at": datetime.utcnow()},
        {"restaurant_name": "Green Bowl", "owner_id": users_map.get("Vikram Patel"), "email": "green@restaurant.com", "contact_number": "+3344556677",
         "address": "789 Oak St, Mumbai", "country_id": get_country_id("India"), "state_id": get_state_id("Maharashtra"), "city_id": get_city_id("Mumbai"), "status": "Active", "registered_at": datetime.utcnow()},
    ])

    print("✅ MongoDB: Database initialized with collections and sample data")

def get_role_id(role_name):
    role = user_roles.find_one({"role_name": role_name})
    return role["_id"] if role else None

def get_country_id(country_name):
    country = countries.find_one({"country_name": country_name})
    return country["_id"] if country else None

def get_state_id(state_name):
    state = states.find_one({"state_name": state_name})
    return state["_id"] if state else None

def get_city_id(city_name):
    city = cities.find_one({"city_name": city_name})
    return city["_id"] if city else None

# Generic CRUD operations

def add_record(collection_name, data: dict):
    collection = db[collection_name]
    result = collection.insert_one(data)
    print(f"✅ Record added to {collection_name} with id {result.inserted_id}")
    return str(result.inserted_id)

def get_all_records(collection_name):
    collection = db[collection_name]
    return list(collection.find())

def get_record_by_id(collection_name, record_id):
    collection = db[collection_name]
    data = collection.find_one({"_id": ObjectId(record_id)})
    if data:
        data["_id"] = str(data["_id"])
    return data

def update_record(collection_name, record_id, data: dict):
    collection = db[collection_name]
    collection.update_one({"_id": ObjectId(record_id)}, {"$set": data})
    print(f"✅ Record in {collection_name} with id {record_id} updated")

def delete_record(collection_name, record_id):
    collection = db[collection_name]
    collection.delete_one({"_id": ObjectId(record_id)})
    print(f"🗑️ Record deleted from {collection_name} with id {record_id}")

def toggle_status(collection_name, record_id):
    collection = db[collection_name]
    doc = collection.find_one({"_id": ObjectId(record_id)})
    if doc and "status" in doc:
        new_status = "Inactive" if doc["status"] == "Active" else "Active"
        collection.update_one({"_id": ObjectId(record_id)}, {"$set": {"status": new_status}})
        print(f"🔁 {collection_name} record {record_id} status toggled to {new_status}")

if __name__ == "__main__":
    init_db()
