from django import forms
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from .models import HealthProfile, Category
from django.shortcuts import render, redirect
from .models import Comment
from .models import FoodLog


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image'] # fields to include in the form


#adds an email field to the signup form
class UserSignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] # shows what to include in the signup form
        

class HealthProfileForm(forms.ModelForm):
    class Meta:
        model = HealthProfile # Model for HealthProfile
        fields = [
            'profile_picture',
            'weight',
            'height',
            'date_of_birth',
            'sex',
        ]




class FoodLogForm(forms.ModelForm): # Form for FoodLog
    class Meta:
        model = FoodLog # Model for FoodLog
        fields = ['date', 'meal_type', 'food_name', 'calories', 'carbs', 'protein', 'fat', 'gluten_free']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}), # Date input widget
        }








class RecipeFilter(forms.Form):
    category_choices = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Filter by Categories"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_choices'].queryset = Category.objects.all()
