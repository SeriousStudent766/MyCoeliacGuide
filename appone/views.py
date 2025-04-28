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
from .models import Recipe, Category
from . import views
from .models import Comment, ViewedMeal
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




@login_required
def glutenExposure(request):
    if request.method == 'POST' and 'delete_id' in request.POST:
        delete_id = request.POST.get('delete_id')
        GlutenExposure.objects.filter(id=delete_id, user=request.user).delete()
        return redirect('glutenExposure')

# check if the request is a POST request to add a new exposure
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

    exposures = GlutenExposure.objects.filter(user=request.user).order_by('date')

   
    grouped_by_year = defaultdict(lambda: defaultdict(int))
    for exposure in exposures:
        year = exposure.date.year
        month = exposure.date.strftime('%B')
        grouped_by_year[year][month] += exposure.reaction_count

    # Prepare sorted chart data
    import calendar
    month_order = list(calendar.month_name)[1:]
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




















user = User.objects.first()
FoodLog.objects.create(
    user=user,
    date=date.today() - timedelta(days=1),
    meal_type='lunch',
    food_name='Test Meal',
    calories=300,
    carbs=20,
    protein=15,
    fat=10,
    gluten_free=True
)





def dietary_history(request):
    # Get range from GET parameters
    day_range = int(request.GET.get("range", 1))
    start_date = date.today() - timedelta(days=day_range)

    logs = (
        FoodLog.objects
        .filter(user=request.user, date__gte=start_date)
        .order_by("-date")
    )

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








def dietary_intake(request):
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










# Create your views here.

def index(request): # Home page view
    return render(request, 'index.html')

def MyGuideHome(request): # MyGuideHome page view
    return render(request, 'MyGuideHome.html')

def aboutus(request):
    return render(request, 'aboutus.html')




@login_required
def community(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'recent')

    all_community = Community.objects.filter(parent__isnull=True)

    if query:
        all_community = all_community.filter(content__icontains=query)

    if sort == 'oldest':
        all_community = all_community.order_by('created_at')
    elif sort == 'most_liked':
        all_community = all_community.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    else:  # default to recent
        all_community = all_community.order_by('-created_at')

    # Handle new posts and replies
    if request.method == 'POST':
        user_community = request.POST.get('community')
        parent_id = request.POST.get('parent_id')
        parent = Community.objects.filter(id=parent_id).first() if parent_id else None

        if user_community:
            Community.objects.create(content=user_community, user=request.user, parent=parent)
            return redirect('community')

    return render(request, 'community.html', {
        'community': all_community,
        'query': query,
        'sort': sort,
    })



@login_required
def health_profile(request):
    profile, created = HealthProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = HealthProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('health_profile')
    else:
        form = HealthProfileForm(instance=profile)

    return render(request, 'health_profile.html', {'form': form, 'profile': profile})















def recipe_page(request):
    form = RecipeFilter(request.GET or None)
    recipes = Recipe.objects.all()

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

    # DEBUGGING LINE — see if it's working
    print("Recipes showing:", recipes.count())

    return render(request, 'recipes.html', {'form': form, 'meals': recipes})



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

    return render(request, 'recipe_detail.html', {
        'meal': recipe,
        'comments': comments
    })











