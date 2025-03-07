# Productivity Tracker

<p>A simple productivity tracker that monitors app usage and categorizes it as productive or unproductive. The app uses MySQL to store user data and tracks the applications that the user has interacted with, categorizing them as either productive or unproductive.
</p>
<p>Start improving your productivity today—because every minute counts!</p>

# Key Features

- Productivity Graphs: Visualize your daily and weekly productivity percentages through interactive, real-time graphs. Track your software usage patterns and see how much time you’re spending on the things that matter.
  
- Productive vs Unproductive Days: Our interactive calendar highlights productive and unproductive days, color-coded for easy reference. Stay motivated and aware of your progress by tracking trends over time.
  
- Real-time Data Insights: Understand how you use your computer by seeing the exact software you interact with, and get insights into which activities are boosting or hindering your productivity.
  
- Beautiful and Easy-to-Use Interface: The platform is designed to give you quick insights into your work habits with an easy-to-navigate interface. Analyze your work and make better decisions to optimize your time.

## Setup

### Prerequisites
- Python 3.x
- MySQL Server
- pip (Python Package Installer)

### Installation
1. Clone the repository:
    git clone https://github.com/Selvalakshmi23-JR/productivity-tracker.git
    cd productivity-tracker
    
2. Create a virtual environment:
    python3 -m venv venv

3. Install required packages:
    pip install -r requirements.txt

4. Set up the MySQL database:
    - Create a database daily_tracker in MySQL.
    - Create tables users, uasge_detail, dailyy_usage, and system_config.
      
5. Set the required environment variables:
    - DB_HOST: MySQL host 
    - DB_USER: MySQL username
    - DB_PASSWORD: MySQL password 
    - DB_NAME: MySQL database name
  
6. Run the application:
    python app.py

### Usage

- Navigate to http://localhost:5000/ in your web browser to access the app.
- Use the Sign Up and Login pages to create and authenticate a user.
- Use the Dashboard to view app usage statistics.
- View activity on the calendar for each day of the month.
