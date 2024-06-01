import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkcalendar import DateEntry
import random
from threading import Timer
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Initialize the main application window
root = tk.Tk()
root.title("Personal Finance Manager")
root.geometry("1000x700")

# Create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both')

# Create basic tabs
budget_tab = ttk.Frame(notebook)
analytics_tab = ttk.Frame(notebook)
savings_tab = ttk.Frame(notebook)
literacy_tab = ttk.Frame(notebook)
goals_tab = ttk.Frame(notebook)

notebook.add(budget_tab, text="Budget Expenses")
notebook.add(analytics_tab, text="Analytics")
notebook.add(savings_tab, text="Savings")
notebook.add(literacy_tab, text="Financial Literacy")
notebook.add(goals_tab, text="Goals & Habits")

# Initialize DataFrame to store expenses
expense_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

# Define the categories and their average spending limits
categories_limits = {
    "coffee": 3.00,
    "groceries": 100.00,
    "dining out": 25.00,
    "clothing": 50.00,
    "entertainment": 20.00,
    "transportation": 30.00,
    "bars": 20.00,
    "electronics": 100.00,
    "health": 30.00,
    "fitness": 40.00,
    "travel": 200.00,
    "home supplies": 50.00,
    "utilities": 100.00,
    "personal care": 20.00,
    "miscellaneous": 10.00
}

# Define suggestions for each category
suggestions_map = {
    "coffee": "Consider switching to a cheaper coffee brand like Folgers.",
    "groceries": "Consider shopping at discount grocery stores.",
    "dining out": "Limit dining out to special occasions and try cooking at home more.",
    "clothing": "Shop during sales or use discount stores.",
    "entertainment": "Look for free or low-cost entertainment options.",
    "transportation": "Consider public transportation or carpooling.",
    "bars": "Limit visits to bars or look for happy hour deals.",
    "electronics": "Buy refurbished or wait for sales.",
    "health": "Use generic brands for medicines and health supplies.",
    "fitness": "Look for cheaper gym memberships or workout at home.",
    "travel": "Plan trips during off-peak times and use budget airlines.",
    "home supplies": "Buy in bulk or during sales.",
    "utilities": "Implement energy-saving measures to reduce bills.",
    "personal care": "Look for generic brands or DIY options.",
    "miscellaneous": "Limit impulse purchases and stick to a budget."
}

# Function to generate savings suggestions
def generate_savings_suggestions():
    suggestions = []
    if not expense_df.empty:
        for category, limit in categories_limits.items():
            category_expenses = expense_df[expense_df['Category'].str.lower() == category]
            if not category_expenses.empty:
                avg_expense = category_expenses["Amount"].mean()
                if avg_expense > limit:
                    suggestion = suggestions_map.get(category, "Consider reducing spending in this category.")
                    suggestions.append((category, avg_expense, suggestion))
    return suggestions

# Function to update savings suggestions
def update_savings_suggestions():
    for widget in savings_suggestions_frame.winfo_children():
        widget.destroy()
    
    suggestions = generate_savings_suggestions()
    if suggestions:
        for category, avg_expense, suggestion in suggestions:
            suggestion_text = f"You've been spending an average of ${avg_expense:.2f} on {category}. {suggestion}"
            
            suggestion_frame = ttk.Frame(savings_suggestions_frame, relief="solid", borderwidth=1, padding=10)
            suggestion_frame.pack(pady=5, fill='x', expand=True)

            ttk.Label(suggestion_frame, text=suggestion_text, wraplength=700, justify='left').pack(pady=5)

            button_frame = ttk.Frame(suggestion_frame)
            button_frame.pack()

            accept_button = ttk.Button(button_frame, text="Accept Strategy", command=lambda cat=category: accept_strategy(cat, suggestion_frame))
            accept_button.pack(side="left", padx=5)

            decline_button = ttk.Button(button_frame, text="Decline Strategy", command=suggestion_frame.destroy)
            decline_button.pack(side="left", padx=5)

def accept_strategy(category, frame):
    goals_listbox.insert(tk.END, f"Reduce spending on {category}")
    frame.destroy()

# Add widgets to display savings suggestions
savings_frame = ttk.Frame(savings_tab)
savings_frame.pack(expand=1, fill='both', padx=10, pady=10)

