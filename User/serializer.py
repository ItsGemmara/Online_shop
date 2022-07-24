import random
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, logout
from django.utils.translation import gettext_lazy as _

from .validators import username_type, OTPValidator, PhoneNumberValidator, validate_email
from .models import CustomUser, OTP


class SignUpSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(write_only=True)

    def validate(self, validated_data):
        if validated_data['password'] != validated_data['password2']:
            raise ValidationError({'password': "Enter same password!"})
        if validated_data['username']:
            try:
                validated_username = username_type(username=validated_data['username'])
            except:
                raise ValidationError({'username':'invalid phone number or email'})
            validated_data['username'] = validated_username['username']
            validated_data['username_type'] = validated_username['type']           
        else:
            raise ValidationError({'username': 'username is required'})
        return validated_data

    def create(self, validated_data):

        password = validated_data['password']
        username = validated_data['username']
        username_type = validated_data['username_type']

        if self.validate(validated_data):
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                sign_up_type=username_type
            )
            if username_type == 'email':
                user.email = username
                user.save()
            elif username_type == 'phone_number':
                user.phone_number = username
                user.save()
            return user
        else:
            raise ValidationError("Enter same password!")

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2')
        write_only_fields = ('password2',)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    
    def validate(self, validated_data):
        if validated_data['username'] and validated_data['password']:
            try:
                validated_username = username_type(username=validated_data['username'])
            except:
                raise ValidationError({'username':'invalid phone number or email'})
            try:
                user = CustomUser.objects.get(username = validated_username['username'])
            except:
                try:
                    if validated_username['type'] == 'email':
                        user = CustomUser.objects.get(email = validated_username['username'])
                    else:
                        user = CustomUser.objects.get(phone_number = validated_username['username'])
                except:
                    raise ValidationError({'username': f'{validated_username["type"]} does not exists.'})
            if not user.is_active:
                raise ValidationError({'username': 'account is deactive.'})
            if validated_username['type'] == 'email':
                if not user.email_is_verified:
                    raise ValidationError({'username': 'The email is not verified. Varify your email first.'})
            else:
                if not user.phone_is_verified:
                    raise ValidationError({'username': 'The phone number is not verified. Varify your phone number first.'})
            validated_data['user'] = authenticate(username=validated_username['username'], password=validated_data['password'])
            if not validated_data['user']:
                raise ValidationError({'password': f'wrong password for {validated_username["username"]}'})
        else:
            raise ValidationError('username and password are required.')
        return validated_data
    class Meta:
        model = CustomUser
        fields = ("username", "password",)


class UpdateUserSerializer(serializers.ModelSerializer):
    
    def validate(self, validated_data):
        email = validated_data['email']
        phone_number = validated_data['phone_number']
        if email:
            validate_email(email)
        if phone_number:
            validator = PhoneNumberValidator(phone_number=phone_number)
            validator.phone_number_validator()
        return validated_data

    def update(self, instance, validated_data):
        uname_type = username_type(instance.username)['type']
        if validated_data['email'] != instance.email:
            instance.email = validated_data['email']
            instance.email_is_verified = False
            instance.save()
            if uname_type == 'email':
                instance.username = validated_data['email']
                instance.save()
                logout(self.context['request'])
        if validated_data['phone_number'] != instance.phone_number:
            instance.phone_number = validated_data['phone_number']
            instance.phone_is_verified = False
            instance.save()
            if uname_type == 'phone_number':
                instance.username = validated_data['phone_number']
                instance.save()
                logout(self.context['request'])
        print(self.context['request'])
        return super(UpdateUserSerializer, self).update(instance, validated_data)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "phone_number")


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ("username", "pk")


class UserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "date_joined")


# class UserRefreshTokenSerializer(serializers.ModelSerializer):

#     username = serializers.CharField(write_only=True)
#     password = serializers.CharField(write_only=True)
#     url = serializers.CharField(write_only=True)
#     grant_type = serializers.CharField(write_only=True)
#     client_id = serializers.CharField(write_only=True)
#     client_secret = serializers.CharField(write_only=True)

#     def validate(self, validated_data):
#         if validated_data['username'] and validated_data['password']:
#             current_user = self.context['request'].user
#             if not current_user.is_anonymous:
#                 if current_user.username != validated_data['username']:
#                     raise ValidationError(f'The username you logged in with does not match '
#                                           f'{validated_data["username"]}')
#             else:
#                 try:
#                     User.objects.get(username=validated_data['username'])
#                 except Exception as e:
#                     raise ValidationError('username dose not exists')
#             user = authenticate(username=validated_data['username'], password=validated_data['password'])
#             if not user:
#                 raise ValidationError(f'wrong password for {validated_data["username"]}')
#             return validated_data
#         else:
#             raise ValidationError('username and password are required.')

#     class Meta:
#         model = User
#         fields = ("username", "password", 'url', 'grant_type', 'client_id', 'client_secret')




# class UserAccessTokenSerializer(serializers.ModelSerializer):

#     refresh_token = serializers.CharField(write_only=True)
#     url = serializers.CharField(write_only=True)
#     client_id = serializers.CharField(write_only=True)
#     client_secret = serializers.CharField(write_only=True)

#     def validate(self, validated_data):
#         if validated_data['refresh_token']:
#             try:
#                 refresh_token = RefreshToken.objects.get(token=validated_data['refresh_token'])
#             except:
#                 raise ValidationError({"refresh_token": "the access token dose not exist.", })
#             if refresh_token.revoked:
#                 raise ValidationError({"access_token": "invalid refresh token. the refresh token is expired", })
#             return validated_data
#         else:
#             raise ValidationError({'refresh_token': 'refresh token is required.'})

#     class Meta:
#         model = User
#         fields = ("refresh_token", 'url', 'client_id', 'client_secret')

