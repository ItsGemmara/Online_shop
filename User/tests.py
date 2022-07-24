from django.forms import ValidationError
from django.test import TestCase
from rest_framework.test import APITestCase, APITransactionTestCase, APIClient, APIRequestFactory
from rest_framework import status

from .validators import PhoneNumberValidator, username_type
from .models import CustomUser

class PhoneNumberValidatorTestCase(TestCase):

    def test_correct_nums(self):
        correct_phone_numbers = ['  +989131111111 ', '+989131111111', '989131111111', '09131111111', '9131111111',]
        for num in correct_phone_numbers:
            phone_number_validator = PhoneNumberValidator(phone_number=num)
            validated_phone_num = phone_number_validator.phone_number_validator()
            self.assertEqual(validated_phone_num, '09131111111')

    def test_invalid_nums(self):
        incorrect_phone_numbers = ['09131111 11', '989111', '98913111111a']
        for num in incorrect_phone_numbers:
            validator = PhoneNumberValidator(num)
            self.assertRaises(ValidationError, validator.phone_number_validator)


class UsernameTypeTestCase(TestCase):

    def test_type(self):
        phone_number_type = username_type('09131111111')
        email_type = username_type('a@gmail.com')
        self.assertEqual('email', email_type['type'])
        self.assertEqual('phone_number', phone_number_type['type'])
        self.assertEqual('a@gmail.com', email_type['username'])
        self.assertEqual('09131111111', phone_number_type['username'])


class PermissionsTestCase(TestCase):

    def test_is_account_owner(self):
        pass


class UserTestCase(APITestCase):
    def setUp(self):
        self.phone_number = '+989131111111'
        self.email = 'aa@gmail.com'
        self.password = 'mmmm1234'
        self.user = CustomUser.objects.create(username='09131111112',
            phone_is_verified=True, email='m@g.com', email_is_verified=True)
        self.user.set_password('mmmm1234')
        self.user.save()

    def test_create_user(self):
        data1 = {
            "username": self.phone_number, 
            "password": self.password, 
            "password2": self.password, 
            }
        data2 = {
            "username": self.email, 
            "password": self.password, 
            "password2": self.password, 
            }
        response1 = self.client.post("/user/users/user-viewset/", data1)
        response2 = self.client.post("/user/users/user-viewset/", data2)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        user_with_email = CustomUser.objects.get(username=self.email)
        user_with_pn = CustomUser.objects.get(username='09131111111')
        self.assertEqual(user_with_email.sign_up_type, 'email')
        self.assertEqual(user_with_pn.sign_up_type, 'phone_number')

    def test_login(self):
        user = CustomUser.objects.get(username='09131111112')
        response = self.client.post('/user/users/user-viewset/login/', {'username':'09131111112', 'password': 'mmmm1234'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user, response.wsgi_request.user)

    def test_update(self):
        user = CustomUser.objects.get(username='09131111112') 
        self.client.login(username='09131111112', password='mmmm1234') # login required
        phone_response = self.client.put(f'/user/users/user-viewset/{user.pk}/', {
            "first_name": "",
            "last_name": "lname",
            "email": "m@g.com",
            "phone_number": "09138855885"
            }) #changing username and phone number
        updated_user = CustomUser.objects.get(username='09138855885')
        self.assertEqual(updated_user.pk, user.pk)
        self.assertEqual(phone_response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_user.username, '09138855885')
        self.assertEqual(updated_user.phone_number, '09138855885')
        self.assertEqual(updated_user.phone_is_verified, False)
        self.assertEqual(updated_user.last_name, 'lname')

    def test_update_email(self):
        user = CustomUser.objects.get(username='09131111112') 
        self.client.login(username='09131111112', password='mmmm1234') # login required
        email_response = self.client.put(f'/user/users/user-viewset/{user.pk}/', {
            "first_name": "fname",
            "last_name": "lname",
            "email": "new@g.com",
            "phone_number": "09138855885"
            }) #changing username and phone number
        updated_user = CustomUser.objects.get(username='09138855885')
        self.assertEqual(email_response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_user.first_name, 'fname')
        self.assertEqual(updated_user.email, 'new@g.com')
        self.assertEqual(updated_user.email_is_verified, False)

    

