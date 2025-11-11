from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationTests(TestCase):
	def test_register_creates_customer_and_allows_login(self):
		"""Post to the registration view and assert the Customer is created and can log in."""
		url = reverse('storefront:register')

		post_data = {
			# UserRegisterForm fields
			'username': 'testuser1',
			'email': 'testuser1@example.com',
			'password1': 'ComplexPass123!',
			'password2': 'ComplexPass123!',

			# CustomerForm fields
			'age': '30',
			'gender': 'Male',
			'employment': '',
			'income_range': '',
			'employment_status': 'Full-time',
			'occupation': 'Tech',
			'education': 'Bachelor',
			'household_size': '2',
			'has_children': 'on',
			'monthly_income_sgd': '5000.00',
		}

		response = self.client.post(url, data=post_data)

		# Expect redirect to home on success
		self.assertEqual(response.status_code, 302)

		# User should exist
		user_qs = User.objects.filter(username='testuser1')
		self.assertTrue(user_qs.exists(), 'User record was not created')
		user = user_qs.first()

		# Check some fields saved from customer form
		self.assertEqual(user.age, 30)
		self.assertEqual(user.employment_status, 'Full-time')

		# Can log in with provided credentials
		login_ok = self.client.login(username='testuser1', password='ComplexPass123!')
		self.assertTrue(login_ok, 'Unable to log in with registered credentials')


