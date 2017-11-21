from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)


class Quote(models.Model):
    quote = models.CharField(max_length=800)
    author = models.CharField(max_length=50, blank=True)
    from_book = models.CharField(max_length=100, blank=True)
    added_by = models.CharField(max_length=30)

    def __str__(self):
        return self.quote