ttk.Label(savings_frame, text="Savings Suggestions").pack(pady=10)

savings_suggestions_frame = ttk.Frame(savings_frame)
savings_suggestions_frame.pack(expand=1, fill='both')

# Define treeview for budget expenses
columns = ("Date", "Description", "Category", "Amount")

tree = ttk.Treeview(budget_tab, columns=columns, show='headings')
tree.heading("Date", text="Date")
tree.heading("Description", text="Description")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount")

for col in columns:
    tree.column(col, anchor='center')

tree.pack(expand=1, fill='both')

# Add entry form
entry_frame = ttk.Frame(budget_tab)
entry_frame.pack(fill='x', padx=10, pady=10)

date_entry = DateEntry(entry_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
description_entry = ttk.Entry(entry_frame)
category_entry = ttk.Entry(entry_frame)
amount_entry = ttk.Entry(entry_frame)

date_entry.grid(row=0, column=1, padx=5, pady=5)
description_entry.grid(row=1, column=1, padx=5, pady=5)
category_entry.grid(row=2, column=1, padx=5, pady=5)
amount_entry.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(entry_frame, text="Date:").grid(row=0, column=0, padx=(0, 5), sticky='e')
ttk.Label(entry_frame, text="Description:").grid(row=1, column=0, padx=(0, 5), sticky='e')
ttk.Label(entry_frame, text="Category:").grid(row=2, column=0, padx=(0, 5), sticky='e')
ttk.Label(entry_frame, text="Amount:").grid(row=3, column=0, padx=(0, 5), sticky='e')


def add_expense():
    global expense_df
    try:
        # Validate and collect input data
        date_value = date_entry.get()
        description_value = description_entry.get()
        category_value = category_entry.get()
        amount_value = float(amount_entry.get())

        new_expense = pd.DataFrame({
            "Date": [date_value],
            "Description": [description_value],
            "Category": [category_value],
            "Amount": [amount_value]
        })

        # Append the new expense to the DataFrame using pd.concat
        expense_df = pd.concat([expense_df, new_expense], ignore_index=True)

        # Insert the new expense into the Treeview
        tree.insert("", "end", values=(date_value, description_value, category_value, amount_value))

        # Clear the entry fields
        date_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)

        # Update analytics and savings suggestions
        update_savings_suggestions()
        update_analytics()
    except ValueError:
        # Handle the case where the amount entered is not a valid float
        print("Invalid amount entered. Please enter a valid number.")

add_button = ttk.Button(entry_frame, text="Add Expense", command=add_expense)
add_button.grid(row=4, columnspan=2, pady=10)

# Analytics tab
def update_analytics():
    for widget in analytics_tab.winfo_children():
        widget.destroy()

    if not expense_df.empty:
        # Total expenses
        total_expense = expense_df["Amount"].sum()
        ttk.Label(analytics_tab, text=f"Total Expense: ${total_expense:.2f}").pack(pady=10)

        # Expenses by category bar chart
        category_expense = expense_df.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots()
        category_expense.plot(kind='bar', ax=ax)
        ax.set_title("Expenses by Category")
        ax.set_ylabel("Amount")

        canvas = FigureCanvasTkAgg(fig, master=analytics_tab)
        canvas.get_tk_widget().pack(expand=1, fill='both')
        canvas.draw()

