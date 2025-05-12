from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from  . forms import UserSignUpForm
from django.contrib import messages
from django.db.models import Count
from datetime import datetime
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import HealthProfileForm
from .models import HealthProfile, GlutenExposure
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .forms import RecipeFilter
from .models import Recipe, Category, FavouriteRecipe
from . import views
from .models import ViewedMeal, Comment
from datetime import datetime, date
from django.utils.timesince import timesince
from django.views.decorators.http import require_POST
from collections import defaultdict
from .models import Community, Like
from .models import FoodLog
from django.shortcuts import render, redirect
from .forms import FoodLogForm
from datetime import date
from datetime import date, timedelta
from .models import Reaction, DietaryIntake 
from django.db.models.functions import TruncMonth
from django.db.models import Count, Exists, OuterRef


#home and about us page
def guide_home(request): 
    return render(request, 'guide_home.html')

def index(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'aboutus.html')

#----------------------------------------------------------------------------------------------------------------

# authentication section 

def SignUp(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST) # Creates a form instance with the POST data
        if form.is_valid():
            user = form.save() # Save the new user to the database

            username = form.cleaned_data.get('username') # Get the username from the form data
            
            messages.success(request, f'Hi {username}, your account has been created successfully!')
            #show success message
            return redirect('index')  #sends back to the home page after signup
    else:
        form = UserSignUpForm() # if not a POST request, create an empty form

    return render(request, 'SignUp.html', {'form': form})



 # Logout view
def logout_view(request): 
    logout(request)  # Log out the user
    return redirect('index') #sends back to home page


#end of authentication section

#----------------------------------------------------------------------------------------------------------------

# gluten exposure section

@login_required
def glutenExposure(request):
    if request.method == 'POST' and 'delete_id' in request.POST: # check if the request is a POST request to delete an exposure
        delete_id = request.POST.get('delete_id') # get the id of the exposure to delete
        GlutenExposure.objects.filter(id=delete_id, user=request.user).delete() # delete the exposure 
        return redirect('glutenExposure')

# adds a new exposure 
    elif request.method == 'POST':
        date_input = request.POST.get('date') # get the date from the form
        reaction_count = request.POST.get('reaction_count') # get the reaction count from the form
        if date_input and reaction_count:
            # check if the date and reaction count are provided
            GlutenExposure.objects.create(
                user=request.user,
                date=date_input,
                reaction_count=int(reaction_count)
            )

            return redirect('glutenExposure')
        
    # gets and groups all exposures for the logged-in user
    exposures = GlutenExposure.objects.filter(user=request.user).order_by('date') 
    grouped_by_year = defaultdict(lambda: defaultdict(int)) # group exposures by year and month
    for exposure in exposures:
        year = exposure.date.year
        month = exposure.date.strftime('%B')
        grouped_by_year[year][month] += exposure.reaction_count

    # Prepare sorted chart data
    import calendar 
    month_order = list(calendar.month_name)[1:] # Get month names in order
    chart_data = {}
    for year, months in grouped_by_year.items():
        sorted_months = [m for m in month_order if m in months]
        chart_data[year] = {
            'labels': sorted_months,
            'reaction_counts': [months[m] for m in sorted_months]
        }

    # Send full chart data
    exposure_data = json.dumps(chart_data)

    # Last reaction info
    last_exposure = exposures.last()
    if last_exposure:
        days_since = (date.today() - last_exposure.date).days
        last_date_str = last_exposure.date.strftime('%d/%m/%Y')
        last_reaction_message = f"You last had a reaction {days_since} day(s) ago ({last_date_str})"
    else:
        last_reaction_message = "No reactions logged yet."

    return render(request, 'glutenExposure.html', {
        'exposure_data': exposure_data,
        'last_reaction_message': last_reaction_message,
        'user_first_name': request.user.first_name,
        'exposures': exposures
    })

#end of gluten exposure section
#----------------------------------------------------------------------------------------------------------------

# dietary intake section

