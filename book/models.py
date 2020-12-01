from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=30, blank=True)
    publication_date = models.DateField(null=True)
    pages = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=255, decimal_places=2)

    def __str__(self):
        return self.title
