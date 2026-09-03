from django.db import models
from django.contrib.auth.models import User


class EmployeeProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )

    name = models.CharField(
        max_length=100,
        default=""
    )

    phone = models.CharField(
        max_length=10
    )

    city = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.user.username


class Attendance(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    punch_in = models.DateTimeField(
        null=True,
        blank=True
    )

    punch_out = models.DateTimeField(
        null=True,
        blank=True
    )

    date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.date}"