def dietary_intake(request):
    #shows the dietary intake page
    logs = FoodLog.objects.filter(user=request.user, date=date.today())
    form = FoodLogForm()
    if request.method == 'POST':
        form = FoodLogForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('dietary_intake')

    totals = {
        'calories': sum(log.calories for log in logs),
        'carbs': sum(log.carbs for log in logs),
        'protein': sum(log.protein for log in logs),
        'fat': sum(log.fat for log in logs),
    }

    context = {
        'form': form,
        'logs': logs,
        'totals': totals,
    }
    return render(request, 'dietary_intake.html', context)



def dietary_history(request):
    # lists the dietary history
    day_range = int(request.GET.get("range", 1))
    start_date = date.today() - timedelta(days=day_range)

    logs = (
        FoodLog.objects
        .filter(user=request.user, date__gte=start_date)
        .order_by("-date")
    )

    # Group logs by date
    grouped = defaultdict(list)
    for log in logs:
        grouped[log.date].append(log)

    # Prepare daily summaries
    day_summaries = []
    for day, day_logs in grouped.items():
        summary = {
            "date": day,
            "logs": day_logs,
            "total_calories": sum(log.calories for log in day_logs),
            "total_carbs": sum(log.carbs for log in day_logs),
            "total_protein": sum(log.protein for log in day_logs),
            "total_fat": sum(log.fat for log in day_logs),
        }
        day_summaries.append(summary)

    context = {
        "dates": sorted(day_summaries, key=lambda x: x["date"], reverse=True),
        "range": str(day_range)
    }
    return render(request, "dietary_history.html", context)

