from django.db import models
from django.contrib.auth.models import User
from django.db.models import CharField
from django.core.validators import MinValueValidator, MaxValueValidator



# Create your models here.
class UserProfile(models.Model):
    USER = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    organisation = models.CharField(max_length=100)


class ContractUpload(models.Model):
    USER = models.ForeignKey(User,on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='uploads/')
    date = models.CharField(max_length=20)

class Complaint(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint_text = models.TextField(max_length=1000)
    reply = models.TextField(max_length=1000)
    date = models.CharField(max_length=20)

class Feedback(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField(max_length=1000)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    date = models.CharField(max_length=100)
