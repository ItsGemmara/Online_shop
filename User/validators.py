from django.forms import ValidationError
from django.core.validators import validate_email

from .models import OTP


class OTPValidator():
    def __init__(self, otp_code=None, otp_type=None, user=None):
        self.otp_code = otp_code
        self.user = user

    def otp_validator(self):
        # check that the otp belongs to user and check the otp attempts
        try:
            otp = OTP.objects.get(otp_code=self.otp_code)
            if not otp.user_id == self.user:
                raise ValidationError('Invalid otp code')
        except Exception as e:
            raise ValidationError({'otp_code': 'Invalid otp code'})
        if otp.attempts >= 3:
            raise ValidationError({'otp_code': 'Too many failed attempts for otp.'})
        return self.otp_code
        

class PhoneNumberValidator:

    def __init__(self, phone_number, valid_digits=[920, 921, 922, 910, 911, 912,
                    913, 914, 915, 916, 917, 918, 919, 990, 991, 992, 993, 994,
                    931, 932, 933, 934, '901', '902', '903', '904', '905', 930, 
                    933, 935, 936, 937, 938, 939]):
        self.phone_number = phone_number.strip()
        self.valid_digits = valid_digits

    def phone_number_validator(self):

        if self.phone_number[:3]=='+98':
            self.phone_number = self.phone_number.replace('+98', '0')

        if self.phone_number[:2]=='98':
            self.phone_number = self.phone_number.replace('98', '0')

        if len(self.phone_number) == 10:
           self.phone_number = f'0{self.phone_number}'

        if (len(self.phone_number) != 11) or not self.phone_number[0] == '0' or\
                self.phone_number[1:4] not in str(self.valid_digits):
            raise ValidationError('invalid phone number')
        try:
            int(self.phone_number)
            return self.phone_number
        except:
            raise ValidationError('invalid phone number')

        

def username_type(username):
    try:
        validator = PhoneNumberValidator(phone_number=username)
        validated_username = validator.phone_number_validator()
        type = 'phone_number'
    except:
        validate_email(username)
        validated_username = username
        type = 'email'
    return({'type':type, 'username': validated_username})