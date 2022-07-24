from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):

    username = models.CharField(
        _("email or phone number"),
        max_length=255,
        unique=True,
        help_text=_(

            "Required. valid email or phone number."
        ),
        error_messages={
            "unique": _("A user with that email or phone number already exists."),
        },
    )
    is_active = models.BooleanField(
        # If the user is deleted, it will be deactivated.
        _("active status"),
        default=True,
    )
    phone_is_verified = models.BooleanField(_("phone number verify status"), default=False,)
    email_is_verified = models.BooleanField(_("email verify status"), default=False,)
    phone_number = models.CharField(_('phone number'), unique=True, max_length=11, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True, blank=True, null=True)
    date_varified = models.DateTimeField(_("date verified"), null=True, blank=True)
    date_deactivated = models.DateTimeField(_("date deactivated"), null=True, blank=True)
    sign_up_type = models.CharField(_("sign up type"),max_length=12)  # phone number or email 

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class OTP(models.Model):

    user_id = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    otp_code = models.IntegerField(_("Otp code"))
    otp_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=True)
    used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)