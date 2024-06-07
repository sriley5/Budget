import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import filedialog
import pdfplumber
import re

# Initialize the main window with ttkbootstrap style
root = ttkb.Window(themename="cosmo")
root.title("Personal Finance Manager")
root.geometry("1200x800")

# Create the notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both')

# Create tabs
expense_tab = ttk.Frame(notebook)
income_tab = ttk.Frame(notebook)
income_distribution_tab = ttk.Frame(notebook)
financial_plan_tab = ttk.Frame(notebook)
savings_tab = ttk.Frame(notebook)

notebook.add(expense_tab, text="Expenses")
notebook.add(income_tab, text="Income")
notebook.add(income_distribution_tab, text="Income Distribution")
notebook.add(financial_plan_tab, text="Financial Planning")
notebook.add(savings_tab, text="Savings Suggestions")

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
    # Add more categories and keywords as needed
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
    # Add more limits as needed
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
    # Add more categories as needed
}

# Initialize DataFrames to store expenses, income, and income distribution
expense_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
income_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Recurring"])
distribution_df = pd.DataFrame(columns=["Paycheck", "Category", "Amount"])

# Expenses Tab
expense_columns = ("Date", "Description", "Category", "Amount")
expense_tree = ttk.Treeview(expense_tab, columns=expense_columns, show='headings')
expense_tree.heading("Date", text="Date")
expense_tree.heading("Description", text="Description")
expense_tree.heading("Category", text="Category")
expense_tree.heading("Amount", text="Amount")

for col in expense_columns:
    expense_tree.column(col, anchor='center')

expense_tree.pack(expand=1, fill='both')

expense_entry_frame = ttk.Frame(expense_tab)
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
        # Ensure Date column is in datetime format
        expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors='coerce')
        
        expense_tree.insert("", "end", values=(date_value.strftime('%Y-%m-%d'), description_value, category_value, amount_value))

        expense_date_entry.delete(0, tk.END)
        expense_description_entry.delete(0, tk.END)
        expense_category_entry.set("")
        expense_amount_entry.delete(0, expense_amount_entry.delete(0, tk.END))

        # Recalculate financial statements and savings suggestions each time an expense is added
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
    return matches

# Function to import expenses from CSV
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

import_expenses_button = ttk.Button(expense_tab, text="Import Expenses", bootstyle=INFO, command=import_expenses)
import_expenses_button.pack(side="left", padx=10, pady=10)

export_expenses_button = ttk.Button(expense_tab, text="Export Expenses", bootstyle=INFO, command=export_expenses)
export_expenses_button.pack(side="left", padx=10, pady=10)

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

# Income Distribution Tab
def show_distribution_popup():
    popup = ttkb.Toplevel(root)
    popup.title("Add Income Distribution")
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

    # Income Distribution
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

ttk.Button(income_distribution_tab, text="Add Distribution", bootstyle=SUCCESS, command=show_distribution_popup).pack(pady=10)

distribution_tree = ttk.Treeview(income_distribution_tab, columns=("Paycheck", "Category", "Amount", "InterestRate"), show='headings')
distribution_tree.heading("Paycheck", text="Paycheck")
distribution_tree.heading("Category", text="Category")
distribution_tree.heading("Amount", text="Amount")
distribution_tree.heading("InterestRate", text="Interest Rate (%)")

for col in ("Paycheck", "Category", "Amount", "InterestRate"):
    distribution_tree.column(col, anchor='center', width=150)

distribution_tree.pack(expand=1, fill='both', padx=10, pady=10)

# Function to export income distribution to CSV
def export_income_distribution():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        distribution_df.to_csv(file_path, index=False)

export_distribution_button = ttk.Button(income_distribution_tab, text="Export Distribution", bootstyle=INFO, command=export_income_distribution)
export_distribution_button.pack(side="left", padx=10, pady=10)

# Financial Planning Tab
financial_plan_canvas = tk.Canvas(financial_plan_tab)
financial_plan_scrollbar = ttk.Scrollbar(financial_plan_tab, orient="vertical", command=financial_plan_canvas.yview)
financial_plan_scrollable_frame = ttk.Frame(financial_plan_canvas)

financial_plan_scrollable_frame.bind(
    "<Configure>",
    lambda e: financial_plan_canvas.configure(
        scrollregion=financial_plan_canvas.bbox("all")
    )
)

financial_plan_canvas.create_window((0, 0), window=financial_plan_scrollable_frame, anchor="nw")
financial_plan_canvas.configure(yscrollcommand=financial_plan_scrollbar.set)

financial_plan_canvas.pack(side="left", fill="both", expand=True)
financial_plan_scrollbar.pack(side="right", fill="y")

financial_plan_frame = ttk.Frame(financial_plan_scrollable_frame)
financial_plan_frame.pack(expand=1, fill='both', padx=70, pady=10)  # Increased padx for more centering

# Add section title
ttk.Label(financial_plan_frame, text="Financial Planning", font=("Arial", 14, "bold")).pack(pady=10)

# Create a frame for the financial statements and pie chart
statements_frame = ttk.Frame(financial_plan_frame)
statements_frame.pack(expand=1, fill='both', padx=10, pady=10)

# Create frames for each financial statement and chart
balance_sheet_container = ttk.Frame(statements_frame)
balance_sheet_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
income_statement_container = ttk.Frame(statements_frame)
income_statement_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
predicted_wealth_container = ttk.Frame(statements_frame)
predicted_wealth_container.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
expense_pie_chart_container = ttk.Frame(statements_frame)
expense_pie_chart_container.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
scatter_plot_container = ttk.Frame(statements_frame)
scatter_plot_container.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Goals section to the right
goals_frame = ttk.Frame(statements_frame)
goals_frame.grid(row=0, column=2, rowspan=4, padx=10, pady=10, sticky="nsew")

# Make the columns and rows expand proportionally
statements_frame.columnconfigure(0, weight=1)
statements_frame.columnconfigure(1, weight=1)
statements_frame.columnconfigure(2, weight=1)
statements_frame.rowconfigure(0, weight=1)
statements_frame.rowconfigure(1, weight=1)
statements_frame.rowconfigure(2, weight=1)
statements_frame.rowconfigure(3, weight=1)

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


# Call update_financial_statements initially to populate the financial planning tab
update_financial_statements()

# Ensure expenses without a year are assumed to belong to the current year
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    pattern = r'(\d{2}/\d{2})\s([A-Z]+[\w*\s-]+)\s(\d+\.\d{2})'
    matches = re.findall(pattern, text)
    current_year = datetime.now().year
    return [(f"{date}/{current_year}", desc, amount) for date, desc, amount in matches]


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

# Start the main loop
root.mainloop()


