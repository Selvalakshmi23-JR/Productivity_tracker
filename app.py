from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import psutil
import time
import threading
from datetime import datetime, timedelta
import calendar
import pandas as pd
import matplotlib
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv

matplotlib.use('Agg') 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

load_dotenv()  
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

conn = mysql.connector.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)

if conn.is_connected():
    print("Successfully connected to MySQL database")
else:
    print("MySQL database connection failed")

def insert_usage_data(app_name, start_time, end_time, duration, category, user_id):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO uasge_detail(app_name, start_time, end_time, duration, category, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (app_name, start_time, end_time, duration, category, user_id))
    print("App usage data is inserted for user")
    conn.commit()
    cursor.close()

def track_usage(user_id):
    app_usage = {}
    app_category = {
        "Code.exe": "Productive",
        "chrome.exe": "Unproductive"
    }

    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            app_name = proc.info['name']
            category = app_category.get(app_name, "other")
            if app_name not in app_usage:
                app_usage[app_name] = {'start_time': time.time(), 'duration': 0, 'category': category}
            else:
                app_usage[app_name]['duration'] = time.time() - app_usage[app_name]['start_time']

        time.sleep(60)
        for app, data in app_usage.items():
            insert_usage_data(app, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['start_time'])),
                              time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), int(data['duration']), data['category'], user_id)


def get_usage_data(user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT category, SUM(duration) FROM uasge_detail WHERE user_id= %s AND category IN ("Productive", "Unproductive") GROUP BY category',(user_id,))
    category_data = cursor.fetchall()
    print("App usage data is fetched from database for user")
    if category_data:
        categories = [item[0] for item in category_data]
        values = [float(item[1]) for item in category_data]
        plt.figure(figsize=(6, 6), facecolor='black')
        label_colors = ['blue', 'yellow','purple']  
        wedges, texts, autotexts = plt.pie(values, labels=categories, autopct='%1.1f%%', startangle=140, colors=['blue', 'yellow'])
        for i, text in enumerate(texts):
            text.set_color(label_colors[i])
        plt.title("Category Distribution", color='purple')
        img_path = os.path.join('static', 'pie.png')
        plt.savefig(img_path)
        plt.close()
    cursor.close()
    gbar_chart(user_id)
    return category_data

def gbar_chart(user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT app_name, SUM(duration), category FROM uasge_detail WHERE user_id = %s AND category IN ("Productive","Unproductive") GROUP BY app_name', (user_id,))
    usage_data = cursor.fetchall()
    if usage_data:
        df = pd.DataFrame(usage_data, columns=['App_name', 'Usage', 'Category'])
        df['Color'] = df['Category'].apply(lambda x: 'green' if x == 'Productive' else 'red')
        plt.figure(figsize=(10, 6))  # Set figure size
        plt.bar(df['App_name'], df['Usage'], color=df['Color'])
        plt.title("App usage details", color="purple")
        plt.xlabel("App Name")
        plt.ylabel("Usage (seconds)")
        img_path = os.path.join('static', 'chart.png')
        plt.savefig(img_path)
        plt.close()

def insert_daily_data(user_id):
    today_date = datetime.now().date()
    yesterday_date = today_date - timedelta(days=1)
    raw_data = get_usage_data(session['user_id'])
    data = {}
    for category, time in raw_data:
        data[category] = time
    print(data)
    if data:
        total_time = data["Productive"] + data["Unproductive"]
        productive_time = (data["Productive"] / total_time) * 100
        print(productive_time)
        unproductive_time = (data["Unproductive"] / total_time) * 100
        res = "productive" if productive_time > unproductive_time else "unproductive"
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dailyy_usage(daily_date, result,user_id) VALUES(%s, %s,%s)", (yesterday_date, res,user_id,))
        print("Inserted daily data")
        conn.commit()
        cursor.close()

def clear_daily_data(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT last_cleanup FROM system_config WHERE user_id= %s ORDER BY id DESC LIMIT 1",(user_id,))
    result = cursor.fetchone()
    current_time = datetime.now()
    current_date = current_time.date()  
    if result is None:
        cursor.execute("INSERT INTO system_config (last_cleanup,user_id) VALUES (%s,%s)", (current_time,user_id,))
        conn.commit()
        return

    last_cleanup = result[0].date() 
    if last_cleanup < current_date:
        insert_daily_data(user_id)
        cursor.execute("DELETE FROM uasge_detail WHERE user_id= %s ",(user_id,)) 
        conn.commit()
        cursor.execute("INSERT INTO system_config (last_cleanup,user_id) VALUES (%s,%s)", (current_time,user_id,))
        conn.commit()
        print(f"Data cleared for previous day. New cleanup timestamp inserted at {current_time}")
    cursor.close()

def get_activity_data(year, month):
    user_id = session.get('user_id')
    cursor = conn.cursor()
    cursor.execute("SELECT daily_date, result FROM dailyy_usage WHERE MONTH(daily_date) = %s AND user_id= %s", (month,user_id,))  
    data = cursor.fetchall()
    activity_data = {}
    for date, category in data:
        activity_data[date.day] = category
    return activity_data



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cursor.close()
        flash("Signup successful! Please log in.")
        return redirect(url_for('login'))
    
    return render_template('sign.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        print("exe")
        if user and user[1] == password:  
            session['user_id'] = user[0]
            print("Login successful!")
            return redirect(url_for('dashboard')) 
        else:
            print("Invalid username or password")
            return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')

# User Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!")
    return redirect(url_for('index'))

# Protect routes
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        clear_daily_data(user_id)
        tracking_thread = threading.Thread(target=track_usage, args=(user_id,))
        tracking_thread.daemon = True
        tracking_thread.start()
        time.sleep(5)
        app_data = get_usage_data(user_id)
        return render_template('index.html', app_data=app_data)


@app.route('/calendar')
@login_required
def home():
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    month_name = today.strftime('%B %Y')
    first_day_of_month = datetime(current_year, current_month, 1).weekday()
    first_day_of_month = (first_day_of_month + 1) % 7
    num_days_in_month = calendar.monthrange(current_year, current_month)[1]

    activity_data = get_activity_data(current_year, current_month)
    days = ["" for _ in range(first_day_of_month)]
    days += list(range(1, num_days_in_month + 1)) 
    num_empty_cells = (7 - len(days) % 7) % 7
    days += ["" for _ in range(num_empty_cells)]

    return render_template('calendar.html', month_name=month_name, days=days, activity_data=activity_data)

@app.route('/')
def index():
    return render_template('home.html')

def run_flask():
    app.run(debug=True, port=5000, use_reloader=False)

if __name__ == "__main__":
    run_flask()