# Financial literacy tab content
literacy_content = [
    {
        "title": "Managing Personal Finances",
        "content": """
        Managing personal finances is crucial for financial stability and growth. It involves budgeting, saving, investing, and planning for future expenses. Start by tracking your income and expenses to create a budget. Allocate funds for necessities, savings, and discretionary spending. Regularly review and adjust your budget to ensure you are meeting your
        goals.

        Begin by listing all your sources of income, such as salary, freelance work, investments, and any other revenue streams. Next, list all your expenses, including fixed costs like rent or mortgage, utilities, insurance, and variable costs like groceries, entertainment, and dining out. Categorize your expenses to understand where your money is going.

        Use budgeting tools or apps to simplify this process and gain a clearer picture of your financial health. Create a budget that aligns with your financial goals, whether it's saving for a down payment on a house, paying off debt, or building an emergency fund.

        Saving is a critical component of managing personal finances. Aim to save at least 20% of your income each month. Set up automatic transfers to your savings account to ensure consistency. Consider opening a high-yield savings account to earn more interest on your savings.

        Investing is another essential aspect of personal finance. Start by understanding different investment options, such as stocks, bonds, mutual funds, and real estate. Diversify your investments to spread risk and maximize returns. Consider consulting a financial advisor to create an investment strategy that aligns with your risk tolerance and financial goals.

        Planning for future expenses is also crucial. This includes saving for retirement, your children’s education, and potential medical expenses. Take advantage of retirement accounts like 401(k)s and IRAs, which offer tax benefits and help you save more effectively.

        In summary, managing personal finances requires careful planning, budgeting, saving, and investing. Regularly review your financial situation, adjust your budget as needed, and stay focused on your financial goals. By taking control of your finances, you can achieve financial stability and build wealth over time.
        """,
        "quiz": {
            "question": "What is the first step in managing personal finances?",
            "options": ["Tracking income and expenses", "Investing in stocks", "Buying a house", "Taking a loan"],
            "answer": "Tracking income and expenses"
        }
    },
    {
        "title": "Understanding Investments",
        "content": """
        Investing is a key component of building wealth. It involves putting money into assets like stocks, bonds, mutual funds, or real estate with the expectation of generating returns. Before investing, assess your risk tolerance and set clear financial goals. Diversify your portfolio to minimize risks and maximize potential returns. Stay informed about market trends and review your investments regularly.

        Stocks represent ownership in a company and offer the potential for high returns but come with higher risk. Bonds are loans made to corporations or governments, providing regular interest payments and lower risk. Mutual funds pool money from multiple investors to invest in a diversified portfolio of stocks, bonds, or other securities. Real estate investing involves purchasing property to generate rental income or profit from appreciation.

        Understand the power of compounding, where the returns on your investments generate their own returns over time. Start investing early to take full advantage of compounding. Regularly contribute to your investment accounts and reinvest dividends and interest to maximize growth.

        It's important to create a diversified investment portfolio that aligns with your risk tolerance and financial goals. Diversification helps spread risk across different asset classes and sectors, reducing the impact of any single investment's poor performance. Rebalance your portfolio periodically to maintain your desired asset allocation.

        Stay informed about market trends, economic indicators, and financial news. This knowledge can help you make informed investment decisions and identify potential opportunities. However, avoid making impulsive decisions based on short-term market fluctuations. Focus on your long-term investment strategy and stay disciplined.

        Consider working with a financial advisor to develop a personalized investment plan. A professional can help you navigate complex investment options, manage risk, and optimize your portfolio for your specific goals.

        In summary, understanding investments is crucial for building wealth and achieving financial goals. Assess your risk tolerance, diversify your portfolio, stay informed, and seek professional advice when needed. With a well-thought-out investment strategy, you can grow your wealth and secure your financial future.
        """,
        "quiz": {
            "question": "What is a key component of building wealth?",
            "options": ["Buying expensive items", "Investing", "Saving all your money in a bank", "Spending on luxuries"],
            "answer": "Investing"
        }
    },
    {
        "title": "Retirement Planning",
        "content": """
        Retirement planning is essential to ensure financial security in your later years. Start by estimating your retirement needs, considering factors like lifestyle, healthcare, and inflation. Contribute to retirement accounts like 401(k), IRA, or pension plans. Take advantage of employer matches and tax benefits. The earlier you start saving for retirement, the more time your investments have to grow.

        Begin by calculating how much money you'll need in retirement. Consider your desired lifestyle, potential healthcare costs, and inflation. Use retirement calculators to estimate your needs and set realistic savings goals.

        Contribute to retirement accounts regularly. 401(k) plans, offered by many employers, allow you to contribute pre-tax income, reducing your taxable income and growing your savings tax-deferred. Many employers also offer matching contributions, which is essentially free money for your retirement. Take full advantage of this benefit by contributing at least enough to get the full match.

        Individual Retirement Accounts (IRAs) are another option. Traditional IRAs offer tax-deferred growth, while Roth IRAs provide tax-free growth on qualified withdrawals. Choose the account that best fits your financial situation and retirement goals.

        Diversify your retirement investments to spread risk and maximize returns. A mix of stocks, bonds, and other assets can help balance growth and stability. Adjust your investment strategy as you approach retirement to reduce risk and preserve capital.

        Regularly review and adjust your retirement plan. Life changes, such as marriage, children, or career changes, can impact your retirement needs and savings ability. Periodically reassess your plan to ensure it still aligns with your goals.

        Consider working with a financial advisor to create a comprehensive retirement plan. A professional can help you navigate complex investment options, optimize your savings strategy, and plan for contingencies.

        In summary, retirement planning involves estimating your future needs, regularly contributing to retirement accounts, diversifying investments, and adjusting your plan as needed. Starting early and staying disciplined can help ensure a comfortable and financially secure retirement.
        """,
        "quiz": {
            "question": "What should you consider when estimating your retirement needs?",
            "options": ["Lifestyle", "Healthcare", "Inflation", "All of the above"],
            "answer": "All of the above"
        }
    },
    {
        "title": "Building Credit",
        "content": """
        Building and maintaining good credit is important for accessing loans and favorable interest rates. Pay your bills on time, keep your credit card balances low, and avoid opening too many new accounts in a short period. Regularly check your credit report for errors and dispute any inaccuracies. A good credit score can save you money on loans, insurance, and even help you secure a job.

        Your credit score is a numerical representation of your creditworthiness, used by lenders, insurers, and employers to assess risk. FICO scores, the most commonly used, range from 300 to 850, with higher scores indicating better creditworthiness.

        Payment history is the most significant factor in your credit score, accounting for 35%. Always pay your bills on time to maintain a positive payment history. Set up automatic payments or reminders to ensure you never miss a due date.

        Credit utilization, the ratio of your credit card balances to your credit limits, makes up 30% of your score. Keep your utilization below 30% to show lenders you can manage credit responsibly. Paying off your balances in full each month is the best practice.

        Length of credit history accounts for 15% of your score. The longer your credit accounts have been open, the better. Avoid closing old accounts, even if you no longer use them, to maintain a lengthy credit history.

        New credit and credit mix each account for 10% of your score. Opening too many new accounts in a short period can negatively impact your score. Diversify your credit types, such as credit cards, auto loans, and mortgages, to show lenders you can manage various credit products.

        Regularly check your credit report for errors. You're entitled to a free credit report from each of the three major credit bureaus (Equifax, Experian, and TransUnion) annually. Dispute any inaccuracies promptly to prevent them from harming your score.

        In summary, building good credit involves timely bill payments, low credit utilization, maintaining a lengthy credit history, avoiding unnecessary new accounts, and monitoring your credit report. A strong credit score can help you access better financial opportunities and save money on interest rates and insurance premiums.
        """,
        "quiz": {
            "question": "What is one way to build good credit?",
            "options": ["Paying bills on time", "Maxing out credit cards", "Opening many new accounts", "Ignoring credit reports"],
            "answer": "Paying bills on time"
        }
    },
    {
        "title": "Emergency Fund",
        "content": """
        An emergency fund is a savings buffer for unexpected expenses like medical bills, car repairs, or job loss. Aim to save three to six months' worth of living expenses. Keep this money in a high-yield savings account for easy access. An emergency fund provides financial security and peace of mind, helping you avoid debt in times of crisis.

        Start by calculating your monthly living expenses, including rent or mortgage, utilities, groceries, transportation, insurance, and other necessities. Multiply this amount by three to six to determine your emergency fund goal.

        Open a separate savings account for your emergency fund to avoid spending it on non-emergencies. A high-yield savings account is
        ideal as it offers better interest rates than a regular savings account, helping your money grow while remaining accessible.

        Build your emergency fund gradually by setting aside a portion of your income each month. Automate your savings to ensure consistency. Start with a small goal, such as saving one month's worth of expenses, and gradually increase it until you reach your target.

        Prioritize your emergency fund over non-essential spending. Cut back on discretionary expenses like dining out, entertainment, or shopping to accelerate your savings. Look for additional sources of income, such as freelance work or selling unused items, to boost your fund.

        Avoid using your emergency fund for non-emergencies. Only dip into it for genuine emergencies, such as unexpected medical bills, car repairs, or job loss. If you do use it, make it a priority to replenish the fund as soon as possible.

        Regularly review and adjust your emergency fund goal based on changes in your living expenses or financial situation. Life events like moving, having a child, or changing jobs can impact your expenses and necessitate a larger fund.

        An emergency fund provides financial security and peace of mind, reducing the need for high-interest debt like credit cards or personal loans in times of crisis. It allows you to handle unexpected expenses without derailing your long-term financial goals.

        In summary, an emergency fund is essential for financial stability and security. Calculate your living expenses, set a savings goal, prioritize building the fund, and use it wisely. A well-funded emergency fund can help you navigate financial challenges and maintain peace of mind.
        """,
        "quiz": {
            "question": "How many months' worth of living expenses should an emergency fund cover?",
            "options": ["One month", "Three to six months", "Nine months", "Twelve months"],
            "answer": "Three to six months"
        }
    },
    {
        "title": "Debt Management",
        "content": """
        Managing debt is crucial for financial health. Prioritize paying off high-interest debts first, such as credit card balances. Consider debt consolidation or refinancing to lower interest rates. Create a repayment plan and stick to it. Avoid taking on new debt while paying off existing balances. Good debt management can improve your credit score and free up money for savings and investments.

        Start by listing all your debts, including credit cards, student loans, auto loans, and mortgages. Note the interest rate, minimum payment, and outstanding balance for each. This will help you prioritize which debts to pay off first.

        High-interest debts, such as credit card balances, should be your top priority. These debts accrue interest quickly, increasing your overall debt burden. Focus on paying off these debts first to save money on interest.

        Consider debt consolidation or refinancing to lower your interest rates. Debt consolidation involves combining multiple debts into a single loan with a lower interest rate, simplifying your payments. Refinancing replaces an existing loan with a new one at a lower interest rate. Both options can reduce your monthly payments and total interest paid.

        Create a repayment plan and stick to it. Allocate a portion of your income towards debt repayment each month. Use the debt snowball method, where you focus on paying off the smallest debts first, or the debt avalanche method, where you prioritize debts with the highest interest rates. Both methods can help you stay motivated and make steady progress.

        Avoid taking on new debt while paying off existing balances. This includes refraining from using credit cards for new purchases or taking out additional loans. Focus on reducing your debt load before considering new credit.

        Good debt management involves regular monitoring and adjustment. Track your progress and make adjustments as needed to stay on track. Celebrate milestones, such as paying off a credit card or reaching a debt reduction goal, to stay motivated.

        In summary, effective debt management involves prioritizing high-interest debts, considering consolidation or refinancing, creating a repayment plan, avoiding new debt, and regularly monitoring progress. Managing debt well can improve your financial health and free up money for other financial goals.
        """,
        "quiz": {
            "question": "What should you prioritize paying off first?",
            "options": ["Low-interest debts", "High-interest debts", "New debts", "Old debts"],
            "answer": "High-interest debts"
        }
    },
    {
        "title": "Tax Planning",
        "content": """
        Effective tax planning can help you minimize your tax liability and maximize your savings. Understand the tax deductions and credits you qualify for. Contribute to tax-advantaged accounts like IRAs and 401(k)s. Keep detailed records of your expenses and income to ensure accurate tax filings. Consult a tax professional for complex situations and to optimize your tax strategy.

        Start by familiarizing yourself with common tax deductions and credits. Deductions reduce your taxable income, while credits directly reduce your tax liability. Examples include the mortgage interest deduction, student loan interest deduction, child tax credit, and education credits.

        Contributing to tax-advantaged accounts is another effective tax strategy. Traditional IRAs and 401(k) plans allow you to contribute pre-tax income, reducing your taxable income and growing your savings tax-deferred. Roth IRAs offer tax-free growth on qualified withdrawals. Health Savings Accounts (HSAs) provide tax benefits for medical expenses.

        Keep detailed records of your income and expenses throughout the year. This includes receipts, invoices, bank statements, and other financial documents. Organized records make tax filing easier and help ensure you claim all eligible deductions and credits.

        Consider consulting a tax professional for complex tax situations, such as owning a business, having significant investments, or experiencing major life changes. A tax professional can provide personalized advice, help you navigate tax laws, and optimize your tax strategy.

        Plan your finances with taxes in mind. This includes timing income and expenses to take advantage of tax benefits, managing capital gains and losses, and making charitable contributions. For example, bunching charitable donations into one year can maximize itemized deductions.

        Regularly review and adjust your tax strategy as needed. Tax laws and personal circumstances change, so it's important to stay informed and make adjustments to optimize your tax planning.

        In summary, effective tax planning involves understanding deductions and credits, contributing to tax-advantaged accounts, keeping detailed records, consulting a tax professional, planning finances with taxes in mind, and regularly reviewing your strategy. Proper tax planning can minimize your tax liability and increase your savings.
        """,
        "quiz": {
            "question": "What can help you minimize tax liability?",
            "options": ["Ignoring tax laws", "Effective tax planning", "Avoiding tax payments", "Not keeping records"],
            "answer": "Effective tax planning"
        }
    },
    {
        "title": "Insurance Planning",
        "content": """
        Insurance is a vital part of financial planning, providing protection against unforeseen events. Assess your insurance needs, including health, life, disability, auto, and homeowners/renters insurance. Shop around for the best rates and coverage. Regularly review your policies to ensure they meet your current needs. Adequate insurance can prevent financial hardships and provide peace of mind.

        Health insurance covers medical expenses and is essential for managing healthcare costs. Evaluate different plans to find one that fits your needs and budget. Consider factors like premiums, deductibles, co-pays, and coverage limits. Employer-sponsored plans, government programs, and private insurance are common options.

        Life insurance provides financial support to your beneficiaries in the event of your death. Term life insurance offers coverage for a specific period, while whole life insurance provides lifelong coverage with a cash value component. Choose a policy that aligns with your financial goals and provides sufficient coverage for your dependents.

        Disability insurance replaces a portion of your income if you become unable to work due to illness or injury. Short-term disability covers temporary disabilities, while long-term disability provides coverage for extended periods. Employer-sponsored plans and private insurance are available options.

        Auto insurance is mandatory in most states and covers vehicle-related expenses, including accidents, theft, and damage. Liability coverage, comprehensive coverage, and collision coverage are common components. Shop around for the best rates and consider bundling policies for discounts.

        Homeowners or renters insurance protects your home and belongings against damage, theft, and liability. Homeowners insurance is required for mortgage holders, while renters insurance is recommended for those who rent. Review your policy to ensure it provides adequate coverage for your property and personal possessions.

        Regularly review your insurance policies to ensure they meet your current needs. Life changes, such as marriage, having children, or buying a home, may necessitate additional coverage. Update your beneficiaries and coverage amounts as needed.

        Shop around for the best insurance rates and coverage. Compare quotes from multiple providers to find the best value. Consider working with an insurance broker to navigate complex options and find the right policies for your needs.

        In summary, insurance planning involves assessing your needs, shopping for the best rates, regularly reviewing policies, and ensuring adequate coverage. Proper insurance planning can prevent financial hardships and provide peace of mind.
        """,
        "quiz": {
            "question": "What type of insurance might you need?",
            "options": ["Health insurance", "Life insurance", "Auto insurance", "All of the above"],
            "answer": "All of the above"
        }
    },
    {
        "title": "Estate Planning",
        "content": """
        Estate planning involves preparing for the management and disposal of your estate after death. Create a will to outline how your assets should be distributed. Consider setting up trusts to manage your assets and minimize estate taxes. Designate beneficiaries for your accounts and insurance policies. Review and update your estate plan regularly to reflect changes in your life circumstances.

        A will is a legal document that specifies how your assets should be distributed after your death. It also allows you to designate a guardian for minor children and an executor to manage your estate. Without a will, your assets will be
        distributed according to state laws, which may not align with your wishes. Create a will to ensure your assets are distributed according to your preferences and to provide guidance for your loved ones.

        Trusts are another important estate planning tool. A trust is a legal entity that holds and manages assets on behalf of beneficiaries. There are several types of trusts, including revocable trusts, irrevocable trusts, and testamentary trusts. Trusts can help minimize estate taxes, avoid probate, and provide ongoing management of assets for beneficiaries. Consult an estate planning attorney to determine the best type of trust for your needs.

        Designate beneficiaries for your financial accounts, retirement plans, and insurance policies. Beneficiary designations override instructions in your will, so it's important to keep them updated. Review your designations regularly, especially after major life events like marriage, divorce, or the birth of a child.

        Power of attorney (POA) is another critical component of estate planning. A POA grants someone the authority to make legal and financial decisions on your behalf if you become incapacitated. There are different types of POA, including durable POA and medical POA. Choose a trusted individual to act as your agent and clearly outline their responsibilities.

        Advance healthcare directives, also known as living wills, provide instructions for your medical care if you become unable to communicate your wishes. These documents can specify your preferences for life-sustaining treatments, organ donation, and other healthcare decisions. Discuss your wishes with your loved ones and healthcare providers to ensure they are honored.

        Estate planning also involves managing estate taxes. Depending on the size of your estate, federal and state estate taxes may apply. Strategies to minimize estate taxes include gifting assets during your lifetime, setting up trusts, and making charitable donations. Consult with an estate planning attorney or financial advisor to develop a tax-efficient plan.

        Regularly review and update your estate plan to reflect changes in your life circumstances, such as marriage, divorce, the birth of a child, or significant changes in your assets. Keep your estate planning documents in a safe place and ensure your executor and key family members know their location.

        In summary, estate planning involves creating a will, setting up trusts, designating beneficiaries, establishing powers of attorney, and managing estate taxes. Regularly review and update your plan to ensure it aligns with your current wishes and circumstances. Proper estate planning provides peace of mind and ensures your assets are managed and distributed according to your preferences.
        """,
        "quiz": {
            "question": "What is one purpose of creating a will?",
            "options": ["To outline asset distribution", "To increase taxes", "To avoid all legal processes", "To spend all money"],
            "answer": "To outline asset distribution"
        }
    },
    {
        "title": "Financial Goal Setting",
        "content": """
        Setting financial goals is essential for achieving financial success. Define short-term, medium-term, and long-term goals. Make your goals specific, measurable, achievable, relevant, and time-bound (SMART). Create a plan to achieve each goal and track your progress. Regularly review and adjust your goals as needed. Financial goal setting provides direction and motivation for managing your finances effectively.

        Start by identifying your short-term, medium-term, and long-term financial goals. Short-term goals are those you aim to achieve within a year, such as saving for a vacation or paying off a credit card. Medium-term goals typically take one to five years to achieve, such as buying a car or saving for a down payment on a house. Long-term goals are those that take more than five years to achieve, such as saving for retirement or funding your children's education.

        Use the SMART criteria to define your goals: Specific, Measurable, Achievable, Relevant, and Time-bound. Specific goals clearly define what you want to achieve. Measurable goals have clear criteria for tracking progress. Achievable goals are realistic and attainable. Relevant goals align with your values and long-term objectives. Time-bound goals have a specific deadline for completion.

        Create a plan to achieve each goal. Break down your goals into smaller, actionable steps. For example, if your goal is to save $10,000 for a down payment on a house in three years, calculate how much you need to save each month and identify ways to reduce expenses or increase income to meet that target.

        Track your progress regularly. Use budgeting tools or financial apps to monitor your income, expenses, and savings. Review your goals periodically to ensure you are on track and make adjustments as needed. Celebrate milestones and achievements to stay motivated.

        Adjust your goals as needed. Life changes, such as getting married, having children, changing jobs, or experiencing a financial setback, may require you to reassess and adjust your goals. Be flexible and open to revising your goals to reflect your current circumstances.

        Financial goal setting provides direction and motivation for managing your finances. By defining clear goals, creating a plan, tracking progress, and making adjustments as needed, you can achieve financial success and build a secure financial future.

        In summary, financial goal setting involves defining short-term, medium-term, and long-term goals, using the SMART criteria, creating a plan, tracking progress, and adjusting goals as needed. Setting clear financial goals provides direction and motivation, helping you achieve financial success and build a secure financial future.
        """,
        "quiz": {
            "question": "What does SMART stand for in financial goal setting?",
            "options": ["Simple, Manageable, Achievable, Relevant, Time-bound", "Specific, Measurable, Achievable, Relevant, Time-bound", "Secure, Monetary, Achievable, Relevant, Timely", "Specific, Monetary, Achievable, Realistic, Time-bound"],
            "answer": "Specific, Measurable, Achievable, Relevant, Time-bound"
        }
    }
]

