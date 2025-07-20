import os
import sys
import django
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from api.models import Customer, Loan

def load_customers(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'phone_number': str(row['Phone Number']),
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                'current_debt': 0.0
            }
        )
    print("Customers loaded successfully.")

def load_loans(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        customer = Customer.objects.get(customer_id=row['Customer ID'])
        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_payment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'date_of_approval': pd.to_datetime(row['Date of Approval']).date(),
                'end_date': pd.to_datetime(row['End Date']).date()
            }
        )
    print("Loans loaded successfully.")

if __name__ == '__main__':
    load_customers('/app/data/customer_data.xlsx')
    load_loans('/app/data/loan_data.xlsx')