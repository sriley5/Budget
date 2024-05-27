import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget and Money Projection App")
        self.root.configure(bg='black')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='black')
        style.configure('TLabel', background='black', foreground='white')
        style.configure('TNotebook', background='black')
        style.configure('TNotebook.Tab', background='black', foreground='white')
        style.configure('Treeview', background='black', foreground='white', fieldbackground='black')
        style.configure('Treeview.Heading', background='black', foreground='white')
        style.configure('TButton', background='black', foreground='white', font=('Arial', 12))
        style.configure('TEntry', background='black', foreground='white', font=('Arial', 12))

        self.notebook = ttk.Notebook(root, style='TNotebook')
        self.notebook.pack(expand=True, fill='both')

        self.expenses = []
        self.expense_dates = set()  # Set to track dates with expenses
        self.goals = {}
        self.reminders = []
        self.checking_balance = 1000
        self.savings_balance = 5000

        self.create_expense_table_tab()
        self.create_add_expense_tab()
        self.create_spending_goals_tab()
        self.create_summary_tab()
        self.create_calendar_tab()
        self.create_income_tab()
        self.create_recurring_transactions_tab()
        self.create_reminders_tab()

        self.root.after(86400000, self.check_reminders)  # Check reminders daily

    def create_expense_table_tab(self):
        self.expense_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.expense_frame, text="Expense Table")

        columns = ("Item", "Cost", "Category", "Account", "Notes")
        self.expense_tree = ttk.Treeview(self.expense_frame, columns=columns, show='headings', style='Treeview')
        self.expense_tree.heading("Item", text="Item")
        self.expense_tree.heading("Cost", text="Cost")
        self.expense_tree.heading("Category", text="Category")
        self.expense_tree.heading("Account", text="Account")
        self.expense_tree.heading("Notes", text="Notes")

        self.expense_tree.pack(expand=True, fill='both')

    def create_add_expense_tab(self):
        self.add_expense_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.add_expense_frame, text="Add Expense")

        form_frame = ttk.Frame(self.add_expense_frame, style='TFrame')
        form_frame.pack(pady=20)

        self.item_var = tk.StringVar()
        self.cost_var = tk.DoubleVar()
        self.category_var = tk.StringVar()
        self.account_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self.date_var = tk.StringVar()

        tk.Label(form_frame, text="Item:", bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.item_var, font=('Arial', 12), bg='black', fg='white').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Cost:", bg='black', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.cost_var, font=('Arial', 12), bg='black', fg='white').grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Category:", bg='black', fg='white', font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.category_var, font=('Arial', 12), bg='black', fg='white').grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Account (Checking/Savings):", bg='black', fg='white', font=('Arial', 12)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.account_var, font=('Arial', 12), bg='black', fg='white').grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", bg='black', fg='white', font=('Arial', 12)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.date_var, font=('Arial', 12), bg='black', fg='white').grid(row=4, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Notes:", bg='black', fg='white', font=('Arial', 12)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.notes_var, font=('Arial', 12), bg='black', fg='white').grid(row=5, column=1, padx=5, pady=5)

        add_button = tk.Button(form_frame, text="Add Expense", command=self.add_expense, bg='black', fg='white', font=('Arial', 12, 'bold'))
        add_button.grid(row=6, columnspan=2, pady=10)

    def add_expense(self):
        item = self.item_var.get()
        cost = self.cost_var.get()
        category = self.category_var.get()
        account = self.account_var.get()
        notes = self.notes_var.get()
        date = self.date_var.get()
        if item and cost and category and account and notes and date:
            new_expense = (item, cost, category, account, notes, date)
            self.expense_tree.insert('', tk.END, values=new_expense[:-1])
            self.expenses.append(new_expense)
            self.expense_dates.add(date)
            if account == "Checking":
                self.checking_balance -= cost
            elif account == "Savings":
                self.savings_balance -= cost
            self.update_summary_chart()
            self.update_calendar()
            self.update_goals()
            messagebox.showinfo("Info", "Expense added successfully!")

    def create_spending_goals_tab(self):
        self.spending_goals_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.spending_goals_frame, text="Spending Goals")

        categories = ["Healthcare", "Rent", "Food", "Bars", "Transportation", "Bills", "Leisure", "Other"]
        self.goals = {category: 0 for category in categories}

        goal_frame = ttk.Frame(self.spending_goals_frame, style='TFrame')
        goal_frame.pack(pady=20)

        self.category_var = tk.StringVar()
        self.goal_var = tk.DoubleVar()

        tk.Label(goal_frame, text="Category:", bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.category_combobox = ttk.Combobox(goal_frame, textvariable=self.category_var, values=categories, font=('Arial', 12))
        self.category_combobox.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(goal_frame, text="Goal:", bg='black', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(goal_frame, textvariable=self.goal_var, font=('Arial', 12), bg='black', fg='white').grid(row=1, column=1, padx=5, pady=5)

        add_goal_button = tk.Button(goal_frame, text="Add Goal", command=self.add_goal, bg='black', fg='white', font=('Arial', 12, 'bold'))
        add_goal_button.grid(row=2, columnspan=2, pady=10)

        self.goal_tree = ttk.Treeview(self.spending_goals_frame, columns=("Category", "Goal", "Actual"), show='headings', style='Treeview')
        self.goal_tree.heading("Category", text="Category")
        self.goal_tree.heading("Goal", text="Goal")
        self.goal_tree.heading("Actual", text="Actual")

        self.goal_tree.pack(expand=True, fill='both')

        self.update_goals()

    def add_goal(self):
        category = self.category_var.get()
        goal = self.goal_var.get()
        if category and goal:
            self.goals[category] = goal
            self.update_goals()
            messagebox.showinfo("Info", "Goal added successfully!")

    def update_goals(self):
        for row in self.goal_tree.get_children():
            self.goal_tree.delete(row)

        actuals = self.calculate_actuals()

        for category, goal in self.goals.items():
            actual = actuals.get(category, 0)
            self.goal_tree.insert('', tk.END, values=(category, goal, actual))

    def calculate_actuals(self):
        actuals = {}
        for expense in self.expenses:
            category = expense[2]
            cost = expense[1]
            if category in actuals:
                actuals[category] += cost
            else:
                actuals[category] = cost
        return actuals

    def create_summary_tab(self):
        self.summary_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.summary_frame, text="Summary")

        self.fig_summary = Figure(figsize=(5, 5), dpi=100)
        self.ax_summary = self.fig_summary.add_subplot(111)
        self.fig_summary.patch.set_facecolor('black')
        self.ax_summary.set_facecolor('black')

        self.canvas_summary = FigureCanvasTkAgg(self.fig_summary, master=self.summary_frame)
        self.canvas_summary.draw()
        self.canvas_summary.get_tk_widget().pack(expand=True, fill='both')

        self.update_summary_chart()

    def update_summary_chart(self):
        accounts = {"Checking": self.checking_balance, "Savings": self.savings_balance}

        labels = list(accounts.keys())
        sizes = list(accounts.values())

        # Handle cases where all balances are zero
        if all(v == 0 for v in sizes):
            sizes = [1, 1]  # Placeholder to avoid zero division error
            self.ax_summary.clear()
            self.ax_summary.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'color': "white"})
            self.ax_summary.text(0, 0, "No data", color="white", ha="center", va="center", fontsize=14)
        else:
            self.ax_summary.clear()
            self.ax_summary.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'color': "white"})
        
        self.canvas_summary.draw()

    def create_calendar_tab(self):
        self.calendar_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.calendar_frame, text="Calendar")

        self.calendar = Calendar(self.calendar_frame, selectmode='day', year=2024, month=5, day=25)
        self.calendar.pack(pady=20, expand=True, fill='both')

        date_frame = ttk.Frame(self.calendar_frame, style='TFrame')
        date_frame.pack(pady=10)

        self.date_input_var = tk.StringVar()

        tk.Label(date_frame, text="Enter Date (YYYY-MM-DD):", bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(date_frame, textvariable=self.date_input_var, font=('Arial', 12), bg='black', fg='white').grid(row=0, column=1, padx=5, pady=5)
        tk.Button(date_frame, text="Show Transactions", command=self.show_transactions, bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=2, padx=5, pady=5)

    def show_transactions(self):
        selected_date = self.date_input_var.get()
        transactions = [expense for expense in self.expenses if expense[-1] == selected_date]

        transaction_window = tk.Toplevel(self.root)
        transaction_window.title(f"Transactions on {selected_date}")
        transaction_window.configure(bg='black')

        columns = ("Item", "Cost", "Category", "Account", "Notes")
        tree = ttk.Treeview(transaction_window, columns=columns, show='headings', style='Treeview')
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(expand=True, fill='both')

        for transaction in transactions:
            tree.insert('', tk.END, values=transaction[:-1])

    def update_calendar(self):
        # Clear existing marks
        self.calendar.calevent_remove('all')

        # Add marks for each date with expenses
        for date in self.expense_dates:
            self.calendar.calevent_create(date, 'Expense', 'expense')
        
        # Style the marks (optional)
        self.calendar.tag_config('expense', background='red', foreground='white')

    def create_income_tab(self):
        self.income_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.income_frame, text="Income")

        form_frame = ttk.Frame(self.income_frame, style='TFrame')
        form_frame.pack(pady=20)

        self.income_source_var = tk.StringVar()
        self.income_amount_var = tk.DoubleVar()

        tk.Label(form_frame, text="Income Source:", bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.income_source_var, font=('Arial', 12), bg='black', fg='white').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Amount:", bg='black', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.income_amount_var, font=('Arial', 12), bg='black', fg='white').grid(row=1, column=1, padx=5, pady=5)

        add_income_button = tk.Button(form_frame, text="Add Income", command=self.add_income, bg='black', fg='white', font=('Arial', 12, 'bold'))
        add_income_button.grid(row=2, columnspan=2, pady=10)

        self.income_tree = ttk.Treeview(self.income_frame, columns=("Source", "Amount"), show='headings', style='Treeview')
        self.income_tree.heading("Source", text="Source")
        self.income_tree.heading("Amount", text="Amount")
        self.income_tree.pack(expand=True, fill='both')

    def add_income(self):
        source = self.income_source_var.get()
        amount = self.income_amount_var.get()
        if source and amount:
            self.income_tree.insert('', tk.END, values=(source, amount))
            messagebox.showinfo("Info", "Income added successfully!")

    def create_recurring_transactions_tab(self):
        self.recurring_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.recurring_frame, text="Recurring Transactions")

        form_frame = ttk.Frame(self.recurring_frame, style='TFrame')
        form_frame.pack(pady=20)

        self.recurring_type_var = tk.StringVar()
        self.recurring_amount_var = tk.DoubleVar()
        self.recurring_frequency_var = tk.StringVar()

        tk.Label(form_frame, text="Type (Income/Expense):", bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.recurring_type_var, font=('Arial', 12), bg='black', fg='white').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Amount:", bg='black', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.recurring_amount_var, font=('Arial', 12), bg='black', fg='white').grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Frequency (Daily/Weekly/Monthly):", bg='black', fg='white', font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.recurring_frequency_var, font=('Arial', 12), bg='black', fg='white').grid(row=2, column=1, padx=5, pady=5)

        add_recurring_button = tk.Button(form_frame, text="Add Recurring Transaction", command=self.add_recurring_transaction, bg='black', fg='white', font=('Arial', 12, 'bold'))
        add_recurring_button.grid(row=3, columnspan=2, pady=10)

        self.recurring_tree = ttk.Treeview(self.recurring_frame, columns=("Type", "Amount", "Frequency"), show='headings', style='Treeview')
        self.recurring_tree.heading("Type", text="Type")
        self.recurring_tree.heading("Amount", text="Amount")
        self.recurring_tree.heading("Frequency", text="Frequency")
        self.recurring_tree.pack(expand=True, fill='both')

    def add_recurring_transaction(self):
        type_ = self.recurring_type_var.get()
        amount = self.recurring_amount_var.get()
        frequency = self.recurring_frequency_var.get()
        if type_ and amount and frequency:
            self.recurring_tree.insert('', tk.END, values=(type_, amount, frequency))
            messagebox.showinfo("Info", "Recurring transaction added successfully!")

    def export_data(self):
        import csv

        with open('financial_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Item", "Cost", "Category", "Account", "Notes", "Date"])
            for expense in self.expenses:
                writer.writerow(expense)
    
        messagebox.showinfo("Info", "Data exported successfully!")

    def create_reminders_tab(self):
        self.reminders_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.reminders_frame, text="Reminders")

        form_frame = ttk.Frame(self.reminders_frame, style='TFrame')
        form_frame.pack(pady=20)

        self.reminder_name_var = tk.StringVar()
        self.reminder_date_var = tk.StringVar()

        tk.Label(form_frame, text="Reminder Name:", bg='black', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.reminder_name_var, font=('Arial', 12), bg='black', fg='white').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", bg='black', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.reminder_date_var, font=('Arial', 12), bg='black', fg='white').grid(row=1, column=1, padx=5, pady=5)

        add_reminder_button = tk.Button(form_frame, text="Add Reminder", command=self.add_reminder, bg='black', fg='white', font=('Arial', 12, 'bold'))
        add_reminder_button.grid(row=2, columnspan=2, pady=10)

        self.reminder_tree = ttk.Treeview(self.reminders_frame, columns=("Name", "Date"), show='headings', style='Treeview')
        self.reminder_tree.heading("Name", text="Name")
        self.reminder_tree.heading("Date", text="Date")
        self.reminder_tree.pack(expand=True, fill='both')

    def add_reminder(self):
        name = self.reminder_name_var.get()
        date = self.reminder_date_var.get()
        if name and date:
            self.reminder_tree.insert('', tk.END, values=(name, date))
            self.reminders.append((name, date))
            self.calendar.calevent_create(date, name, 'reminder')
            self.calendar.tag_config('reminder', background='blue', foreground='white')
            messagebox.showinfo("Info", "Reminder added successfully!")

    def check_reminders(self):
        today = datetime.date.today()
        for name, date in self.reminders:
            reminder_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if reminder_date == today:
                messagebox.showinfo("Reminder", f"Reminder: {name} is due today!")
        self.root.after(86400000, self.check_reminders)  # Check every day

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()