def display_article(content, quiz):
    for widget in literacy_tab.winfo_children():
        widget.destroy()
    
    text_widget = tk.Text(literacy_tab, wrap='word')
    text_widget.insert(tk.END, content)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(pady=10, padx=10, expand=1, fill='both')
    
    ttk.Label(literacy_tab, text="Quiz", font=("Arial", 12, "bold")).pack(pady=10)
    ttk.Label(literacy_tab, text=quiz["question"]).pack(pady=5)
    
    quiz_var = tk.StringVar()
    for option in quiz["options"]:
        ttk.Radiobutton(literacy_tab, text=option, variable=quiz_var, value=option).pack(anchor=tk.W)
    
    def check_answer():
        global incorrect_attempt
        if quiz_var.get() == quiz["answer"]:
            ttk.Label(literacy_tab, text="Correct!", foreground="green").pack(pady=5)
        else:
            ttk.Label(literacy_tab, text=f"Incorrect! The correct answer is: {quiz['answer']}", foreground="red").pack(pady=5)
    
    ttk.Button(literacy_tab, text="Submit Answer", command=check_answer).pack(pady=10)

    back_button = ttk.Button(literacy_tab, text="Back", command=lambda: display_articles())
    back_button.pack(pady=10)


def display_articles():
    for widget in literacy_tab.winfo_children():
        widget.destroy()
    
    ttk.Label(literacy_tab, text="Financial Literacy Articles", font=("Arial", 14, "bold")).pack(pady=10)
    
    for article in literacy_content:
        button = ttk.Button(literacy_tab, text=article["title"], command=lambda a=article: display_article(a["content"], a["quiz"]))
        button.pack(pady=5)


