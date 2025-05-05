from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings



# model for gluten exposure
class GlutenExposure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # link to the user model
    date = models.DateField() # date of the reaction
    reaction_count = models.PositiveIntegerField() # number of reactions on that date

    def str(self): 
        return f"{self.user.username} - {self.date} ({self.reaction_count} reactions)" # string representation of the model




class FoodLog(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, default='breakfast')
    food_name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField()
    fat = models.PositiveIntegerField()
    gluten_free = models.BooleanField(default=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.food_name} ({self.meal_type}) - {self.user.username}"




class FavouriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)  
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="comments")  # link to your recipe model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"



class ViewedMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} viewed {self.recipe.name}"



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  

    def __str__(self):  
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, related_name="recipes", blank=True)
    description = models.TextField()
    calories = models.IntegerField()
    image = models.ImageField(upload_to='recipes_images/', null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    protein = models.IntegerField(null=True, blank=True)
    carbs = models.IntegerField(null=True, blank=True)
    fats = models.IntegerField(null=True, blank=True)
    fibre = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey('Community', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')  # prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"

class Community(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def str(self):
        return self.content[:50]

class HealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default='Unknown')
    last_name = models.CharField(max_length=50, default='Unknown')
    date_of_birth = models.DateField(null=True, blank=True, default='2000-01-01')  
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    height = models.CharField(max_length=10, default='170')  
    weight = models.CharField(max_length=10, default='60')   
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)


    def __str__(self):
        return f"{self.user.username}'s Profile"




@receiver(post_save, sender=User)
def create_health_profile(sender, instance, created, **kwargs): 
    if created:
        HealthProfile.objects.create(
            user=instance,
            date_of_birth='2000-01-01',  # Default values to prevent NULL errors
            height='170',
            weight='60'
        )

@receiver(post_save, sender=User)
def save_health_profile(sender, instance, **kwargs): 
    instance.healthprofile.save()



class Reaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True)
    # … any other fields you need …

    def __str__(self):
        return f"{self.user} – {self.date}"

class DietaryIntake(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    calories = models.IntegerField(default=0)
    carbs    = models.IntegerField(default=0)
    protein  = models.IntegerField(default=0)
    fat      = models.IntegerField(default=0)
    # … any other macros you track …

    def __str__(self):
        return f"{self.user} – {self.date}"
