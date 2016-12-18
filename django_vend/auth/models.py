from django.db import models
from django.conf import settings


class VendRetailer(models.Model):
    name = models.CharField(unique=True, max_length=256)
    access_token = models.CharField(max_length=256)
    expires = models.DateTimeField()
    expires_in = models.IntegerField()
    refresh_token = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class VendUser(models.Model):
    ADMIN = 'A'
    MANAGER = 'M'
    CASHIER = 'C'
    ACCOUNT_TYPE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL)
    uid = models.UUIDField(editable=False)
    retailer = models.ForeignKey(VendRetailer, editable=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256)
    image = models.URLField(blank=True)
    account_type = models.CharField(
        max_length=1,
        choices=ACCOUNT_TYPE_CHOICES,
        default=CASHIER,
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.name
