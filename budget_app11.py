import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import filedialog
import pdfplumber
import re
import calendar
import seaborn as sns
import numpy as np
import yfinance as yf
import sqlite3
import json
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os
from customtkinter import *
import threading
import time

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the database path
db_path = os.path.join(script_dir, 'user_sessions.db')

# Initialize the main window with ttkbootstrap style
root = ttkb.Window(themename="cosmo")
root.title("Personal Finance Manager")
root.geometry("1200x800")

# Function to save data and end session
def save_and_end_session(): 
    save_data()  # Ensure data is saved
    messagebox.showinfo("Session Saved", "Your session has been saved.")
    root.destroy()  # Close the application

# Create a frame to hold the notebook and the button
top_frame = ttk.Frame(root)
top_frame.pack(fill='x')

# Create the notebook (tabbed interface)
notebook = ttk.Notebook(top_frame)
notebook.grid(row=0, column=0, sticky='w')

# Add the "Save and End Session" button to the same row as the notebook tabs
end_session_button = ttkb.Button(top_frame, text="Save and End Session", bootstyle="danger", command=save_and_end_session)
end_session_button.grid(row=0, column=1, sticky='e', padx=10, pady=10)

# Ensure the notebook expands to fill available space
top_frame.grid_columnconfigure(0, weight=1)

current_user_id = None

# Initialize DataFrames globally to store data
expense_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
income_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

# Database functions
def create_database():
    print(f"Creating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database created successfully.")

