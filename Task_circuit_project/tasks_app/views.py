from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task, UserProfile
from .forms import RegistrationForm, UniqueKeyForm, LoginForm, TaskForm
from .services.key_generator import generate_random_key

def get_or_create_profile(user):
    """Get or create user profile"""
    try:
        return user.profile
    except:
        import random
        while True:
            key = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            if not UserProfile.objects.filter(unique_key=key).exists():
                break
        profile = UserProfile.objects.create(user=user, unique_key=key)
        return profile

def register_view(request):
    """Registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            request.session['pending_user_id'] = user.id
            request.session['age'] = form.cleaned_data.get('age')
            messages.success(request, f'Welcome {user.first_name}! Now create your unique login key.')
            return redirect('create_key')
    else:
        form = RegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})

def create_key_view(request):
    """Create unique 6-digit key"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, 'Please register first.')
        return redirect('register')
    
    if request.method == 'POST':
        form = UniqueKeyForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            
            profile = UserProfile.objects.create(
                user=user,
                unique_key=form.cleaned_data['unique_key'],
                age=request.session.get('age')
            )
            
            del request.session['pending_user_id']
            if 'age' in request.session:
                del request.session['age']
            
            messages.success(request, f'Your unique key {form.cleaned_data["unique_key"]} has been created! Please login.')
            return redirect('login')
    else:
        form = UniqueKeyForm()
        suggested_key = generate_random_key()
    
    return render(request, 'authentication/create_key.html', {
        'form': form,
        'suggested_key': suggested_key
    })

def login_view(request):
    """Login with unique key"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            unique_key = form.cleaned_data['unique_key']
            try:
                profile = UserProfile.objects.get(unique_key=unique_key)
                login(request, profile.user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome back, {profile.user.first_name}!')
                return redirect('dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Invalid key. Please try again.')
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})

@login_required
def logout_view(request):
    """Logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard_view(request):
    """Dashboard - today's tasks"""
    today = timezone.now().date()
    tasks = Task.objects.filter(user=request.user, scheduled_date=today).order_by('-priority', 'created_at')
    
    # Calculate completed tasks
    completed_count = tasks.filter(completed=True).count()
    
    # Get or create profile
    profile = get_or_create_profile(request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(initial={'scheduled_date': today})
    
    context = {
        'tasks': tasks,
        'form': form,
        'today': today,
        'profile': profile,
        'completed_count': completed_count,
    }
    return render(request, 'tasks_app/home.html', context)

@login_required
def toggle_task_view(request, task_id):
    """Toggle task completion"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if task.completed:
        task.completed = False
        task.completed_at = None
    else:
        task.mark_complete()
    task.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def delete_task_view(request, task_id):
    """Delete task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def history_view(request):
    """Task history by date"""
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    tasks = Task.objects.filter(
        user=request.user,
        scheduled_date=selected_date
    ).order_by('-priority', 'created_at')
    
    # Calculate stats
    total_count = tasks.count()
    completed_count = tasks.filter(completed=True).count()
    pending_count = tasks.filter(completed=False).count()
    
    # Fix completion rate calculation
    if total_count > 0:
        completion_rate = int((completed_count / total_count) * 100)
    else:
        completion_rate = 0
    
    dates_with_tasks = Task.objects.filter(
        user=request.user
    ).values_list('scheduled_date', flat=True).distinct().order_by('-scheduled_date')
    
    # Get or create profile
    profile = get_or_create_profile(request.user)
    
    context = {
        'tasks': tasks,
        'selected_date': selected_date,
        'dates_with_tasks': dates_with_tasks,
        'profile': profile,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'completion_rate': completion_rate,
    }
    return render(request, 'tasks_app/history.html', context)

@login_required
def schedule_view(request):
    """Schedule future tasks"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task scheduled for {task.scheduled_date}!')
            return redirect('schedule')
    else:
        form = TaskForm(initial={'scheduled_date': tomorrow})
    
    upcoming_tasks = Task.objects.filter(
        user=request.user,
        scheduled_date__gt=timezone.now().date()
    ).order_by('scheduled_date', '-priority')
    
    # Get or create profile
    profile = get_or_create_profile(request.user)
    
    context = {
        'form': form,
        'upcoming_tasks': upcoming_tasks,
        'profile': profile,
    }
    return render(request, 'tasks_app/schedule.html', context)

@login_required
def profile_view(request):
    """User profile"""
    profile = get_or_create_profile(request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_theme':
            profile.dark_theme = not profile.dark_theme
            profile.save()
            
            # REFRESH THE PROFILE FROM DATABASE
            profile.refresh_from_db()
            
            # REFRESH THE USER OBJECT TO GET UPDATED PROFILE
            request.user.refresh_from_db()
            
            theme_name = "Dark Mode" if profile.dark_theme else "Light Mode"
            messages.success(request, f'Theme switched to {theme_name}!')
            return redirect('profile')
        
        elif action == 'update_info':
            # Update user info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            age = request.POST.get('age')
            
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()
            
            # Update profile
            if age:
                profile.age = int(age) if age else None
            
            # Handle profile picture update
            if request.FILES.get('profile_picture'):
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    
    # Calculate stats - FIXED
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    pending_tasks = Task.objects.filter(user=request.user, completed=False).count()
    
    # Calculate completion rate - FIXED
    if total_tasks > 0:
        completion_rate = int((completed_tasks / total_tasks) * 100)
    else:
        completion_rate = 0
    
    context = {
        'profile': profile,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': completion_rate,
    }
    return render(request, 'tasks_app/profile.html', context)


def handler404(request, exception):
    return render(request, '404.html', status=404)
