import sqlite3
from datetime import datetime

DB_NAME = "restaurant_management.db"

# ==========================================================
#  DATABASE CONNECTION
# ==========================================================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================================
#  DATABASE INITIALIZATION
# ==========================================================
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # ---------- USER ROLES ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- USERS ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role_id INTEGER,
            contact_number TEXT,
            profile_image TEXT,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES user_roles(role_id)
        )
    """)

    # ---------- RESTAURANTS ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_name TEXT NOT NULL,
            owner_id INTEGER,
            email TEXT,
            contact_number TEXT,
            address TEXT,
            country_id INTEGER,
            state_id INTEGER,
            city_id INTEGER,
            status TEXT DEFAULT 'Active',
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(user_id)
        )
    """)

    # ---------- NOTIFICATIONS ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT,
            target_type TEXT CHECK(target_type IN ('User','Restaurant')) DEFAULT 'User',
            target_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Unread'
        )
    """)

    # ---------- SUBSCRIPTION PLANS ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscription_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT NOT NULL,
            description TEXT,
            duration_months INTEGER,
            price REAL NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- SUBSCRIPTION HISTORY ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscription_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            restaurant_id INTEGER,
            plan_id INTEGER,
            start_date DATE,
            end_date DATE,
            payment_status TEXT DEFAULT 'Paid',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
            FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id)
        )
    """)

    # ---------- COUNTRIES ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            country_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_name TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active'
        )
    """)

    # ---------- STATES ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS states (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            state_name TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (country_id) REFERENCES countries(country_id)
        )
    """)

    # ---------- CITIES ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            state_id INTEGER NOT NULL,
            city_name TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (country_id) REFERENCES countries(country_id),
            FOREIGN KEY (state_id) REFERENCES states(state_id)
        )
    """)

    # ---------- ADMIN ACTIVITY LOG ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action TEXT,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users(user_id)
        )
    """)

    # ---------- INSERT SAMPLE DATA ----------
    # User Roles
    cur.execute("INSERT OR IGNORE INTO user_roles (role_name, description) VALUES ('Admin', 'Administrator role')")
    cur.execute("INSERT OR IGNORE INTO user_roles (role_name, description) VALUES ('Owner', 'Restaurant Owner role')")

    # Countries
    cur.execute("INSERT OR IGNORE INTO countries (country_name) VALUES ('India')")
    cur.execute("INSERT OR IGNORE INTO countries (country_name) VALUES ('USA')")

    # States
    cur.execute("INSERT OR IGNORE INTO states (country_id, state_name) VALUES (1, 'Maharashtra')")
    cur.execute("INSERT OR IGNORE INTO states (country_id, state_name) VALUES (1, 'Delhi')")
    cur.execute("INSERT OR IGNORE INTO states (country_id, state_name) VALUES (2, 'California')")

    # Cities
    cur.execute("INSERT OR IGNORE INTO cities (country_id, state_id, city_name) VALUES (1, 1, 'Mumbai')")
    cur.execute("INSERT OR IGNORE INTO cities (country_id, state_id, city_name) VALUES (1, 1, 'Pune')")
    cur.execute("INSERT OR IGNORE INTO cities (country_id, state_id, city_name) VALUES (1, 2, 'New Delhi')")
    cur.execute("INSERT OR IGNORE INTO cities (country_id, state_id, city_name) VALUES (2, 3, 'Los Angeles')")

    # Sample Users
    cur.execute("INSERT OR IGNORE INTO users (name, email, password, role_id, contact_number) VALUES ('Super Admin', 'admin@admin.com', 'admin123', 1, '+1234567890')")
    cur.execute("INSERT OR IGNORE INTO users (name, email, password, role_id, contact_number) VALUES ('Raj Malhotra', 'raj@example.com', 'password', 2, '+0987654321')")
    cur.execute("INSERT OR IGNORE INTO users (name, email, password, role_id, contact_number) VALUES ('Ritika Sharma', 'ritika@example.com', 'password', 2, '+1122334455')")
    cur.execute("INSERT OR IGNORE INTO users (name, email, password, role_id, contact_number) VALUES ('Vikram Patel', 'vikram@example.com', 'password', 2, '+2233445566')")

    # Sample Restaurants
    cur.execute("INSERT OR IGNORE INTO restaurants (restaurant_name, owner_id, email, contact_number, address, country_id, state_id, city_id) VALUES ('Truffle Downtown', 2, 'truffle@restaurant.com', '+1122334455', '123 Main St, Bangalore', 1, 1, 1)")
    cur.execute("INSERT OR IGNORE INTO restaurants (restaurant_name, owner_id, email, contact_number, address, country_id, state_id, city_id) VALUES ('Spice Villa', 3, 'spice@restaurant.com', '+2233445566', '456 Elm St, Delhi', 1, 2, 3)")
    cur.execute("INSERT OR IGNORE INTO restaurants (restaurant_name, owner_id, email, contact_number, address, country_id, state_id, city_id) VALUES ('Green Bowl', 4, 'green@restaurant.com', '+3344556677', '789 Oak St, Mumbai', 1, 1, 1)")

    conn.commit()
    conn.close()
    print("✅ Database and tables created successfully!")


# ==========================================================
#  GENERIC CRUD OPERATIONS
# ==========================================================
def add_record(table, data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cur.execute(query, tuple(data.values()))
    conn.commit()
    conn.close()
    print(f"✅ Record added to {table} successfully!")


def get_all_records(table):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_record_by_id(table, id_field, record_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {id_field} = ?", (record_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_record(table, id_field, record_id, data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = list(data.values()) + [record_id]
    query = f"UPDATE {table} SET {set_clause} WHERE {id_field} = ?"
    cur.execute(query, tuple(values))
    conn.commit()
    conn.close()
    print(f"✅ Record in {table} updated successfully!")


def delete_record(table, id_field, record_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {id_field} = ?", (record_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Record deleted from {table}!")


def toggle_status(table, id_field, record_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT status FROM {table} WHERE {id_field} = ?", (record_id,))
    row = cur.fetchone()
    if row:
        new_status = 'Inactive' if row['status'] == 'Active' else 'Active'
        cur.execute(f"UPDATE {table} SET status = ? WHERE {id_field} = ?", (new_status, record_id))
        conn.commit()
        print(f"🔁 {table} record {record_id} status toggled to {new_status}")
    conn.close()


# ==========================================================
#  MODULE SPECIFIC FUNCTIONS (Examples)
# ==========================================================
def create_user(name, email, password, role_id, contact_number):
    add_record("users", {
        "name": name,
        "email": email,
        "password": password,
        "role_id": role_id,
        "contact_number": contact_number
    })

def create_country(name):
    add_record("countries", {"country_name": name})

def create_state(country_id, state_name):
    add_record("states", {"country_id": country_id, "state_name": state_name})

def create_city(country_id, state_id, city_name):
    add_record("cities", {"country_id": country_id, "state_id": state_id, "city_name": city_name})

def create_restaurant(restaurant_name, owner_id, email, contact_number, address, country_id, state_id, city_id):
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

# ==========================================================
#  MAIN EXECUTION
# ==========================================================
if __name__ == "__main__":
    init_db()
