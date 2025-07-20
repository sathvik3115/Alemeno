from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
from .models import Customer
from .models import Loan
from datetime import datetime, timedelta, date
import random
import pandas as pd

@api_view(['POST'])
def register_customer(request):
    try:
        data = request.data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        age = data.get("age")
        monthly_salary = data.get("monthly_salary")
        phone_number = data.get("phone_number")

        if not all([first_name, last_name, age, monthly_salary, phone_number]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        approved_limit = round(36 * int(monthly_salary), -5)

        with transaction.atomic():
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                phone_number=phone_number,
                monthly_salary=monthly_salary,
                approved_limit=approved_limit,
            )
            customer.save()

        return Response({
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_salary": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET', 'POST'])
def check_eligibility(request):
    try:
        data = request.data if request.method == 'POST' else request.query_params

        try:
            customer_id = int(data.get('customer_id'))
            loan_amount = float(data.get('loan_amount'))
            interest_rate = float(data.get('interest_rate'))
            tenure = int(data.get('tenure'))
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing input fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        salary = customer.monthly_salary
        approved_limit = customer.approved_limit

        df = pd.read_excel('/app/data/loan_data.xlsx')
        df = df[df['Customer ID'] == customer_id]

        total_current_loans = df['Loan Amount'].sum()
        if total_current_loans > approved_limit:
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": None,
                "tenure": tenure,
                "monthly_installment": None
            }, status=status.HTTP_200_OK)

        past_loans = len(df)
        on_time_emi = df['EMIs paid on Time'].sum()
        current_year = datetime.now().year
        current_year_loans = df[df['Date of Approval'].dt.year == current_year]
        total_volume = df['Loan Amount'].sum()

        credit_score = 0
        if past_loans > 0:
            credit_score += min((on_time_emi / past_loans) * 35, 35)
        credit_score += min(past_loans * 5, 15)
        credit_score += min(len(current_year_loans) * 5, 15)
        credit_score += min((total_volume / 100000) * 5, 15)

        r = interest_rate / 12 / 100
        emi = loan_amount * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)

        if emi > 0.5 * salary:
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": None,
                "tenure": tenure,
                "monthly_installment": None
            }, status=status.HTTP_200_OK)

        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if interest_rate >= 12:
                approval = True
            else:
                corrected_interest_rate = 12
        elif 10 < credit_score <= 30:
            if interest_rate >= 16:
                approval = True
            else:
                corrected_interest_rate = 16
        else:
            approval = False

        if corrected_interest_rate != interest_rate:
            r = corrected_interest_rate / 12 / 100
            emi = loan_amount * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)

        return Response({
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(emi, 2)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET', 'POST'])
def create_loan(request):
    if request.method == 'GET':
        return Response({
            "message": "Send a POST request to apply for a loan with required fields: customer_id, loan_amount, interest_rate, tenure"
        })

    try:
        data = request.data
        customer_id = int(data.get('customer_id'))
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        customer = Customer.objects.get(customer_id=customer_id)
        salary = customer.monthly_salary
        approved_limit = customer.approved_limit

        df = pd.read_excel('/app/data/loan_data.xlsx')
        df = df[df['Customer ID'] == customer_id]

        total_current_loans = df['Loan Amount'].sum()
        if total_current_loans > approved_limit:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Total existing loans exceed approved limit.",
                "monthly_installment": None
            })

        past_loans = len(df)
        on_time_emi = df['EMIs paid on Time'].sum()
        current_year = datetime.now().year
        current_year_loans = df[df['Date of Approval'].dt.year == current_year]
        total_volume = df['Loan Amount'].sum()

        credit_score = 0
        if past_loans > 0:
            credit_score += min((on_time_emi / past_loans) * 35, 35)
        credit_score += min(past_loans * 5, 15)
        credit_score += min(len(current_year_loans) * 5, 15)
        credit_score += min((total_volume / 100000) * 5, 15)

        r = interest_rate / 12 / 100
        emi = loan_amount * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)

        if emi > 0.5 * salary:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "EMI exceeds 50% of monthly salary.",
                "monthly_installment": None
            })

        approved = False
        corrected_rate = interest_rate

        if credit_score > 50:
            approved = True
        elif 30 < credit_score <= 50:
            if interest_rate >= 12:
                approved = True
            else:
                corrected_rate = 12
        elif 10 < credit_score <= 30:
            if interest_rate >= 16:
                approved = True
            else:
                corrected_rate = 16
        else:
            approved = False

        if corrected_rate != interest_rate:
            r = corrected_rate / 12 / 100
            emi = loan_amount * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)

        if not approved:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Loan not approved based on credit score criteria.",
                "monthly_installment": None
            })

        loan = Loan.objects.create(
            loan_id=random.randint(100000, 999999),
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_rate,
            monthly_payment=round(emi, 2),
            emis_paid_on_time=0,
            date_of_approval=datetime.today(),
            end_date=datetime.today() + timedelta(days=30 * tenure)
        )

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully.",
            "monthly_installment": round(emi, 2)
        })

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
        customer = loan.customer

        return Response({
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": round(loan.monthly_payment, 2),
            "tenure": loan.tenure
        })

    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from datetime import date

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)

        loan_list = []
        for loan in loans:
            today = date.today()
            if today >= loan.end_date:
                repayments_left = 0
            else:
                months_left = (loan.end_date.year - today.year) * 12 + (loan.end_date.month - today.month)
                repayments_left = max(months_left, 0)

            loan_list.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": round(loan.monthly_payment, 2),
                "repayments_left": repayments_left
            })

        return Response(loan_list)

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
