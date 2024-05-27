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
        self.root.configure(bg='white')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='white')
        style.configure('TLabel', background='white', foreground='green')
        style.configure('TNotebook', background='white', tabposition='sw')  # Move tabs to the bottom
        style.configure('TNotebook.Tab', background='green', foreground='white', padding=[140, 20], font=('Arial', 10, 'bold'))
        style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
        style.configure('Treeview.Heading', background='green', foreground='white')
        style.configure('TButton', background='green', foreground='white', font=('Arial', 12))
        style.configure('TEntry', background='white', foreground='black', font=('Arial', 12))

        self.notebook = ttk.Notebook(root, style='TNotebook')
        self.notebook.pack(expand=True, fill='both')

        self.expenses = []
        self.expense_dates = set()  # Set to track dates with expenses
        self.goals = {}
        self.reminders = []
        self.checking_balance = 1000
        self.savings_balance = 5000

        self.create_expense_table_tab()
        self.create_spending_goals_tab()
        self.create_summary_tab()
        self.create_calendar_tab()
        self.create_financial_literacy_tab()

        self.root.after(86400000, self.check_reminders)  # Check reminders daily

    def create_expense_table_tab(self):
        self.expense_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.expense_frame, text="Expenses")

        add_button = tk.Button(self.expense_frame, text="+ Add Expense", command=self.open_add_expense_form, bg='green', fg='white', font=('Arial', 12, 'bold'))
        add_button.pack(pady=10)

        columns = ("Item", "Cost", "Category", "Account", "Notes")
        self.expense_tree = ttk.Treeview(self.expense_frame, columns=columns, show='headings', style='Treeview')
        self.expense_tree.heading("Item", text="Item")
        self.expense_tree.heading("Cost", text="Cost")
        self.expense_tree.heading("Category", text="Category")
        self.expense_tree.heading("Account", text="Account")
        self.expense_tree.heading("Notes", text="Notes")

        self.expense_tree.pack(expand=True, fill='both')

    def open_add_expense_form(self):
        self.add_expense_popup = tk.Toplevel(self.root)
        self.add_expense_popup.title("Add Expense")
        self.add_expense_popup.configure(bg='white')

        form_frame = ttk.Frame(self.add_expense_popup, style='TFrame')
        form_frame.pack(pady=20)

        self.item_var = tk.StringVar()
        self.cost_var = tk.DoubleVar()
        self.category_var = tk.StringVar()
        self.account_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self.date_var = tk.StringVar()

        tk.Label(form_frame, text="Item:", bg='white', fg='green', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.item_var, font=('Arial', 12), bg='white', fg='black').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Cost:", bg='white', fg='green', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.cost_var, font=('Arial', 12), bg='white', fg='black').grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Category:", bg='white', fg='green', font=('Arial', 12)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.category_var, font=('Arial', 12), bg='white', fg='black').grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Account (Checking/Savings):", bg='white', fg='green', font=('Arial', 12)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.account_var, font=('Arial', 12), bg='white', fg='black').grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", bg='white', fg='green', font=('Arial', 12)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.date_var, font=('Arial', 12), bg='white', fg='black').grid(row=4, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Notes:", bg='white', fg='green', font=('Arial', 12)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(form_frame, textvariable=self.notes_var, font=('Arial', 12), bg='white', fg='black').grid(row=5, column=1, padx=5, pady=5)

        add_button = tk.Button(form_frame, text="Add Expense", command=self.add_expense, bg='green', fg='white', font=('Arial', 12, 'bold'))
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
            self.add_expense_popup.destroy()
            messagebox.showinfo("Info", "Expense added successfully!")

    def create_spending_goals_tab(self):
        self.spending_goals_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.spending_goals_frame, text="Spending Goals")

        categories = ["Healthcare", "Rent", "Food", "Bars", "Transportation", "Bills", "Leisure", "Other"]
        self.goals = {category: 0 for category in categories}
        self.actuals = {category: 0 for category in categories}

        goal_frame = ttk.Frame(self.spending_goals_frame, style='TFrame')
        goal_frame.pack(pady=20)

        self.category_var = tk.StringVar()
        self.goal_var = tk.DoubleVar()

        tk.Label(goal_frame, text="Category:", bg='white', fg='green', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.category_combobox = ttk.Combobox(goal_frame, textvariable=self.category_var, values=categories, font=('Arial', 12))
        self.category_combobox.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(goal_frame, text="Goal:", bg='white', fg='green', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Entry(goal_frame, textvariable=self.goal_var, font=('Arial', 12), bg='white', fg='black').grid(row=1, column=1, padx=5, pady=5)

        add_goal_button = tk.Button(goal_frame, text="Add Goal", command=self.add_goal, bg='green', fg='white', font=('Arial', 12, 'bold'))
        add_goal_button.grid(row=2, columnspan=2, pady=10)

        self.goal_tree = ttk.Treeview(self.spending_goals_frame, columns=("Category", "Goal", "Actual"), show='headings', style='Treeview')
        self.goal_tree.heading("Category", text="Category")
        self.goal_tree.heading("Goal", text="Goal")
        self.goal_tree.heading("Actual", text="Actual")

        self.goal_tree.pack(expand=True, fill='both')

        self.progressbars = {category: ttk.Progressbar(self.spending_goals_frame, orient="horizontal", length=200, mode='determinate') for category in categories}
        for category, progressbar in self.progressbars.items():
            progressbar.pack(pady=5)

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

        self.calculate_actuals()

        for category, goal in self.goals.items():
            actual = self.actuals.get(category, 0)
            self.goal_tree.insert('', tk.END, values=(category, goal, actual))
            self.update_progressbar(category, actual, goal)

    def calculate_actuals(self):
        self.actuals = {category: 0 for category in self.goals}
        for expense in self.expenses:
            category = expense[2]
            cost = expense[1]
            if category in self.actuals:
                self.actuals[category] += cost

    def update_progressbar(self, category, actual, goal):
        progressbar = self.progressbars[category]
        percentage = (actual / goal) * 100 if goal != 0 else 0
        progressbar['value'] = percentage

        if percentage < 50:
            progressbar.configure(style='green.Horizontal.TProgressbar')
        elif 50 <= percentage < 100:
            progressbar.configure(style='yellow.Horizontal.TProgressbar')
        else:
            progressbar.configure(style='red.Horizontal.TProgressbar')
     

    def create_summary_tab(self):
        self.summary_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.summary_frame, text="Summary")

        self.fig_summary = Figure(figsize=(5, 5), dpi=100)
        self.ax_summary = self.fig_summary.add_subplot(111)
        self.fig_summary.patch.set_facecolor('white')
        self.ax_summary.set_facecolor('white')

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
            self.ax_summary.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'color': "green"})
            self.ax_summary.text(0, 0, "No data", color="green", ha="center", va="center", fontsize=14)
        else:
            self.ax_summary.clear()
            self.ax_summary.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'color': "green"})
        
        self.canvas_summary.draw()

    def create_calendar_tab(self):
        self.calendar_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.calendar_frame, text="Calendar")

        self.calendar = Calendar(self.calendar_frame, selectmode='day', year=2024, month=5, day=25)
        self.calendar.pack(pady=20, expand=True, fill='both')

        date_frame = ttk.Frame(self.calendar_frame, style='TFrame')
        date_frame.pack(pady=10)

        self.date_input_var = tk.StringVar()

        tk.Label(date_frame, text="Enter Date (YYYY-MM-DD):", bg='white', fg='green', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(date_frame, textvariable=self.date_input_var, font=('Arial', 12), bg='white', fg='black').grid(row=0, column=1, padx=5, pady=5)
        tk.Button(date_frame, text="Show Transactions", command=self.show_transactions, bg='green', fg='white', font=('Arial', 12)).grid(row=0, column=2, padx=5, pady=5)

    def show_transactions(self):
        selected_date = self.date_input_var.get()
        transactions = [expense for expense in self.expenses if expense[-1] == selected_date]

        transaction_window = tk.Toplevel(self.root)
        transaction_window.title(f"Transactions on {selected_date}")
        transaction_window.configure(bg='white')

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

    def create_financial_literacy_tab(self):
        self.financial_literacy_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.financial_literacy_frame, text="Financial Literacy")

      topics = [
        ("Savings", self.show_savings_info),
        ("Retirement", self.show_retirement_info),
        ("Tax", self.show_tax_info),
        ("Investing", self.show_investing_info),
        ("Income", self.show_income_info)
    ]

    for topic, command in topics:
        button = tk.Button(self.financial_literacy_frame, text=topic, command=command, bg='green', fg='white', font=('Arial', 14, 'bold'), width=20, height=3)
        button.pack(pady=10)

    def show_savings_info(self):
        self.show_info_window("Savings", """
        **Different Types of Savings Accounts:**
        1. **Regular Savings Account**: Basic account offering interest on deposits.
        2. **High-Yield Savings Account**: Higher interest rates compared to regular savings.
        3. **Money Market Account**: Offers benefits of both savings and checking accounts, usually higher interest rates.
        4. **Certificate of Deposit (CD)**: Fixed interest rate for a fixed period.
        5. **Individual Retirement Accounts (IRA)**: Savings account with tax advantages for retirement savings.

        **Nuances of Savings:**
        - **Emergency Funds**: Importance of setting aside funds for unexpected expenses.
        - **Interest Rates**: How different accounts yield different returns.
        - **Accessibility**: Comparing liquidity of different savings vehicles.
        """)

    def show_retirement_info(self):
        self.show_info_window("Retirement", """
        **Ways to Prepare for Retirement:**
        1. **401(k)**: Employer-sponsored retirement account with tax benefits.
        2. **Roth IRA**: Individual retirement account funded with post-tax dollars.
        3. **Traditional IRA**: Individual retirement account funded with pre-tax dollars.
        4. **Pension Plans**: Employer-provided retirement benefits.
        5. **Annuities**: Insurance products that provide a fixed income stream in retirement.

        **Tips for Retirement Planning:**
        - **Start Early**: The benefits of compound interest over time.
        - **Contribute Regularly**: Importance of consistent contributions.
        - **Diversify Investments**: Balancing risk and return through varied investments.
        - **Understand Tax Implications**: Tax benefits and liabilities of different retirement accounts.
        """)

    def show_tax_info(self):
        self.show_info_window("Tax", """
        **Relevant Tax Laws:**
        1. **Income Tax**: Tax on earnings from work and investments.
        2. **Sales Tax**: Tax on purchased goods and services.
        3. **Property Tax**: Tax on property ownership.
        4. **Estate Tax**: Tax on inherited wealth.
        5. **Capital Gains Tax**: Tax on profits from investments.

        **Tips for Tax Management:**
        - **Keep Accurate Records**: Importance of maintaining detailed financial records.
        - **Deductions and Credits**: Maximizing tax savings through allowable deductions and credits.
        - **Estimated Taxes**: Planning for tax payments if self-employed.
        """)

    def show_investing_info(self):
        self.show_info_window("Investing", """
        **Basics of Investing for Children:**
        1. **Stocks**: Buying shares of companies.
        2. **Bonds**: Loans made to companies or governments.
        3. **Mutual Funds**: Pooled investments in various securities.
        4. **Real Estate**: Investing in property.
        5. **Index Funds**: Funds tracking market indices.

        **Key Investment Principles:**
        - **Start Early**: Leverage the power of compound interest.
        - **Diversify**: Spread investments to manage risk.
        - **Understand Fees**: Awareness of investment costs and their impact.
          """)

    def show_income_info(self):
        self.show_info_window("Income", """
        **Ways to Earn Income for Teenagers:**
        1. **Part-Time Jobs**: Working in retail, food service, etc.
        2. **Freelancing**: Offering skills like writing, graphic design.
        3. **Tutoring**: Helping peers or younger students.
        4. **Online Businesses**: Selling products or services online.
        5. **Passive Income**: Investing in stocks, real estate, etc.

        **Tips for Managing Income:**
        - **Save a Portion of Earnings**: Importance of saving.
        - **Invest Wisely**: Basics of investing.
        - **Learn About Budgeting**: Managing expenses and savings.
        """)

    def show_info_window(self, title, info):
        info_window = tk.Toplevel(self.root)
        info_window.title(title)
        info_window.configure(bg='white')

        label = tk.Label(info_window, text=title, bg='white', fg='green', font=('Arial', 16, 'bold'))
        label.pack(pady=10)

        text = tk.Text(info_window, wrap=tk.WORD, bg='white', fg='black', font=('Arial', 12))
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)
        text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    # Add these methods to your BudgetApp class
    BudgetApp.create_financial_literacy_tab = create_financial_literacy_tab
    BudgetApp.show_savings_info = show_savings_info
    BudgetApp.show_retirement_info = show_retirement_info
    BudgetApp.show_tax_info = show_tax_info
    BudgetApp.show_investing_info = show_investing_info
    BudgetApp.show_income_info = show_income_info
    BudgetApp.show_info_window = show_info_window
      

    # Rest of your methods...

    def show_definition(self, definition):
        messagebox.showinfo("Definition", definition)

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

