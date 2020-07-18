from django.db import models


class Company(models.Model):
    # Company name
    name = models.CharField(max_length=200, unique=True)
    # Company name without well-known prefixes
    cleaned_name = models.CharField(max_length=200)
