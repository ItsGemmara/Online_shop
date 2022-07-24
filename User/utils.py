import random
from django.core.exceptions import ValidationError
from .models import OTP


def create_otp(user, otp_type):
    try:
        previous_active_otps = OTP.objects.filter(used=False, user_id=user, otp_type=otp_type)
        for otp in previous_active_otps:
            otp.used = True
            otp.save()
    except:
        raise ValidationError('Something wrong with deactivate otpies.')
    try:
        otp_code = random.randint(10000,99999)
        new_otp = OTP.objects.create(otp_type=otp_type, user_id=user, otp_code=otp_code)
    except:
        raise ValidationError('Something wrong with create new OTP.')
    return new_otp