display_articles()

# Goals listbox
ttk.Label(goals_tab, text="Goals").pack(pady=10)
goals_listbox = tk.Listbox(goals_tab)
goals_listbox.pack(expand=1, fill='both', padx=10, pady=10)

# Function to start the game


def start_game():
    game_window = tk.Toplevel(root)
    game_window.title("Guess the Number Game")

    game_frame = ttk.Frame(game_window, padding="10")
    game_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(game_frame, text="Guess the number between 1 and 100").grid(row=0, column=0, columnspan=2, pady=10)

    guess_entry = ttk.Entry(game_frame, width=10)
    guess_entry.grid(row=1, column=0, pady=5)

    result_label = ttk.Label(game_frame, text="")
    result_label.grid(row=3, column=0, columnspan=2, pady=5)

    countdown_label = ttk.Label(game_frame, text="Time remaining: 15 seconds")
    countdown_label.grid(row=4, column=0, columnspan=2, pady=5)

    number_to_guess = random.randint(1, 100)
    time_up = False

    def time_out():
        nonlocal time_up
        time_up = True
        result_label.config(text="Time's up! You lose.")

    def check_guess():
        nonlocal time_up
        if time_up:
            return
        try:
            guess = int(guess_entry.get())
            if guess < number_to_guess:
                result_label.config(text="Too low! Try again.")
            elif guess > number_to_guess:
                result_label.config(text="Too high! Try again.")
            else:
                result_label.config(text="Correct! You guessed the number!")
                timer.cancel()
        except ValueError:
            result_label.config(text="Please enter a valid number.")

    def countdown(count):
        if count > 0:
            countdown_label.config(text=f"Time remaining: {count} seconds")
            root.after(1000, countdown, count-1)
        else:
            time_out()

    guess_button = ttk.Button(game_frame, text="Guess", command=check_guess)
    guess_button.grid(row=2, column=0, pady=5)

    # Set a timer for 15 seconds
    timer = Timer(15.0, time_out)
    timer.start()
    countdown(15)

# Button to start the game
ttk.Button(savings_frame, text="Play a Game", command=start_game).pack(pady=5)

# Initial call to update savings suggestions and analytics when the app starts
update_savings_suggestions()
update_analytics()

# Start the Tkinter event loop
root.mainloop()
   