def user_exists(user_id):
    print(f"Checking if user_id exists: {user_id}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM sessions WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    print(f"User exists: {exists}")
    return exists

def save_session(user_id, data):
    print(f"Saving session for user_id: {user_id}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO sessions (user_id, data) VALUES (?, ?)', (user_id, data))
    conn.commit()
    conn.close()
    print("Session saved successfully.")

def load_last_session(user_id):
    print(f"Loading session for user_id: {user_id}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM sessions WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    print(f"Loaded data: {row}")
    return row[0] if row else None

def continue_session_popup():
    popup = tk.Toplevel(root)
    popup.title("Continue Session")
    popup.geometry("300x200")

    label = tk.Label(popup, text="Enter User ID:", font=("Arial", 14))
    label.pack(pady=10)

    continue_user_id_entry = tk.Entry(popup, font=("Arial", 14))
    continue_user_id_entry.pack(pady=10)

    def load_continue_session():
        global current_user_id
        user_id = continue_user_id_entry.get().strip()
        if not user_id:
            messagebox.showerror("Error", "User ID cannot be empty.")
            return
        if not user_exists(user_id):
            messagebox.showerror("Error", "User ID does not exist.")
            return
        current_user_id = user_id
        last_session = load_last_session(user_id)
        print(f"Session data to load: {last_session}")
        if last_session:
            session_data = json.loads(last_session)
            load_data(session_data)
            messagebox.showinfo("Continue Session", f"Previous session for User ID: {user_id} loaded successfully.")
            popup.destroy()
            show_main_app()
        else:
            messagebox.showinfo("Continue Session", f"No previous session found for User ID: {user_id}.")
            popup.destroy()

    continue_button = ttkb.Button(popup, text="Continue", command=load_continue_session, bootstyle="primary")
    continue_button.pack(pady=20)

def new_session_popup():
    popup = tk.Toplevel(root)
    popup.title("Create New User ID")
    popup.geometry("300x200")

    label = tk.Label(popup, text="Enter New User ID:", font=("Arial", 14))
    label.pack(pady=10)

    new_user_id_entry = tk.Entry(popup, font=("Arial", 14))
    new_user_id_entry.pack(pady=10)

    def create_new_user():
        global current_user_id
        new_user_id = new_user_id_entry.get().strip()
        if not new_user_id:
            messagebox.showerror("Error", "User ID cannot be empty.")
            return
        if user_exists(new_user_id):
            messagebox.showerror("Error", "User ID already exists. Please choose a different ID.")
            return
        current_user_id = new_user_id
        save_session(new_user_id, json.dumps({'expenses': [], 'income': []}))
        popup.destroy()
        messagebox.showinfo("New Session", f"Starting a new session for User ID: {new_user_id}")
        show_main_app()

    create_button = ttkb.Button(popup, text="Create", command=create_new_user, bootstyle="success")
    create_button.pack(pady=20)

def on_continue():
    continue_session_popup()

def show_main_app():
    welcome_frame.destroy()
    notebook.pack(expand=1, fill='both')

def load_data(data):
    global expense_df, income_df
    print(f"Loading data into DataFrames: {data}")
    
    # Ensure the expense DataFrame has the correct structure
    expense_df = pd.DataFrame(data.get('expenses', []))
    if not expense_df.empty:
        expense_df['Date'] = pd.to_datetime(expense_df['Date'], errors='coerce')
    else:
        expense_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
    
    # Ensure the income DataFrame has the correct structure
    income_df = pd.DataFrame(data.get('income', []))
    if not income_df.empty:
        income_df['Date'] = pd.to_datetime(income_df['Date'], errors='coerce')
    else:
        income_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
    
    print(f"Expense DataFrame: {expense_df}")
    print(f"Income DataFrame: {income_df}")
    refresh_expense_treeview()

def save_data():
    data = {
        'expenses': expense_df.assign(Date=expense_df['Date'].astype(str)).to_dict(orient='records'),
        'income': income_df.assign(Date=income_df['Date'].astype(str)).to_dict(orient='records'),
    }
    print(f"Data to save: {data}")
    save_session(current_user_id, json.dumps(data))

# Create the welcome screen
create_database()

welcome_frame = tk.Frame(root)
welcome_frame.pack(expand=True, fill='both')

welcome_label = tk.Label(welcome_frame, text="Welcome to AICH", font=("Arial", 24))
welcome_label.pack(pady=20)

button_frame = tk.Frame(welcome_frame)
button_frame.pack(pady=20)

continue_button = ttkb.Button(button_frame, text="Continue Session", command=on_continue, bootstyle="primary")
continue_button.pack(side='left', padx=20)

new_button = ttkb.Button(button_frame, text="New Session", command=new_session_popup, bootstyle="success")
new_button.pack(side='right', padx=20)

# Create the notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack_forget()  # Initially hide the notebook

# Create main tabs
expense_tab = ttk.Frame(notebook)
income_tab = ttk.Frame(notebook)
asset_allocation_tab = ttk.Frame(notebook)
financial_plan_tab = ttk.Frame(notebook)
savings_tab = ttk.Frame(notebook)

notebook.add(expense_tab, text="Expenses")
notebook.add(income_tab, text="Income")
notebook.add(asset_allocation_tab, text="Asset Allocation")
notebook.add(financial_plan_tab, text="Financial Planning")
notebook.add(savings_tab, text="Savings Suggestions")

# Create a secondary notebook within the Expenses tab
expense_notebook = ttk.Notebook(expense_tab)
expense_notebook.pack(expand=1, fill='both')

# Create the sub-tabs within the expense notebook
manage_expenses_tab = ttk.Frame(expense_notebook)
expense_tracking_tab = ttk.Frame(expense_notebook)

expense_notebook.add(manage_expenses_tab, text="Manage Expenses")
expense_notebook.add(expense_tracking_tab, text="Expense Tracking")

# Add sub-tabs within the Financial Planning tab
financial_plan_notebook = ttk.Notebook(financial_plan_tab)
financial_plan_notebook.pack(expand=1, fill='both')

analytics_tab = ttk.Frame(financial_plan_notebook)
investments_tab = ttk.Frame(financial_plan_notebook)
calendar_tab = ttk.Frame(financial_plan_notebook)

financial_plan_notebook.add(analytics_tab, text="Analytics")
financial_plan_notebook.add(investments_tab, text="Investments")
financial_plan_notebook.add(calendar_tab, text="Calendar")

# Center the tabs within the financial_plan_notebook
for tab in [analytics_tab, investments_tab, calendar_tab]:
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)

class CustomCalendar(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.cal = calendar.TextCalendar(calendar.SUNDAY)
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.payments = {}
        self.init_db()
        self.load_payments()
        self.build_calendar()

    def init_db(self):
        # Initialize the database connection and create table if it doesn't exist
        self.conn = sqlite3.connect('payments.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                description TEXT,
                amount REAL
            )
        ''')
        self.conn.commit()

    def load_payments(self):
        # Load payments from the database
        self.cursor.execute('SELECT year, month, day, description, amount FROM payments')
        rows = self.cursor.fetchall()
        for row in rows:
            year, month, day, description, amount = row
            if (year, month, day) not in self.payments:
                self.payments[(year, month, day)] = []
            self.payments[(year, month, day)].append({"description": description, "amount": amount})

    def build_calendar(self):
        # Build the calendar (same as before)
        for widget in self.winfo_children():
            widget.destroy()
        header = ttk.Frame(self)
        header.pack(fill='x')

        prev_btn = ttk.Button(header, text="<", command=self.prev_month)
        prev_btn.pack(side='left')
        next_btn = ttk.Button(header, text=">", command=self.next_month)
        next_btn.pack(side='right')

        month_year_lbl = ttk.Label(header, text=f"{calendar.month_name[self.month]} {self.year}", font=("Arial", 24))
        month_year_lbl.pack(side='top')

        cal_frame = ttk.Frame(self)
        cal_frame.pack(fill='both', expand=True)

        # Configure column and row weights for expansion
        for i in range(7):
            cal_frame.columnconfigure(i, weight=1)
        for i in range(6):  # Maximum 6 rows in a month view
            cal_frame.rowconfigure(i, weight=1)

        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for day in days:
            ttk.Label(cal_frame, text=day, font=("Arial", 24)).grid(row=0, column=days.index(day), sticky="nsew")

        month_days = self.cal.monthdayscalendar(self.year, self.month)
        for row, week in enumerate(month_days, 1):
            for col, day in enumerate(week):
                if day != 0:
                    day_frame = ttk.Frame(cal_frame, width=100, height=600, relief="ridge", borderwidth=1)
                    day_frame.grid_propagate(False)
                    day_frame.grid(row=row, column=col, sticky="nsew")
                    day_lbl = ttk.Label(day_frame, text=str(day), font=("Arial", 24))
                    day_lbl.pack(anchor='n', expand=True)
                    if (self.year, self.month, day) in self.payments:
                        payments = self.payments[(self.year, self.month, day)]
                        for payment in payments:
                            self.create_bubble(day_frame, payment['description'], payment['amount'])

    def create_bubble(self, parent, description, amount):
        canvas = tk.Canvas(parent, width=100, height=50)
        canvas.pack(anchor='center')
        canvas.create_oval(10, 10, 90, 40, fill='lightblue')
        canvas.create_text(50, 25, text=f"{description}\n${amount}", font=("Arial", 12), fill='blue')

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.build_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.build_calendar()

    def add_payment(self, day, description, amount):
        if (self.year, self.month, day) not in self.payments:
            self.payments[(self.year, self.month, day)] = []
        self.payments[(self.year, self.month, day)].append({"description": description, "amount": amount})
        self.save_payment_to_db(self.year, self.month, day, description, amount)
        self.build_calendar()

    def save_payment_to_db(self, year, month, day, description, amount):
        self.cursor.execute('''
            INSERT INTO payments (year, month, day, description, amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (year, month, day, description, amount))
        self.conn.commit()

def add_payment_popup(calendar_widget):
    popup = tk.Toplevel(root)
    popup.title("Add Payment")
    popup.geometry("400x300")

    ttk.Label(popup, text="Date (MM/DD/YYYY):").pack(pady=5)
    date_entry = ttk.Entry(popup)
    date_entry.pack(pady=5)

    ttk.Label(popup, text="Description:").pack(pady=5)
    desc_entry = ttk.Entry(popup)
    desc_entry.pack(pady=5)

    ttk.Label(popup, text="Amount:").pack(pady=5)
    amount_entry = ttk.Entry(popup)
    amount_entry.pack(pady=5)

    error_lbl = ttk.Label(popup, text="", foreground="red")
    error_lbl.pack(pady=5)

    def save_payment():
        try:
            date_str = date_entry.get()
            date = datetime.strptime(date_str, "%m/%d/%Y")
            day = date.day
            description = desc_entry.get()
            amount = float(amount_entry.get())

            calendar_widget.add_payment(day, description, amount)
            popup.destroy()
        except ValueError as e:
            error_lbl.config(text=f"Error: {e}")

    ttk.Button(popup, text="Add Payment", command=save_payment).pack(pady=20)

# Add the calendar widget to the calendar tab
calendar_widget = CustomCalendar(calendar_tab)
calendar_widget.pack(expand=1, fill='both')

ttk.Button(calendar_tab, text="Add Payment", command=lambda: add_payment_popup(calendar_widget)).pack(pady=10)

# Keywords for categorizing expenses
keywords = {
    "Dining Out": [
        "restaurant", "cafe", "bistro", "diner", "eatery", "bar", "grill", "deli", "pizza", "sushi", "burger", "taco", "steakhouse", "pub",
        "brunch", "dinner", "lunch", "breakfast", "buffet", "food truck", "takeout", "delivery", "fast food", "catering", "meal", "subway",
        "chipotle", "doordash", "grubhub", "ubereats", "wendy's", "mcdonald's", "kfc", "burger king", "taco bell", "panda express", "Red Lion",
        "Five guys", "Famiglia", "Strokos", "Gourmet", "Just Salad", "Dig Inn", "Raising Canes", "Carmines", "Happy Hot Hunan"
    ],
    "Groceries": [
        "supermarket", "grocery", "market", "store", "bakery", "butcher", "farmers market", "produce", "vegetables", "fruits", "meat", "fish",
        "seafood", "dairy", "organic", "whole foods", "costco", "walmart", "trader joe's", "aldi", "safeway", "kroger", "publix", "target",
        "food", "beverage", "milk", "bread", "eggs", "cereal", "snacks", "drinks"
    ],
    "Transportation": [
        "uber", "lyft", "taxi", "bus", "metro", "subway", "train", "tram", "ferry", "flight", "airline", "airport", "gas", "fuel", "petrol",
        "diesel", "electric vehicle", "toll", "parking", "car rental", "auto", "vehicle", "maintenance", "repair", "oil change", "tires",
        "brake", "car wash", "registration", "license", "insurance"
    ],
    "Healthcare": [
        "hospital", "clinic", "doctor", "physician", "dentist", "orthodontist", "optometrist", "pharmacy", "medication", "drug", "prescription",
        "insurance", "copay", "therapy", "counseling", "mental health", "chiropractor", "urgent care", "emergency", "surgery", "lab test",
        "diagnostic", "nursing", "vaccination", "medical", "health", "wellness", "fitness"
    ],
    "Fitness": [
        "gym", "fitness", "workout", "exercise", "yoga", "pilates", "crossfit", "zumba", "spin class", "personal trainer", "membership",
        "health club", "sports", "athletic", "run", "jog", "swim", "bike", "hike", "climb", "martial arts", "boxing", "kickboxing", "gym pass",
        "planet fitness", "24 hour fitness", "la fitness", "equinox", "gold's gym"
    ],
    "Entertainment": [
        "movie", "cinema", "theater", "concert", "show", "event", "ticket", "festival", "amusement park", "theme park", "museum", "exhibit",
        "gallery", "club", "nightclub", "bar", "pub", "game", "sports", "match", "play", "opera", "ballet", "circus", "streaming", "netflix",
        "hulu", "spotify", "apple music", "amazon prime", "disney+", "concert", "broadway", "Regal", "AMC", "Ba", "Palace", "Carrol's Place",
        "The Box"
    ],
    "Utilities": [
        "electricity", "water", "gas", "sewer", "trash", "recycling", "internet", "cable", "satellite", "phone", "mobile", "cell", "bill",
        "payment", "utility", "power", "heat", "cooling", "wifi", "landline", "fiber", "telecom"
    ],
    "Subscriptions": [
        "subscription", "membership", "service", "streaming", "netflix", "hulu", "amazon prime", "disney+", "spotify", "apple music",
        "magazine", "newspaper", "gym", "club", "box", "kit", "meal plan", "software", "app", "siriusxm", "adobe", "microsoft office",
        "cloud storage", "new york times", "washington post", "subcripti"
    ],
    "Education": [
        "tuition", "school", "college", "university", "course", "class", "lesson", "workshop", "seminar", "textbook", "book", "lab fee",
        "application fee", "student loan", "scholarship", "grant", "degree", "diploma", "certificate", "training", "education", "online course",
        "edx", "coursera", "udemy", "khan academy", "tutor"
    ],
    "Travel": [
        "hotel", "motel", "inn", "bnb", "airbnb", "hostel", "resort", "vacation", "travel", "trip", "flight", "airline", "cruise", "tour",
        "rental car", "taxi", "ride share", "bus", "train", "subway", "metro", "public transport", "luggage", "passport", "visa", "booking",
        "reservation", "expedia", "booking.com", "tripadvisor", "trivago", "kayak", "Mta"
    ],
    "Shopping": [
        "store", "shop", "mall", "outlet", "boutique", "market", "bazaar", "online shopping", "e-commerce", "amazon", "ebay", "etsy", "walmart",
        "target", "costco", "retail", "sale", "discount", "deal", "clothing", "apparel", "fashion", "accessories", "jewelry", "shoes",
        "electronics", "appliances", "furniture", "home decor", "beauty", "cosmetics", "health", "wellness", "sports", "outdoor", "pet supplies",
        "toys", "games", "hobbies", "books", "music", "movies", "video games", "software", "ikea", "best buy", "home depot", "lowe's", "Amzn", "Marketplace",
        "Duane Reade", "CVS"
    ],
}

def categorize_expense(description):
    for category, kw_list in keywords.items():
        if any(keyword in description.lower() for keyword in kw_list):
            return category
    return "Miscellaneous"

# Define average limits for categories and suggestions
average_limits = {
    "Groceries": 200,
    "Dining Out": 50,
    "Coffee": 10,
    "Transportation": 100,
    "Clothing": 50,
    "Entertainment": 100,
    "Utilities": 150,
    "Subscriptions": 20,
    "Healthcare": 100,
    "Insurance": 100,
    "Personal Care": 50,
    "Education": 100,
    "Travel": 200,
    "Fitness": 25,
    "Gifts": 50,
    "Miscellaneous": 50,
    "Home Maintenance": 50,
    "Pet Care": 50,
    "Childcare": 150,
    "Hobbies": 50,
    "Tech Gadgets": 50,
    "Home Decor": 50,
    "Online Shopping": 50,
    "Vehicle Maintenance": 50,
    "Bank Fees": 10,
    "Debt Repayment": 100,
    "Investments": 100,
}

savings_suggestions = {
    "Groceries": "Consider shopping at discount grocery stores or buying generic brands. Use coupons and take advantage of sales.",
    "Dining Out": "Reduce the number of times you eat out each month. Cook at home and try meal prepping.",
    "Coffee": "Brew your own coffee at home instead of buying expensive coffee from cafes. Invest in a good coffee maker.",
    "Transportation": "Use public transportation, carpool, or bike to work instead of driving alone. Consider buying a fuel-efficient vehicle.",
    "Clothing": "Buy clothing during sales or from discount stores. Consider buying second-hand clothes from thrift stores.",
    "Entertainment": "Look for free or low-cost entertainment options, such as community events, outdoor activities, or library resources.",
    "Utilities": "Reduce energy consumption by turning off lights, using energy-efficient appliances, and adjusting your thermostat.",
    "Subscriptions": "Review your subscriptions and cancel any that you don't use regularly. Look for bundle deals or shared plans.",
    "Healthcare": "Shop around for the best prices on medications. Use generic drugs when possible and take advantage of preventive care.",
    "Insurance": "Compare insurance rates and switch providers if you can get a better deal. Bundle insurance policies to save money.",
    "Personal Care": "Cut back on salon visits and expensive beauty products. Look for DIY alternatives and home treatments.",
    "Education": "Take advantage of scholarships, grants, and free online courses. Buy used textbooks or rent them instead of buying new ones.",
    "Travel": "Travel during off-peak times to save on flights and accommodations. Use travel rewards programs and compare prices.",
    "Fitness": "Cancel your gym membership if you don't use it regularly. Look for free workout resources online or exercise outdoors.",
    "Gifts": "Set a budget for gifts and stick to it. Consider making homemade gifts or giving experiences instead of physical items.",
    "Miscellaneous": "Track all other expenses and find ways to cut costs. Avoid impulse purchases and create a savings plan.",
    "Home Maintenance": "Perform regular maintenance tasks yourself, such as cleaning gutters or painting. Shop around for the best prices on services.",
    "Pet Care": "Buy pet food in bulk and look for discounts on pet supplies. Consider pet insurance to cover unexpected veterinary expenses.",
    "Childcare": "Look for affordable childcare options, such as family members or cooperative childcare groups. Take advantage of employer childcare benefits.",
    "Hobbies": "Set a budget for hobbies and stick to it. Look for second-hand equipment or materials and free resources online.",
    "Tech Gadgets": "Wait for sales or buy refurbished gadgets instead of new ones. Sell or trade in old devices for a discount on new purchases.",
    "Home Decor": "DIY home decor projects using affordable materials. Shop at discount stores or thrift shops for decor items.",
    "Online Shopping": "Use price comparison tools and look for discount codes before making online purchases. Take advantage of free shipping offers.",
    "Vehicle Maintenance": "Perform routine maintenance tasks yourself, such as oil changes and tire rotations. Shop around for the best prices on services.",
    "Bank Fees": "Avoid unnecessary bank fees by maintaining minimum balances, using in-network ATMs, and choosing accounts with no monthly fees.",
    "Debt Repayment": "Prioritize paying off high-interest debt first. Consider debt consolidation to reduce interest rates and simplify payments.",
    "Investments": "Minimize investment fees by choosing low-cost index funds or ETFs. Avoid frequent trading to reduce transaction costs.",
}

# Initialize DataFrames to store expenses, income, and asset allocation
expense_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
income_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Recurring"])
distribution_df = pd.DataFrame(columns=["Paycheck", "Category", "Amount", "InterestRate"])

# Manage Expenses Tab
expense_columns = ("Date", "Description", "Category", "Amount")
expense_tree = ttk.Treeview(manage_expenses_tab, columns=expense_columns, show='headings')
expense_tree.heading("Date", text="Date")
expense_tree.heading("Description", text="Description")
expense_tree.heading("Category", text="Category")
expense_tree.heading("Amount", text="Amount")

for col in expense_columns:
    expense_tree.column(col, anchor='center')

expense_tree.pack(expand=1, fill='both')

expense_entry_frame = ttk.Frame(manage_expenses_tab)
expense_entry_frame.pack(fill='x', padx=10, pady=10)

expense_date_entry = ttk.Entry(expense_entry_frame)
expense_description_entry = ttk.Entry(expense_entry_frame)
expense_category_entry = ttk.Combobox(expense_entry_frame, values=list(average_limits.keys()))
expense_amount_entry = ttk.Entry(expense_entry_frame)

expense_date_entry.grid(row=0, column=1, padx=5, pady=5)
expense_description_entry.grid(row=1, column=1, padx=5, pady=5)
expense_category_entry.grid(row=2, column=1, padx=5, pady=5)
expense_amount_entry.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(expense_entry_frame, text="Date:").grid(row=0, column=0, sticky='e')
ttk.Label(expense_entry_frame, text="Description:").grid(row=1, column=0, sticky='e')
ttk.Label(expense_entry_frame, text="Category:").grid(row=2, column=0, sticky='e')
ttk.Label(expense_entry_frame, text="Amount:").grid(row=3, column=0, sticky='e')

def refresh_expense_treeview():
    print("Refreshing expense treeview...")
    for item in expense_tree.get_children():
        expense_tree.delete(item)
    for _, row in expense_df.iterrows():
        expense_tree.insert("", "end", values=(row["Date"], row["Description"], row["Category"], row["Amount"]))

def add_expense():
    global expense_df
    try:
        date_value = pd.to_datetime(expense_date_entry.get(), errors='coerce')
        if pd.isna(date_value):
            raise ValueError("Invalid date format")
        description_value = expense_description_entry.get()
        category_value = expense_category_entry.get()
        amount_value = float(expense_amount_entry.get())

        if category_value not in average_limits:
            category_value = "Other"

        new_expense = pd.DataFrame({
            "Date": [date_value],
            "Description": [description_value],
            "Category": [category_value],
            "Amount": [amount_value]
        })

        expense_df = pd.concat([expense_df, new_expense], ignore_index=True)
        refresh_expense_treeview()
        save_data()  # Ensure data is saved after adding an expense
        print("Expense added successfully")

        expense_date_entry.delete(0, tk.END)
        expense_description_entry.delete(0, tk.END)
        expense_category_entry.set("")
        expense_amount_entry.delete(0, tk.END)

        update_financial_statements()
        calculate_savings_suggestions()

    except ValueError as e:
        print(f"Error: {e}")

add_expense_button = ttk.Button(expense_entry_frame, text="Add Expense", bootstyle=SUCCESS, command=add_expense)
add_expense_button.grid(row=4, columnspan=2, pady=10)

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    pattern = r'(\d{2}/\d{2})\s([A-Z]+[\w*\s-]+)\s(\d+\.\d{2})'
    matches = re.findall(pattern, text)
    current_year = datetime.now().year
    return [(f"{date}/{current_year}", desc, amount) for date, desc, amount in matches]

# Function to import expenses from PDF
def import_expenses():
    global expense_df
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf_text = extract_text_from_pdf(file_path)
        
        # Assuming the PDF text is in a format where each expense is represented as a tuple
        # (date, description, amount)
        expenses = extract_text_from_pdf(file_path)
        
        for expense in expenses:
            date_value, description_value, amount_value = expense
            category_value = categorize_expense(description_value)
            
            # Append expense to the DataFrame
            new_expense = pd.DataFrame({
                "Date": [pd.to_datetime(date_value, errors='coerce')],
                "Description": [description_value],
                "Category": [category_value],
                "Amount": [float(amount_value)]
            })
            expense_df = pd.concat([expense_df, new_expense], ignore_index=True)
            
            # Insert expense into the expense_tree
            expense_tree.insert("", "end", values=(date_value, description_value, category_value, f'${amount_value}'))
        
        # Recalculate financial statements and savings suggestions after adding all expenses
        update_financial_statements()
        calculate_savings_suggestions()

# Function to export expenses to CSV
def export_expenses():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        expense_df.to_csv(file_path, index=False)

# Function to refresh the expense treeview
def refresh_expense_treeview():
    for item in expense_tree.get_children():
        expense_tree.delete(item)
    for _, row in expense_df.iterrows():
        expense_tree.insert("", "end", values=(row["Date"].strftime('%Y-%m-%d') if not pd.isna(row["Date"]) else "", row["Description"], row["Category"], row["Amount"]))

import_expenses_button = ttk.Button(manage_expenses_tab, text="Import Expenses", bootstyle=INFO, command=import_expenses)
import_expenses_button.pack(side="left", padx=10, pady=10)

export_expenses_button = ttk.Button(manage_expenses_tab, text="Export Expenses", bootstyle=INFO, command=export_expenses)
export_expenses_button.pack(side="left", padx=10, pady=10)

# Expense Tracking Tab
progress_bars = {}
current_month = datetime.now().month
current_year = datetime.now().year

def update_progress_bars():
    for category in average_limits.keys():
        total_spent = expense_df[(expense_df["Category"] == category) & (expense_df["Date"].dt.month == current_month) & (expense_df["Date"].dt.year == current_year)]["Amount"].sum()
        limit = average_limits[category]
        progress_bars[category]["value"] = (total_spent / limit) * 100
        progress_bars[category].label.config(text=f"{category}: ${total_spent:.2f} / ${limit:.2f}")

def create_progress_bar(category):
    frame = ttk.Frame(scrollable_frame)
    frame.pack(fill='x', padx=10, pady=5)
    
    label = ttk.Label(frame, text=f"{category}: $0.00 / ${average_limits[category]:.2f}")
    label.pack(side='left')
    
    progress = ttk.Progressbar(frame, orient='horizontal', length=1000, mode='determinate', style="TProgressbar")
    progress.pack(side='right', fill='x', expand=True)
    progress.label = label
    progress_bars[category] = progress
    
    frame.update()

# Custom progress bar style
style = ttkb.Style()
style.configure("TProgressbar", thickness=20)

# Make the expense tracking tab scrollable
canvas = tk.Canvas(expense_tracking_tab)
scrollbar = ttk.Scrollbar(expense_tracking_tab, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Add month selector
month_selector_frame = ttk.Frame(scrollable_frame)
month_selector_frame.pack(fill='x', padx=10, pady=5)

ttk.Label(month_selector_frame, text="Select Month:").pack(side='left')

month_selector = ttk.Combobox(month_selector_frame, values=[datetime(current_year, m, 1).strftime("%B %Y") for m in range(1, 13)])
month_selector.current(current_month - 1)
month_selector.pack(side='left')

def update_month():
    global current_month, current_year
    selected_date = datetime.strptime(month_selector.get(), "%B %Y")
    current_month = selected_date.month
    current_year = selected_date.year
    update_progress_bars()

month_selector.bind("<<ComboboxSelected>>", lambda event: update_month())

for category in average_limits.keys():
    create_progress_bar(category)

# Edit Budget Popup
def edit_budget_popup():
    popup = ttkb.Toplevel(root)
    popup.title("Edit Budget")
    popup.geometry("400x600")
    
    for category in average_limits.keys():
        frame = ttk.Frame(popup)
        frame.pack(fill='x', padx=10, pady=5)
        
        label = ttk.Label(frame, text=category)
        label.pack(side='left')
        
        entry = ttk.Entry(frame)
        entry.insert(0, average_limits[category])
        entry.pack(side='right')
        
        def save_new_limit(category=category, entry=entry):
            try:
                new_limit = float(entry.get())
                average_limits[category] = new_limit
                update_progress_bars()
                refresh_expense_treeview()
            except ValueError:
                pass
        
        save_button = ttk.Button(frame, text="Save", command=save_new_limit)
        save_button.pack(side='right', padx=5)

ttk.Button(scrollable_frame, text="Edit Budget", bootstyle=SUCCESS, command=edit_budget_popup).pack(pady=10)

# Function to update financial statements
def update_financial_statements():
    handle_recurring_income()
    update_progress_bars()

# Income Tab
income_columns = ("Date", "Description", "Category", "Amount", "Recurring")
income_tree = ttk.Treeview(income_tab, columns=income_columns, show='headings')
income_tree.heading("Date", text="Date")
income_tree.heading("Description", text="Description")
income_tree.heading("Category", text="Category")
income_tree.heading("Amount", text="Amount")
income_tree.heading("Recurring", text="Recurring")

for col in income_columns:
    income_tree.column(col, anchor='center')

income_tree.pack(expand=1, fill='both')

income_entry_frame = ttk.Frame(income_tab)
income_entry_frame.pack(fill='x', padx=10, pady=10)

income_date_entry = ttk.Entry(income_entry_frame)
income_description_entry = ttk.Entry(income_entry_frame)
income_category_entry = ttk.Combobox(income_entry_frame, values=["Salary", "Bonus", "Investment", "Other"])
income_amount_entry = ttk.Entry(income_entry_frame)
income_recurring_entry = ttk.Combobox(income_entry_frame, values=["None", "Weekly", "Bi-Weekly", "Monthly"])

income_date_entry.grid(row=0, column=1, padx=5, pady=5)
income_description_entry.grid(row=1, column=1, padx=5, pady=5)
income_category_entry.grid(row=2, column=1, padx=5, pady=5)
income_amount_entry.grid(row=3, column=1, padx=5, pady=5)
income_recurring_entry.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(income_entry_frame, text="Date:").grid(row=0, column=0, sticky='e')
ttk.Label(income_entry_frame, text="Description:").grid(row=1, column=0, sticky='e')
ttk.Label(income_entry_frame, text="Category:").grid(row=2, column=0, sticky='e')
ttk.Label(income_entry_frame, text="Amount:").grid(row=3, column=0, sticky='e')
ttk.Label(income_entry_frame, text="Recurring:").grid(row=4, column=0, sticky='e')

def add_income():
    global income_df
    try:
        date_value = pd.to_datetime(income_date_entry.get(), errors='coerce')
        if pd.isna(date_value):
            raise ValueError("Invalid date format")
        description_value = income_description_entry.get()
        category_value = income_category_entry.get()
        amount_value = float(income_amount_entry.get())
        recurring_value = income_recurring_entry.get()

        new_income = pd.DataFrame({
            "Date": [date_value],
            "Description": [description_value],
            "Category": [category_value],
            "Amount": [amount_value],
            "Recurring": [recurring_value]
        })

        income_df = pd.concat([income_df, new_income], ignore_index=True)
        # Ensure Date column is in datetime format
        income_df["Date"] = pd.to_datetime(income_df["Date"], errors='coerce')
        
        income_tree.insert("", "end", values=(date_value.strftime('%Y-%m-%d'), description_value, category_value, amount_value, recurring_value))

        income_date_entry.delete(0, tk.END)
        income_description_entry.delete(0, tk.END)
        income_category_entry.set("")
        income_amount_entry.delete(0, tk.END)
        income_recurring_entry.set("")

        # Recalculate financial statements each time income is added
        update_financial_statements()

    except ValueError as e:
        print(f"Error: {e}")

add_income_button = ttk.Button(income_entry_frame, text="Add Income", bootstyle=SUCCESS, command=add_income)
add_income_button.grid(row=5, columnspan=2, pady=10)

# Function to handle recurring income
def handle_recurring_income():
    global income_df
    current_date = datetime.now()
    new_entries = []

    for index, row in income_df.iterrows():
        if row['Recurring'] == "Weekly":
            next_date = row['Date'] + timedelta(weeks=1)
        elif row['Recurring'] == "Bi-Weekly":
            next_date = row['Date'] + timedelta(weeks=2)
        elif row['Recurring'] == "Monthly":
            next_date = row['Date'] + timedelta(days=30)
        else:
            next_date = None

        if next_date and next_date <= current_date:
            new_entries.append({
                "Date": next_date,
                "Description": row['Description'],
                "Category": row['Category'],
                "Amount": row['Amount'],
                "Recurring": row['Recurring']
            })

    if new_entries:
        new_income_df = pd.DataFrame(new_entries)
        income_df = pd.concat([income_df, new_income_df], ignore_index=True)
        update_financial_statements()

handle_recurring_income()

# Asset Allocation Tab
def show_distribution_popup():
    popup = ttkb.Toplevel(root)
    popup.title("Add Asset Allocation")
    popup.geometry("400x800")

    selected_paycheck = income_df["Description"].unique().tolist()
    current_balance_var = tk.StringVar(value="Current Balance: $0")

    def update_balance():
        paycheck = paycheck_dropdown.get()
        total_income = income_df[income_df["Description"] == paycheck]["Amount"].sum()
        total_expenses = sum(float(entry.get() or 0) for entry in expense_entries)
        investments = sum(float(entry.get() or 0) for entry in investment_entries)
        current_balance_var.set(f"Current Balance: ${total_income - total_expenses - investments:.2f}")

    ttk.Label(popup, text="Select Paycheck:").pack(pady=10)
    paycheck_dropdown = ttk.Combobox(popup, values=selected_paycheck)
    paycheck_dropdown.pack(pady=10)

    current_balance_label = ttk.Label(popup, textvariable=current_balance_var)
    current_balance_label.pack(pady=10)

    # Projected Expenses
    expense_frame = ttk.Frame(popup)
    expense_frame.pack(pady=10, padx=10, fill='both', expand=True)

    expense_canvas = tk.Canvas(expense_frame)
    expense_scrollbar = ttk.Scrollbar(expense_frame, orient="vertical", command=expense_canvas.yview)
    expense_scrollable_frame = ttk.Frame(expense_canvas)

    expense_scrollable_frame.bind(
        "<Configure>",
        lambda e: expense_canvas.configure(
            scrollregion=expense_canvas.bbox("all")
        )
    )

    expense_canvas.create_window((0, 0), window=expense_scrollable_frame, anchor="nw")
    expense_canvas.configure(yscrollcommand=expense_scrollbar.set)

    expense_canvas.pack(side="left", fill="both", expand=True)
    expense_scrollbar.pack(side="right", fill="y")

    ttk.Label(expense_scrollable_frame, text="Projected Expenses:").pack(pady=10)
    expense_categories = ["Rent", "Insurance", "Healthcare", "Food", "Utilities", "Other"]
    expense_entries = []
    for category in expense_categories:
        ttk.Label(expense_scrollable_frame, text=category).pack(pady=5)
        entry = ttk.Entry(expense_scrollable_frame)
        entry.pack(pady=5)
        entry.bind("<KeyRelease>", lambda event: update_balance())
        expense_entries.append(entry)

    # Asset Allocation
    distribution_frame = ttk.Frame(popup)
    distribution_frame.pack(fill='x', padx=10, pady=10)

    investment_categories = ["Savings", "Stocks", "Fixed-Income Stocks", "Bonds", "Retirement", "Checking", "Real Estate"]
    investment_entries = []
    interest_rate_entries = []

    for idx, category in enumerate(investment_categories):
        ttk.Label(distribution_frame, text=f"{category}:").grid(row=idx, column=0, padx=5, pady=5)
        entry = ttk.Entry(distribution_frame)
        entry.grid(row=idx, column=1, padx=5, pady=5)
        entry.bind("<KeyRelease>", lambda event: update_balance())
        investment_entries.append(entry)
        
        ttk.Label(distribution_frame, text="Interest Rate (%):").grid(row=idx, column=2, padx=5, pady=5)
        rate_entry = ttk.Entry(distribution_frame)
        rate_entry.grid(row=idx, column=3, padx=5, pady=5)
        interest_rate_entries.append(rate_entry)

    def save_distribution():
        global distribution_df
        try:
            # Save each distribution entry
            distributions = {category: entry.get() for category, entry in zip(investment_categories, investment_entries)}
            interest_rates = {category: rate_entry.get() for category, rate_entry in zip(investment_categories, interest_rate_entries)}

            for category, amount in distributions.items():
                if amount:
                    new_distribution = pd.DataFrame({
                        "Paycheck": [paycheck_dropdown.get()],
                        "Category": [category],
                        "Amount": [float(amount)],
                        "InterestRate": [float(interest_rates[category] or 0)]
                    })

                    distribution_df = pd.concat([distribution_df, new_distribution], ignore_index=True)
                    distribution_tree.insert("", "end", values=(paycheck_dropdown.get(), category, amount, interest_rates[category]))

            # Recalculate financial statements and update the predicted wealth graph
            update_financial_statements()

            popup.destroy()
        except ValueError as e:
            print(f"Error: {e}")

    save_button = ttk.Button(popup, text="Save Distribution", bootstyle=SUCCESS, command=save_distribution)
    save_button.pack(pady=20)

ttk.Button(asset_allocation_tab, text="Add Distribution", bootstyle=SUCCESS, command=show_distribution_popup).pack(pady=10)

distribution_tree = ttk.Treeview(asset_allocation_tab, columns=("Paycheck", "Category", "Amount", "InterestRate"), show='headings')
distribution_tree.heading("Paycheck", text="Paycheck")
distribution_tree.heading("Category", text="Category")
distribution_tree.heading("Amount", text="Amount")
distribution_tree.heading("InterestRate", text="Interest Rate (%)")

for col in ("Paycheck", "Category", "Amount", "InterestRate"):
    distribution_tree.column(col, anchor='center', width=150)

distribution_tree.pack(expand=1, fill='both', padx=10, pady=10)

# Function to export asset allocation to CSV
def export_income_distribution():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        distribution_df.to_csv(file_path, index=False)

export_distribution_button = ttk.Button(asset_allocation_tab, text="Export Distribution", bootstyle=INFO, command=export_income_distribution)
export_distribution_button.pack(side="left", padx=10, pady=10)


# Analytics Tab (centered and scrollable)
analytics_canvas = tk.Canvas(analytics_tab)
analytics_scrollbar = ttk.Scrollbar(analytics_tab, orient="vertical", command=analytics_canvas.yview)
scrollable_analytics_frame = ttk.Frame(analytics_canvas)

scrollable_analytics_frame.bind(
    "<Configure>",
    lambda e: analytics_canvas.configure(
        scrollregion=analytics_canvas.bbox("all")
    )
)

analytics_canvas.create_window((0, 0), window=scrollable_analytics_frame, anchor="nw")
analytics_canvas.configure(yscrollcommand=analytics_scrollbar.set)

analytics_canvas.pack(side="left", fill="both", expand=True)
analytics_scrollbar.pack(side="right", fill="y")

analytics_frame = ttk.Frame(scrollable_analytics_frame)
analytics_frame.pack(expand=1, fill='both', padx=10, pady=10)

# Add section title
ttk.Label(analytics_frame, text="Analytics", font=("Arial", 14, "bold")).pack(pady=10)

# Create frames for each financial statement and chart
top_frame = ttk.Frame(analytics_frame)
top_frame.pack(padx=10, pady=10, fill='x')

balance_sheet_container = ttk.Frame(top_frame)
balance_sheet_container.pack(side='left', padx=10, pady=10, fill='both', expand=True)
income_statement_container = ttk.Frame(top_frame)
income_statement_container.pack(side='left', padx=10, pady=10, fill='both', expand=True)

predicted_wealth_container = ttk.Frame(analytics_frame)
predicted_wealth_container.pack(padx=10, pady=10, fill='x')
expense_pie_chart_container = ttk.Frame(analytics_frame)
expense_pie_chart_container.pack(padx=10, pady=10, fill='x')
scatter_plot_container = ttk.Frame(analytics_frame)
scatter_plot_container.pack(padx=10, pady=10, fill='x')

# Function to update financial statements
def update_financial_statements():
    handle_recurring_income()
    # Clear existing widgets
    for widget in balance_sheet_container.winfo_children():
        widget.destroy()
    for widget in income_statement_container.winfo_children():
        widget.destroy()
    for widget in predicted_wealth_container.winfo_children():
        widget.destroy()
    for widget in expense_pie_chart_container.winfo_children():
        widget.destroy()
    for widget in scatter_plot_container.winfo_children():
        widget.destroy()

    # Ensure Date columns are in datetime format
    income_df["Date"] = pd.to_datetime(income_df["Date"], errors='coerce')
    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors='coerce')

    # Balance Sheet
    balance_sheet = pd.DataFrame(columns=["Assets", "Liabilities", "Equity"])
    assets = income_df["Amount"].sum()
    liabilities = expense_df["Amount"].sum()
    equity = assets - liabilities
    balance_sheet = pd.concat([balance_sheet, pd.DataFrame({"Assets": [assets], "Liabilities": [liabilities], "Equity": [equity]})], ignore_index=True)

    ttk.Label(balance_sheet_container, text="Balance Sheet", font=("Arial", 12, "bold")).pack(pady=5)
    balance_sheet_tree = ttk.Treeview(balance_sheet_container, columns=["Assets", "Liabilities", "Equity"], show='headings')
    for col in balance_sheet_tree["columns"]:
        balance_sheet_tree.heading(col, text=col)
        balance_sheet_tree.column(col, anchor='center', width=100)
    for _, row in balance_sheet.iterrows():
        balance_sheet_tree.insert("", "end", values=list(row))
    balance_sheet_tree.pack(expand=1, fill='both')

    # Monthly Income Statement
    income_statement = pd.DataFrame(columns=["Month", "Income", "Expenses", "Net Income"])
    current_date = datetime.now()
    for month in range(12):
        month_date = pd.Timestamp(current_date - timedelta(days=30 * month))
        month_str = month_date.strftime("%B %Y")
        monthly_income = income_df[income_df["Date"].dt.to_period('M') == month_date.to_period('M')]["Amount"].sum()
        monthly_expenses = expense_df[expense_df["Date"].dt.to_period('M') == month_date.to_period('M')]["Amount"].sum()
        net_income = monthly_income - monthly_expenses
        income_statement = pd.concat([income_statement, pd.DataFrame({"Month": [month_str], "Income": [monthly_income], "Expenses": [monthly_expenses], "Net Income": [net_income]})], ignore_index=True)

    ttk.Label(income_statement_container, text="Income Statement", font=("Arial", 12, "bold")).pack(pady=5)
    income_statement_tree = ttk.Treeview(income_statement_container, columns=["Month", "Income", "Expenses", "Net Income"], show='headings')
    for col in income_statement_tree["columns"]:
        income_statement_tree.heading(col, text=col)
        income_statement_tree.column(col, anchor='center', width=100)
    for _, row in income_statement.iterrows():
        income_statement_tree.insert("", "end", values=list(row))
    income_statement_tree.pack(expand=1, fill='both')

    # Predicted Wealth Line Graph
    def calculate_predicted_wealth():
        # Calculate total principal
        principal = sum(distribution_df["Amount"])
        predicted_wealth = [principal]
        months = [datetime.now().strftime("%B %Y")]

        # Calculate average monthly expenses
        average_monthly_expense = expense_df.resample('M', on='Date')["Amount"].sum().mean()

        # Calculate total recurring income per month
        recurring_salaries = income_df[income_df["Recurring"] != "None"]
        recurring_income = 0

        for _, row in recurring_salaries.iterrows():
            frequency = row["Recurring"]
            if frequency == "Weekly":
                recurring_income += row["Amount"] * 4
            elif frequency == "Bi-Weekly":
                recurring_income += row["Amount"] * 2
            elif frequency == "Monthly":
                recurring_income += row["Amount"]

        for month in range(1, 13):
            month_growth = 0
            for _, row in distribution_df.iterrows():
                rate = row['InterestRate'] / 100 if 'InterestRate' in row and not pd.isna(row['InterestRate']) else 0
                amount = row['Amount']
                growth = amount * (rate / 12)  # Monthly growth
                month_growth += growth
            principal += month_growth + recurring_income - average_monthly_expense
            months.append((datetime.now() + timedelta(days=30 * month)).strftime("%B %Y"))
            predicted_wealth.append(principal)
        
        return months, predicted_wealth

    months, predicted_wealth = calculate_predicted_wealth()
    ttk.Label(predicted_wealth_container, text="Predicted Wealth Over Next 12 Months", font=("Arial", 12, "bold")).pack(pady=5)
    fig, ax = plt.subplots(figsize=(6, 3))  # Adjusted size for better visibility
    ax.plot(months, predicted_wealth, label="Predicted Wealth", marker='o')
    for i, value in enumerate(predicted_wealth):
        ax.annotate(f"${value:.2f}", (months[i], predicted_wealth[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    ax.set_xlabel("Month-Year", fontsize=4)
    ax.set_ylabel("Value ($)", fontsize=6)
    ax.set_title("Predicted Wealth", fontsize=8)
    ax.legend(fontsize=6)  # Decreased legend font size
    fig.tight_layout()  # Adjust layout to prevent clipping
    ax.tick_params(axis='x', rotation=90, labelsize=4)  # Vertically aligned x-axis labels for better readability and smaller font size

    canvas = FigureCanvasTkAgg(fig, master=predicted_wealth_container)
    canvas.get_tk_widget().pack(expand=1, fill='both')
    canvas.draw()

    # Expense Pie Chart
    if not expense_df.empty:
        category_expense = expense_df.groupby("Category")["Amount"].sum()
        ttk.Label(expense_pie_chart_container, text="Expense Categories", font=("Arial", 12, "bold")).pack(pady=5)
        fig, ax = plt.subplots(figsize=(6, 3))  # Adjusted size for better visibility
        category_expense.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax)
        ax.set_ylabel("")
        fig.tight_layout()  # Adjust layout to prevent clipping

        canvas = FigureCanvasTkAgg(fig, master=expense_pie_chart_container)
        canvas.get_tk_widget().pack(expand=1, fill='both')
        canvas.draw()

    # Scatter Plot for Average Expenses per Category vs Upper Limit
    if not expense_df.empty:
        avg_expense = expense_df.groupby("Category")["Amount"].mean()
        categories = list(average_limits.keys())
        avg_values = [avg_expense.get(cat, 0) for cat in categories]
        upper_limits = [average_limits[cat] for cat in categories]

        ttk.Label(scatter_plot_container, text="Average Expenses vs Upper Limits", font=("Arial", 12, "bold")).pack(pady=5)
        fig, ax = plt.subplots(figsize=(6, 3))  # Adjusted size for better visibility
        ax.scatter(categories, avg_values, label='Average Spent')
        ax.scatter(categories, upper_limits, label='Upper Limit', color='r')
        ax.set_xlabel("Categories", fontsize=5)
        ax.set_ylabel("Amount ($)", fontsize=6)
        ax.set_title("Average Expenses vs Upper Limits", fontsize=8)
        ax.legend(fontsize=6)  # Decreased legend font size
        fig.tight_layout()  # Adjust layout to prevent clipping
        ax.tick_params(axis='x', rotation=90, labelsize=4)  # Vertically aligned x-axis labels for better readability and smaller font size

        canvas = FigureCanvasTkAgg(fig, master=scatter_plot_container)
        canvas.get_tk_widget().pack(expand=1, fill='both')
        canvas.draw()

# Call update_financial_statements initially to populate the analytics tab
update_financial_statements()

# Savings Tab Layout
ttk.Label(savings_tab, text="Savings Suggestions", font=("Arial", 14, "bold")).pack(pady=10)

# Treeview with a new 'Action' column
savings_tree = ttk.Treeview(savings_tab, columns=("Category", "Average Spent", "Suggestion", "Action"), show='headings')
savings_tree.heading("Category", text="Category")
savings_tree.heading("Average Spent", text="Average Spent")
savings_tree.heading("Suggestion", text="Suggestion")
savings_tree.heading("Action", text="Action")

for col in ("Category", "Average Spent", "Suggestion", "Action"):
    savings_tree.column(col, anchor='center', width=150)

savings_tree.pack(expand=1, fill='both', padx=10, pady=10)

# Potential savings label, initially hidden
potential_savings_label = ttk.Label(savings_tab, text="", font=("Arial", 12, "bold"))
potential_savings_label.pack(pady=10)

accepted_goals = []

def add_goal_from_suggestion(goal):
    goals_listbox.insert(tk.END, goal)

def accept_suggestion(item):
    values = savings_tree.item(item, "values")
    category, avg_spent, suggestion = values[:3]
    goal = f"Reduce spending in {category}: {suggestion}"
    add_goal_from_suggestion(goal)
    accepted_goals.append(category)
    savings_tree.delete(item)

def decline_suggestion(item):
    savings_tree.delete(item)

def create_action_buttons(item):
    action_frame = ttk.Frame(savings_tree)
    accept_button = ttk.Button(action_frame, text="Accept", command=lambda i=item: accept_suggestion(i))
    decline_button = ttk.Button(action_frame, text="Decline", command=lambda i=item: decline_suggestion(i))
    accept_button.pack(side="left", padx=5)
    decline_button.pack(side="left", padx=5)
    savings_tree.set(item, column="Action", value="")
    action_frame.update_idletasks()
    bbox = savings_tree.bbox(item, "Action")
    if bbox:
        action_frame.place(x=bbox[0], y=bbox[1], anchor="nw")

def calculate_savings_suggestions():
    # Clear existing suggestions
    for item in savings_tree.get_children():
        savings_tree.delete(item)

    total_savings = 0

    # Calculate average spending and provide suggestions
    for category, limit in average_limits.items():
        avg_spent = expense_df[expense_df["Category"].str.lower() == category.lower()]["Amount"].mean()
        if pd.notna(avg_spent) and avg_spent > limit:
            suggestion = savings_suggestions.get(category, "Consider ways to reduce spending in this category.")
            total_savings += (avg_spent - limit)

            item = savings_tree.insert("", "end", values=(category, f"${avg_spent:.2f}", suggestion, ""))

            # Create a frame to hold the buttons
            buttons_frame = ttk.Frame(savings_tab)
            accept_button = ttk.Button(buttons_frame, text="Accept", command=lambda i=item: accept_suggestion(i))
            decline_button = ttk.Button(buttons_frame, text="Decline", command=lambda i=item: decline_suggestion(i))
            accept_button.pack(side="left", padx=5)
            decline_button.pack(side="left", padx=5)

            savings_tree.update_idletasks()
            win = savings_tree.bbox(item, column="Action")
            if win:
                buttons_frame.place(x=win[0], y=win[1], anchor="nw")

    potential_savings_label.config(text=f"Potential Total Savings: ${total_savings:.2f}")

# Automatically calculate savings suggestions
calculate_savings_suggestions()

# Goals from savings
goals_frame = ttk.Frame(savings_tab)
goals_frame.pack(expand=1, fill='both', padx=10, pady=10)

ttk.Label(goals_frame, text="Goals Added from Savings", font=("Arial", 12, "bold")).pack(pady=10)

goals_listbox = tk.Listbox(goals_frame)
goals_listbox.pack(expand=1, fill='both')

# Function to add goals to the listbox
def add_goal(goal):
    goals_listbox.insert(tk.END, goal)

# Investment Tab
investment_summary_df = pd.DataFrame(columns=["Category", "Market Value", "Estimated Yield"])

def calculate_investment_summary(asset_df):
    total_investment = asset_df["Market Value"].sum()
    category_breakdown = asset_df.groupby('Category')['Market Value'].sum()
    category_percentage = (category_breakdown / total_investment) * 100
    return total_investment, category_breakdown, category_percentage

def create_investment_summary_ui(parent, asset_df):
    total_investment, category_breakdown, category_percentage = calculate_investment_summary(asset_df)
    
    ttk.Label(parent, text=f"Total Investment: ${total_investment:.2f}", font=("Arial", 14)).pack(pady=10)
    
    summary_frame = ttk.Frame(parent)
    summary_frame.pack(fill='both', expand=True)
    
    summary_columns = ("Category", "Market Value", "Percentage of Total")
    summary_tree = ttk.Treeview(summary_frame, columns=summary_columns, show='headings')
    
    for col in summary_columns:
        summary_tree.heading(col, text=col)
        summary_tree.column(col, anchor='center')
    
    for category, value in category_breakdown.items():
        percentage = category_percentage[category]
        summary_tree.insert("", "end", values=(category, f"${value:.2f}", f"{percentage:.2f}%"))
    
    summary_tree.pack(expand=1, fill='both')

investment_summary_df = pd.DataFrame()

def import_portfolio_pdf():
    global investment_summary_df
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    print(f"Selected file: {file_path}")  # Debug print

    if file_path:
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    print(f"Text on page {page.page_number}: {text}")  # Debug print
                    if text:
                        pattern = r'([\w\s]+)\s+([\w\d]+)\s+([\w\s]+)\s+([\d\.]+)\s+\$([\d,]+\.\d+)\s+\$([\d,]+\.\d+)\s+\$([\d,]+\.\d+)\s+(\d+\.\d+)%'
                        matches = re.findall(pattern, text)
                        print(f"Matches found on page {page.page_number}: {matches}")  # Debug print

                        if matches:
                            for match in matches:
                                name, ticker, account_type, quantity, price, market_value, est_div_yield, percent_total = match
                                market_value = float(market_value.replace(",", ""))
                                investment_summary_df = pd.concat([investment_summary_df, pd.DataFrame({
                                    "Name": [name],
                                    "Ticker": [ticker],
                                    "Account Type": [account_type],
                                    "Quantity": [float(quantity)],
                                    "Price": [float(price.replace(",", ""))],
                                    "Market Value": [market_value],
                                    "Est. Dividend Yield": [float(est_div_yield.replace(",", ""))],
                                    "% of Total Portfolio": [float(percent_total)]
                                })], ignore_index=True)
                        else:
                            print(f"No matches found on page: {page.page_number}")
                    else:
                        print(f"Could not extract text from page: {page.page_number}")
        except Exception as e:
            print(f"Error processing PDF: {e}")
        
        create_investment_summary_ui(investments_tab, investment_summary_df)
    else:
        print("No file selected")

def create_investment_summary_ui(parent, asset_df):
    parent.update_idletasks()

    # Clear existing widgets in the parent frame
    for widget in parent.winfo_children():
        widget.destroy()

    # Create a canvas for scrollable content
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create a frame for the overall summary
    summary_frame = ttk.Frame(scrollable_frame)
    summary_frame.pack(fill='x', expand=True, padx=10, pady=10)

    total_investment = asset_df["Market Value"].sum()
    unrealized_gains = asset_df["Market Value"].sum() - (asset_df["Quantity"] * asset_df["Price"]).sum()

    # Display overall summary
    summary_font = ("Arial", 12, "bold")
    ttk.Label(summary_frame, text="Investment Summary", font=summary_font).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

    details = f"""
    Total Holding Market Value: ${total_investment:.2f}
    Unrealized Gains/Losses: ${unrealized_gains:.2f}
    Average Yield: {asset_df['Est. Dividend Yield'].mean():.2f}%
    Portfolio Diversification Index: {calculate_diversification_index(asset_df):.2f}
    Risk-Adjusted Return: {calculate_risk_adjusted_return(asset_df):.2f}
    Beta: {calculate_beta(asset_df, fetch_historical_data(asset_df)):.2f}
    Standard Deviation: {calculate_portfolio_sd(fetch_historical_data(asset_df)):.2f}
    Sharpe Ratio: {calculate_sharpe_ratio(asset_df, fetch_historical_data(asset_df)):.2f}
    Alpha: {calculate_alpha(asset_df, fetch_historical_data(asset_df)):.2f}
    Investor Score: {calculate_investor_score(asset_df, calculate_beta(asset_df, fetch_historical_data(asset_df)), calculate_sharpe_ratio(asset_df, fetch_historical_data(asset_df)), calculate_alpha(asset_df, fetch_historical_data(asset_df)), calculate_diversification_index(asset_df), calculate_risk_adjusted_return(asset_df))}
    """
    ttk.Label(summary_frame, text=details, font=("Arial", 10)).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')

    # Suggestions based on analysis
    suggestions = generate_suggestions(calculate_investor_score(asset_df, calculate_beta(asset_df, fetch_historical_data(asset_df)), calculate_sharpe_ratio(asset_df, fetch_historical_data(asset_df)), calculate_alpha(asset_df, fetch_historical_data(asset_df)), calculate_diversification_index(asset_df), calculate_risk_adjusted_return(asset_df)))
    ttk.Label(summary_frame, text=f"Suggestions: {suggestions}", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='w')

    # Portfolio Table
    table_frame = ttk.Frame(scrollable_frame)
    table_frame.pack(fill='x', expand=True, padx=10, pady=10)

    columns = ["Ticker", "Account Type", "Quantity", "Price", "Market Value", "Est. Dividend Yield", "% of Total Portfolio"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    tree.pack(fill='both', expand=True)

    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, anchor='center', width=100)

    for idx, row in asset_df.iterrows():
        tree.insert('', 'end', values=(
            row["Ticker"],
            row["Account Type"],
            row["Quantity"],
            row["Price"],
            row["Market Value"],
            row["Est. Dividend Yield"],
            row["% of Total Portfolio"]
        ))

    # Charts
    plot_investment_summary(asset_df, fetch_historical_data(asset_df), scrollable_frame)

def fetch_historical_data(asset_df):
    historical_data = {}
    for ticker in asset_df['Ticker']:
        stock_data = yf.download(ticker, period="1y")
        historical_data[ticker] = stock_data['Adj Close']
    return pd.DataFrame(historical_data)

def calculate_diversification_index(asset_df):
    return 1 / (asset_df['Market Value'].std() / asset_df['Market Value'].mean())

def calculate_risk_adjusted_return(asset_df):
    average_return = asset_df['Est. Dividend Yield'].mean()
    risk = asset_df['Market Value'].std()
    return average_return / risk if risk != 0 else 0

def calculate_investor_score(asset_df, beta, sharpe_ratio, alpha, diversification_index, risk_adjusted_return):
    score = (
        (asset_df['Est. Dividend Yield'].mean() >= 2) +
        (beta <= 1.2) +
        (sharpe_ratio >= 1) +
        (alpha > 0) +
        (diversification_index >= 0.5) +
        (risk_adjusted_return >= 0.5)
    )
    if score >= 5:
        return "A"
    elif score >= 4:
        return "B"
    elif score >= 3:
        return "C"
    else:
        return "D"

def calculate_beta(asset_df, historical_data, market_ticker='^GSPC'):
    market_data = yf.download(market_ticker, period="1y")['Adj Close']
    market_returns = market_data.pct_change().dropna()

    # Align the dates of market returns and portfolio returns
    portfolio_returns = historical_data.pct_change(fill_method=None).dropna().mean(axis=1)
    aligned_portfolio_returns = portfolio_returns.reindex(market_returns.index).dropna()
    aligned_market_returns = market_returns.reindex(aligned_portfolio_returns.index)

    # Re-check the lengths to ensure they are the same
    if len(aligned_portfolio_returns) != len(aligned_market_returns):
        raise ValueError("The lengths of aligned portfolio returns and market returns do not match.")

    covariance = np.cov(aligned_portfolio_returns, aligned_market_returns)[0, 1]
    beta = covariance / aligned_market_returns.var()
    return beta

def calculate_portfolio_sd(historical_data):
    portfolio_returns = historical_data.pct_change(fill_method=None).dropna().mean(axis=1)
    return portfolio_returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(asset_df, historical_data, risk_free_rate=0.02):
    portfolio_returns = historical_data.pct_change(fill_method=None).dropna().mean(axis=1)
    average_return = portfolio_returns.mean() * 252
    portfolio_sd = portfolio_returns.std() * np.sqrt(252)
    return (average_return - risk_free_rate) / portfolio_sd

def calculate_alpha(asset_df, historical_data, benchmark_return=0.10, risk_free_rate=0.02, market_ticker='^GSPC'):
    market_data = yf.download(market_ticker, period="1y")['Adj Close']
    market_returns = market_data.pct_change(fill_method=None).dropna().mean() * 252
    portfolio_returns = historical_data.pct_change(fill_method=None).dropna().mean(axis=1)
    average_return = portfolio_returns.mean() * 252
    beta = calculate_beta(asset_df, historical_data)
    alpha = average_return - (risk_free_rate + beta * (market_returns - risk_free_rate))
    return alpha

def plot_investment_summary(asset_df, historical_data, parent):
    fig, axs = plt.subplots(3, 1, figsize=(8, 20))  # Adjust figure size and layout
    fig.subplots_adjust(hspace=0.5, wspace=0.5)

    # Pie Chart for Investment Breakdown
    category_breakdown = asset_df.groupby('Name')['Market Value'].sum()
    wedges, texts, autotexts = axs[0].pie(category_breakdown, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    axs[0].set_title('Investment Breakdown by Category', fontsize=10)  # Smaller title font size
    axs[0].legend(wedges, category_breakdown.index, title="Categories", loc="center left", bbox_to_anchor=(-0.6, 0.5), fontsize=8)  # Move legend more to the left

    # Bar Chart for Market Value by Asset
    sns.barplot(x='Market Value', y='Name', data=asset_df, ax=axs[1])
    axs[1].set_title('Market Value by Asset', fontsize=10)  # Smaller title font size
    axs[1].set_xlabel('Market Value ($)', fontsize=8)  # Smaller label font size
    axs[1].set_ylabel('Asset', fontsize=8)  # Smaller label font size
    axs[1].tick_params(axis='both', labelsize=6)  # Make all fonts smaller for the bar graph

    # Line Plot for Historical Performance of the Portfolio
    historical_data['Total Portfolio'] = historical_data.mean(axis=1)
    historical_data.plot(ax=axs[2])
    axs[2].set_title('Historical Performance of the Portfolio', fontsize=10)  # Smaller title font size
    axs[2].set_xlabel('Date', fontsize=8)  # Smaller label font size
    axs[2].set_ylabel('Price ($)', fontsize=8)  # Smaller label font size

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.draw()

def generate_suggestions(investor_score):
    suggestions = {
        "A": "Your portfolio is performing well. Consider maintaining your current strategy.",
        "B": "Your portfolio is doing well. Review areas for potential improvement, such as increasing diversification or evaluating high-risk assets.",
        "C": "There is room for improvement. Consider diversifying your investments, reducing high-risk assets, and focusing on stable returns.",
        "D": "Your portfolio may be underperforming. Evaluate your strategy and consider seeking professional advice. Focus on diversification and risk management."
    }
    return suggestions.get(investor_score, "No suggestions available.")

# Add the button to import PDF in the investments tab
ttk.Button(investments_tab, text="Import Portfolio PDF", command=import_portfolio_pdf).pack(pady=10)

root.mainloop()
