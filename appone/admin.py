from django.contrib import admin
from .models import Community, HealthProfile, GlutenExposure, Recipe, Category, FavouriteRecipe, FoodLog 

#All fields are displayed in the admin panel

@admin.register(FoodLog)  
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_type', 'food_name', 'calories', 'carbs', 'protein', 'fat', 'gluten_free') # Show relevant fields in the list
    search_fields = ('food_name', 'user__username')
    list_filter = ('meal_type', 'date', 'gluten_free')



@admin.register(Community) 
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'created_at', 'parent') # Show relevant fields in the list
    search_fields = ('content', 'user__username')
    list_filter = ('created_at',)


@admin.register(HealthProfile) # Register the model
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'date_of_birth', 'sex', 'height', 'weight')
    search_fields = ('user__username', 'first_name', 'last_name')


@admin.register(GlutenExposure) # Register the model
class GlutenExposureAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'reaction_count')


@admin.register(Recipe)  # Register the model
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories')
    list_filter = ('categories',)
    search_fields = ('name', 'description')
    filter_horizontal = ('categories',) 


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)       # Show category name in the list
    search_fields = ('name',)      # Add search by name field

@admin.register(FavouriteRecipe)
class FavouriteRecipeAdmin(admin.ModelAdmin): 
    list_display = ('user', 'recipe', 'added_at') # Show user and recipe in the list
    search_fields = ('user__username', 'recipe__name') # Add search by user and recipe fields
