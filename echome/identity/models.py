from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser

class Account(models.Model):
    account_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True, null=False)
    secret = models.TextField()
    tags = models.JSONField()

    def __str__(self) -> str:
        return self.account_id


class User(AbstractUser):
    user_id = models.CharField(max_length=20, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=False)
    secret = models.TextField()
    tags = models.JSONField()

    def __str__(self) -> str:
        return self.user_id


class UserAccessAccounts(AbstractBaseUser):
    auth_id = models.CharField(max_length=20, unique=True)
    parent_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=False)
    secret = models.TextField()
    tags = models.JSONField()

    def __str__(self) -> str:
        return self.auth_id


class ServerServiceAccounts(models.Model):
    sa_id = models.CharField(max_length=20, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    owner = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True, null=False)
    active = models.BooleanField(default=True)
    secret = models.TextField()
    tags = models.JSONField()

    def __str__(self) -> str:
        return self.sa_id