def view_day_logs(request, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return render(request, 'error.html', {'message': 'Invalid date format.'})

    logs = FoodLog.objects.filter(user=request.user, date=date_obj)

    totals = {
        'calories': sum(log.calories for log in logs),
        'carbs': sum(log.carbs for log in logs),
        'protein': sum(log.protein for log in logs),
        'fat': sum(log.fat for log in logs),
    }

    context = {
        'logs': logs,
        'date': date_obj,
        'totals': totals
    }

    return render(request, 'view_day_logs.html', context)



from .models import (
    Community, Like, HealthProfile, Recipe,
    ViewedMeal, FavouriteRecipe,
    GlutenExposure, Reaction, DietaryIntake, FoodLog
)
from .forms  import HealthProfileForm, RecipeFilter, FoodLogForm, UserSignUpForm

def view_day_logs(request, date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return render(request, 'error.html', {'message': 'Invalid date format.'})

    logs = FoodLog.objects.filter(user=request.user, date=date_obj)
    totals = {
        'calories': sum(l.calories for l in logs),
        'carbs':     sum(l.carbs     for l in logs),
        'protein':   sum(l.protein   for l in logs),
        'fat':       sum(l.fat       for l in logs),
    }

    return render(request, 'view_day_logs.html', {
        'logs':   logs,
        'date':   date_obj,
        'totals': totals,
    })


#end of dietary intake section

#----------------------------------------------------------------------------------------------------------------

# community section

@login_required
def community(request):
    query = request.GET.get('q', '')
    sort  = request.GET.get('sort', 'recent')

    # Base threads
    qs = Community.objects.filter(parent__isnull=True)
    if query:
        qs = qs.filter(content__icontains=query)

    # Annotate counts & whether current user liked
    user_like_qs = Like.objects.filter(user=request.user, comment=OuterRef('pk'))
    qs = qs.annotate(
        like_count=Count('likes', distinct=True),
        is_liked  =Exists(user_like_qs),
    )

    # Sort
    if sort == 'oldest':
        qs = qs.order_by('created_at')
    elif sort == 'most_liked':
        qs = qs.order_by('-like_count', '-created_at')
    else:
        qs = qs.order_by('-created_at')

    if request.method == 'POST':
        like_id   = request.POST.get('like_id')
        if like_id:
            thread = get_object_or_404(Community, id=like_id)
            existing = Like.objects.filter(user=request.user, comment=thread).first()
            if existing:
                existing.delete()
            else:
                Like.objects.create(user=request.user, comment=thread)
            return redirect('community')

        # Handle new post or reply with image
        body      = request.POST.get('community')
        parent_id = request.POST.get('parent_id')
        image     = request.FILES.get('image')  
        parent    = Community.objects.filter(id=parent_id).first() if parent_id else None

        if body or image:
            Community.objects.create(
                content=body,
                user=request.user,
                parent=parent,
                image=image 
            )
        return redirect('community')


        # Otherwise: new thread or reply
        body      = request.POST.get('community')
        parent_id = request.POST.get('parent_id')
        parent    = Community.objects.filter(id=parent_id).first() if parent_id else None
        if body:
            Community.objects.create(content=body, user=request.user, parent=parent)
        return redirect('community')

    return render(request, 'community.html', {
        'community': qs,
        'query':     query,
        'sort':      sort,
    })


#end of community section

#----------------------------------------------------------------------------------------------------------------

# health profile section


def health_profile(request):
    # grab the one‐to‐one that always exists
    profile = request.user.healthprofile

    if request.method == 'POST':
        form = HealthProfileForm(
            request.POST,
            request.FILES,      # for image upload
            instance=profile
        )
        if form.is_valid():
            form.save()
            return redirect('health_profile')
    else:
        form = HealthProfileForm(instance=profile)

    return render(request, 'health_profile.html', {
        'profile': profile,
        'form': form
    })

#end of health profile section

#----------------------------------------------------------------------------------------------------------------



# recipe section

def recipe_page(request):
    form = RecipeFilter(request.GET or None) # Create a form instance with GET data
    recipes = Recipe.objects.all() # Get all recipes

# Filter by categories if selected
    if form.is_valid():
        selected_categories = form.cleaned_data.get('category_choices')
        if selected_categories:
            print("Selected:", selected_categories)
            recipes = recipes.filter(categories__in=selected_categories).distinct()
    else:
        print("No categories selected.")

    # Do sorting even if no filter
    sort_by = request.GET.get('sort_by')
    if sort_by == 'calories':
        recipes = recipes.order_by('calories')
    elif sort_by == 'protein':
        recipes = recipes.order_by('-protein')
    elif sort_by == 'fibre':
        recipes = recipes.order_by('-fibre')
    elif sort_by == 'low_fat':
        recipes = recipes.order_by('fats')
    elif sort_by == 'low_carbs':
        recipes = recipes.order_by('carbs')

        fav_ids = []
    if request.user.is_authenticated: # check if user is logged in
        fav_qs    = FavouriteRecipe.objects.filter(user=request.user)
        fav_ids   = fav_qs.values_list('recipe_id', flat=True)
        fav_count = fav_qs.count()
    else:
        fav_ids   = []
        fav_count = 0

    return render(request, 'recipes.html', {
        'form':       form,
        'meals':      recipes,
        'fav_ids':    set(fav_ids),
        'fav_count':  fav_count,
    })





@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                content=content,
                user=request.user,
                recipe=recipe
            )
            return redirect('recipe_detail', recipe_id=recipe_id)

    comments = Comment.objects.filter(recipe=recipe, parent__isnull=True).order_by('-created_at')

    viewed_meal, created = ViewedMeal.objects.get_or_create(user=request.user, recipe=recipe)
    if not created:
        viewed_meal.viewed_at = now()
        viewed_meal.save()
        

        recipes = Recipe.objects.all()  # or filtered

    if request.user.is_authenticated:
        fav_ids = set(
            FavouriteRecipe.objects
                           .filter(user=request.user)
                           .values_list('recipe_id', flat=True)
        )
    else:
        fav_ids = set()

    return render(request, 'recipe_detail.html', { 
        'recipe': recipe,
        'comments': comments,   
        'fav_ids': fav_ids,
    })





@login_required
def toggle_favorite(request, recipe_id): # toggle favorite 
    from .models import FavouriteRecipe, Recipe

    recipe = get_object_or_404(Recipe, pk=recipe_id) # get the recipe
    fav, created = FavouriteRecipe.objects.get_or_create( # get or create a favorite
        user=request.user,
        recipe=recipe
    )
    if not created:
        # already existed → unfavorite
        fav.delete()
    return redirect(request.META.get('HTTP_REFERER','/')) # redirect to the previous page





@login_required
def favorites_list(request):
    # gets all favorite recipes for user
    fav_qs   = FavouriteRecipe.objects.filter(user=request.user).select_related('recipe') # prefetch related recipes
    # get the recipe objects
    recipes  = [fav.recipe for fav in fav_qs]
    return render(request, 'favorites_list.html', { 
        'meals': recipes,
        'fav_count': fav_qs.count(),
    })



#end of recipe section
