from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.views import generic
from django.contrib import messages

from jazzmin.templatetags.jazzmin import User
from django.contrib.auth.models import User

from payapp.forms import RegisterForm, CommentForm
from register.models import Account, Comment

def index(request):
    return render(request, "user/index.html")

def about(request):
    return render(request, "user/about.html")

def contact_us(request):
    return render(request, "user/contact-us.html")

# Goes to sign-up page, authenticates, and receives user inputs
def register_user(request):
    # When the user input is read
    if request.method == "POST":
        form = RegisterForm(request.POST)
        # If all the user input is correct
        if form.is_valid():
            # Grabs user input into this variable and returns to homepage
            new_user = form.save()
            username = form.cleaned_data.get("username")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            full_name = first_name + " " + last_name
            messages.success(request, f"Welcome to VG Bank, {full_name}. Account created successfully!")
            messages.success(request, f"Your username is {username}!")

            new_user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            login(request, new_user)
            return redirect("index")
    elif request.user.is_authenticated:
        # If a user is already registered, return to homepage again
        messages.warning(request, "You are already logged in!")
        return redirect("index")
    else:
        form = RegisterForm()

    context = {"form": form}
    return render(request, "register/sign-up.html", context)

# Goes to login page, authenticates, and receives user inputs
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            # Authenticating user inputs
            user = User.objects.get(username=username)
            user = authenticate(request, username=user.username, password=password)

            # Checking if user details are in the database
            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in!")
                return redirect("index")
            else:
                messages.warning(request, "Invalid username or password.")
                return redirect("login")
        except:
            messages.error(request, "User does not exist.")
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("index")
    return render(request, "register/login.html")

# Goes to log out page, can be redirected to guest dashboard or back to log in
def logout_view(request):
    logout(request)
    messages.success(request, "You are now logged out!")
    return render(request, "register/logout.html")

# Goes to edit account details
# Must be logged in to "activate" the security url on settings.py and go to the page successfully
@login_required
def edit_user_detail_view(request):
    user = request.user
    account = Account.objects.get(user=user)
    try:
        comment = Comment.objects.get(user=user)
    except:
        comment = None

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            # Inputs from this form are saved but not commited to database (yet)
            new_form = form.save(commit=False)
            # Because some fields are null fields and has to be specified like this
            new_form.user = user
            new_form.account = account
            # Now, we save
            new_form.save()
            messages.success(request, "Your user details have been updated successfully!.")
            return redirect("index")
    else:
        form = CommentForm(instance=comment)

    context = {"form": form, "account": account}
    return render(request, "user/edit-account-details.html", context)

# Goes to view account (both Comment and Account variables must be shown)
# Must be logged in to "activate" the security url on settings.py and go to the page successfully
#@login_required
def account_view(request):
    # This if/else statement can be replaced with login_required but this way shows an error message
    # The other way will take users to yellow error page
    if request.user.is_authenticated:
        comment = Comment.objects.get(user=request.user)
        account = Account.objects.get(user=request.user)
    else:
        messages.warning(request, "You are not logged in!")
        return redirect("login")

    context = {"comment": comment, "account": account}
    return render(request, "user/view-account.html", context)

def dashboard(request):
    if request.user.is_authenticated:
        comment = Comment.objects.get(user=request.user)
        account = Account.objects.get(user=request.user)
    else:
        messages.warning(request, "You are not logged in!")
        return redirect("login")

    context = {"comment": comment, "account": account}
    return render(request, "user/dashboard.html", context)

