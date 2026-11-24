import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models

class AgeBasedQuestion(models.Model):
    age_group = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=50) 
    words = models.TextField()

    def __str__(self):
        return f'{self.age_group} - {self.difficulty}'

class User(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),  
        ('approved', 'Approved'),
        ('blocked', 'Blocked'),  
    ]

    id = models.AutoField(primary_key=True) 
    email = models.EmailField(max_length=255, unique=True)  
    image = models.ImageField(upload_to='static/images/', null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=1000, default='')
    date_joined = models.DateTimeField(auto_now_add=True) 
    phone_number = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    status = models.CharField(max_length=1000)
    age = models.PositiveIntegerField() 

class WordRecallResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age_group = models.CharField(max_length=50)
    recalled_words = models.TextField()
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('Completed', 'Completed'), ('Incomplete', 'Incomplete')], default='Incomplete')
    date_attempted = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(default=0) 



class TestImage(models.Model):
    fluency_image = models.ImageField(upload_to='static/fluency_image/', null=True, blank=True)
    tags = models.TextField(help_text="Enter tags (comma-separated), e.g., dog, cat, tree.")
    category = models.CharField(max_length=100)

    def get_tags(self):
        return [tag.strip() for tag in self.tags.split(',')]


class FluencyTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_image = models.ForeignKey(TestImage, on_delete=models.CASCADE)
    date_attempted = models.DateTimeField(auto_now_add=True)
    correct_answers = models.IntegerField()
    wrong_answers = models.IntegerField()
    score = models.FloatField()

class NumberMemoryConfig(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    name = models.CharField(max_length=100, help_text="e.g., Level 1 - 3x3")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    grid_size = models.IntegerField(default=3)               
    number_range_start = models.IntegerField(default=1)
    number_range_end = models.IntegerField(default=9)        
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.difficulty})"    

class NumberMemoryResult(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    grid = models.JSONField()                 
    click_history = models.JSONField()        
    correct_clicks = models.IntegerField()
    mistakes = models.IntegerField()
    time_taken = models.IntegerField(default=0)
    date_attempted = models.DateTimeField(auto_now_add=True)
    config = models.ForeignKey(NumberMemoryConfig, on_delete=models.SET_NULL, null=True)
    score = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.correct_clicks}/9"
    