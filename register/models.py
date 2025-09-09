from sys import prefix
from django.db import models
import uuid
from django.template.defaultfilters import length
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import User
from django.db.models.signals import post_save

TRANSACTION_TYPE = (
    ('payment', 'Payment'),
    ('request', 'Request'),
    ('request_acc', 'Request Accepted'),
    ('request_rej', 'Request Rejected'),
    ('request_proc', 'Request Pending'),
    ('received', 'Received'),
    ('none', 'None'))

ACCOUNT_STATUS = (('active', 'Active'), ('in-active', 'In-active'))

CURRENCY = (('GB', 'British Pounds'), ('Dollar', 'US Dollars'), ('Euro', 'European Euros'))

def user_directory_path(instance, filename):
    ext = filename.split(".")[-1] # Splits the .extensions
    filename = "%s_%s" % (instance.id, ext)
    return "user_{0}/{1}".format(instance.user.id, filename)

# Account & User Detail Models

# For all accounts, these are the field requirements
# When a user signs up, their account will automatically be filled with these requirements
class Account(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False) # Must be unique and un-editable
    user = models.OneToOneField(User, on_delete=models.CASCADE) # When deleted, cascades so it doesn't affect other users
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=750.00)
    account_id = ShortUUIDField(unique=True, length=7, max_length=20, prefix="VG", alphabet="1234567890")
    account_pin = ShortUUIDField(length=4, max_length=7, alphabet="1234567890")
    account_status = models.CharField(max_length=100, choices=ACCOUNT_STATUS, default="active")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.user}"

# What the user can upload and edit in their account
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    currency = models.CharField(choices=CURRENCY, max_length=100)
    date_of_birth = models.DateField(auto_now_add=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

# Using Django signals, make an account when user creates one
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

# Using Django signals, update account when user saves their account data
def update_account(sender, instance, **kwargs):
    instance.account.save()

post_save.connect(create_account, sender=User)
post_save.connect(update_account, sender=User)

# Transaction Models

# When a user sends a payment
class Transaction(models.Model):
    transaction_id = ShortUUIDField(unique=True, length=10, max_length=15, prefix="TR-", alphabet='abcdef1234567890')

    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_TYPE, default="none")
    #currency = models.CharField(choices=CURRENCY, max_length=100, default="GB")

    user = models.ForeignKey(User, related_name="user", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.SET_NULL, null=True)
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.SET_NULL, null=True)
    receiver_account = models.ForeignKey(Account, related_name="receiver_account", on_delete=models.SET_NULL, null=True)
    sender_account = models.ForeignKey(Account, related_name="sender_account", on_delete=models.SET_NULL, null=True)

    transaction_created_date = models.DateTimeField(auto_now_add=True)
    transaction_updated_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    def __str__(self):
        try:
            return f"{self.user}"
        except:
            return f"Transaction"

