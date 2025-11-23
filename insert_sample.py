import sqlite3

conn = sqlite3.connect('restaurant_management.db')
cur = conn.cursor()

# Insert sample notification
cur.execute('INSERT INTO notifications (title, message, target_type, target_id, priority) VALUES (?, ?, ?, ?, ?)',
           ('Welcome', 'Welcome to our platform', 'User', 2, 'High'))

# Insert sample subscription history
cur.execute('INSERT INTO subscription_history (user_id, restaurant_id, plan_id, start_date, end_date, payment_amount, payment_method, auto_renew) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
           (2, 1, 1, '2025-11-16', '2025-12-16', 999.0, 'Credit Card', 1))

conn.commit()
conn.close()
print('Sample data inserted successfully')
