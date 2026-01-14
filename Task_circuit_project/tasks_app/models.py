from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    unique_key = models.CharField(max_length=6, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    date_of_register = models.DateTimeField(auto_now_add=True)
    dark_theme = models.BooleanField(default=True) 
    
    def __str__(self):
        return f"{self.user.username} - {self.unique_key}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    scheduled_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        
    def __str__(self):
        return f"{self.title} ({self.scheduled_date})"
    
    def mark_complete(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()
