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



# model for food log
class FoodLog(models.Model): 
    MEAL_CHOICES = [ # choices for meal types
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, default='breakfast') # meal type
    food_name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField()
    fat = models.PositiveIntegerField()
    gluten_free = models.BooleanField(default=True)
    date = models.DateField() # date of the meal

    def __str__(self): # show the food name and meal type in the admin panel
        return f"{self.food_name} ({self.meal_type}) - {self.user.username}"




class FavouriteRecipe(models.Model): # model for favourite recipes
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)  
    added_at = models.DateTimeField(auto_now_add=True) # timestamp of favoriting

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"



class Comment(models.Model): # model for comments
    content = models.TextField() # content of the comment
    image = models.ImageField(upload_to='comment_images/', null=True, blank=True)
    # user can optionally attach an image
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE) # to allow replies to comments
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}" #to show the first 30 characters of the comment in the admin panel






class Community(models.Model):
    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     null=True, blank=True, 
                     on_delete=models.CASCADE 
                 ) 
    content    = models.TextField()
    image      = models.ImageField(
                     upload_to='community_images/',
                     blank=True, null=True
                 )
    created_at = models.DateTimeField(auto_now_add=True)
    parent     = models.ForeignKey(
                     'self', null=True, blank=True,
                     related_name='replies',
                     on_delete=models.CASCADE
                 )# nesting for replies

    def __str__(self):
        preview = (self.content[:27] + '...') if len(self.content) > 30 else self.content # to show the first 30 characters of the comment
        username = self.user.username if self.user else 'Anonymous' # to show the username if available
        return f"{username}: {preview}" 



# shows when a user views a recipe
class ViewedMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True) #update the timestamp when viewed

    def __str__(self):
        return f"{self.user.username} viewed {self.recipe.name}"


#for filtering recipes by category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  

    def __str__(self):  
        return self.name

#stores the recipes
class Recipe(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, related_name="recipes", blank=True)   # multiple categories per recipe
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

    

    
# likes for comments
class Like(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    comment    = models.ForeignKey(
                     Community,
                     on_delete=models.CASCADE,
                     related_name='likes'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment') # to ensure a user can only like a comment once

    def __str__(self):
        return f"{self.user.username} liked thread {self.comment.id}"








#details of the user
class HealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default=' ')
    last_name = models.CharField(max_length=50, default=' ')
    date_of_birth = models.DateField(null=True, blank=True, default=' ')  
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default=' ')
    height = models.CharField(max_length=10, default=' ')  
    weight = models.CharField(max_length=10, default=' ')   
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)


    def __str__(self):
        return f"{self.user.username}'s Profile"



#autpmatically create a health profile 
@receiver(post_save, sender=User)
def create_health_profile(sender, instance, created, **kwargs): 
    if created:
        HealthProfile.objects.create(
            user=instance,
            date_of_birth='2000-01-01',  
            height='0',
            weight='0'
        )

@receiver(post_save, sender=User)
def save_health_profile(sender, instance, **kwargs):  #make sure to save the health profile
    instance.healthprofile.save()


# model for reactions to gluten exposure
class Reaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True)
   

    def __str__(self):
        return f"{self.user} – {self.date}"
    
    
# model for dietary intake
class DietaryIntake(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # link to the user model
    date = models.DateField()
    calories = models.IntegerField(default=0)
    carbs    = models.IntegerField(default=0)
    protein  = models.IntegerField(default=0)
    fat      = models.IntegerField(default=0)
   

    def __str__(self):
        return f"{self.user} – {self.date}"