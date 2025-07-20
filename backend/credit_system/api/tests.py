from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Customer, Loan
from datetime import date, timedelta
import json

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/register'
        self.eligibility_url = '/check-eligibility'
        self.create_loan_url = '/create-loan'

        self.customer = Customer.objects.create(
            customer_id=101,
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=100000,
            approved_limit=3600000
        )

        self.loan = Loan.objects.create(
            loan_id=501,
            customer=self.customer,
            loan_amount=200000,
            tenure=12,
            interest_rate=10.0,
            monthly_payment=17580.0,
            emis_paid_on_time=12,
            date_of_approval=date.today() - timedelta(days=365),
            end_date=date.today() + timedelta(days=365)
        )

    def test_register_customer(self):
        payload = {
            "first_name": "Sathvik",
            "last_name": "Vemula",
            "age": 20,
            "monthly_salary": 30000,
            "phone_number": "9876543210"
        }

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('customer_id', response.json())
        self.assertEqual(response.json()['monthly_salary'], 30000)

    def test_check_eligibility_approved(self):
        payload = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }

        response = self.client.post(self.eligibility_url, data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('approval', response.json())
        self.assertIn('monthly_installment', response.json())

    def test_check_eligibility_customer_not_found(self):
        payload = {
            "customer_id": 999,
            "loan_amount": 50000,
            "interest_rate": 12,
            "tenure": 6
        }

        response = self.client.post(self.eligibility_url, data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_create_loan_successful(self):
        payload = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }

        response = self.client.post(self.create_loan_url, data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('loan_approved', response.json())
        self.assertTrue(response.json()['loan_approved'])
        self.assertIsNotNone(response.json()['loan_id'])

    def test_create_loan_customer_not_found(self):
        payload = {
            "customer_id": 999,
            "loan_amount": 50000,
            "interest_rate": 10,
            "tenure": 12
        }

        response = self.client.post(self.create_loan_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_view_loan_by_id(self):
        url = f'/view-loan/{self.loan.loan_id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], self.loan.loan_id)
        self.assertEqual(response.data['customer']['first_name'], self.customer.first_name)

    def test_view_all_loans_by_customer(self):
        url = f'/view-loans/{self.customer.customer_id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['loan_id'], self.loan.loan_id)
        self.assertIn('repayments_left', response.data[0])
