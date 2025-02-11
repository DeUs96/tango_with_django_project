from django.shortcuts import render
from rango.models import Page
from rango.models import Category
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime



from django.http import HttpResponse
def index(request):
# Query the database for a list of ALL categories currently stored.
# Order the categories by the number of likes in descending order.
# Retrieve the top 5 only -- or all if less than 5.
# Place the list in our context_dict dictionary (with our boldmessage!)
# that will be passed to the template engine.
  category_list = Category.objects.order_by('-likes')[:5]
  page_list = Page.objects.order_by('-views')[:5]
  context_dict = {}
  context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
  context_dict = {
        'categories': category_list,
          'pages': page_list}
  # Render the response and send it back!
  request.session.set_test_cookie()
  if request.session.test_cookie_worked():
    print("TEST COOKIE WORKED!")
    request.session.delete_test_cookie()
  response = render(request, 'rango/index.html', context=context_dict)
  visitor_cookie_handler(request)
  context_dict['visits'] = request.session['visits']

  return response

def show_category(request, category_name_slug):
# Create a context dictionary which we can pass
# to the template rendering engine.
  context_dict = {}
  try:
  # Can we find a category name slug with the given name?
  # If we can't, the .get() method raises a DoesNotExist exception.
  # The .get() method returns one model instance or raises an exception.
    category = Category.objects.get(slug=category_name_slug)
    # Retrieve all of the associated pages.
    # The filter() will return a list of page objects or an empty list.
    pages = Page.objects.filter(category=category)
    # Adds our results list to the template context under name pages.
    context_dict['pages'] = pages
    # We also add the category object from
    # the database to the context dictionary.
    # We'll use this in the template to verify that the category exists.
    context_dict['category'] = category
  except Category.DoesNotExist:
  # We get here if we didn't find the specified category.
  # Don't do anything -
  # the template will display the "no category" message for us.
    context_dict['category'] = None
    context_dict['pages'] = None
    # Go render the response and return it to the client.
  return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
  form = CategoryForm()
  # A HTTP POST?
  if request.method == 'POST':
    form = CategoryForm(request.POST)
  # Have we been provided with a valid form?
    if form.is_valid():
    # Save the new category to the database.
      form.save(commit=True)
    # Now that the category is saved, we could confirm this.
    # For now, just redirect the user back to the index view.
      return redirect('/rango/')
    else:
      print(form.errors)
  return render(request, 'rango/add_category.html', {'form': form})

def about(request):
    return render(request, 'rango/about.html')

def register(request):
  registered = False
  if request.method == 'POST':
    user_form = UserForm(request.POST)
    profile_form = UserProfileForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid():
      user = user_form.save()
      user.set_password(user.password)
      user.save()
      profile = profile_form.save(commit=False)
      profile.user = user
      if 'picture' in request.FILES:
        profile.picture = request.FILES['picture']
        profile.save()
        registered = True
    else:
      print(user_form.errors, profile_form.errors)
  else:
    user_form = UserForm()
    profile_form = UserProfileForm() 
  return render(request,'rango/register.html',context = {'user_form': user_form,'profile_form': profile_form,'registered': registered})

def user_login(request):
# If the request is a HTTP POST, try to pull out the relevant information.
  if request.method == 'POST':
  # Gather the username and password provided by the user.
  # This information is obtained from the login form.
  # We use request.POST.get('<variable>') as opposed
  # to request.POST['<variable>'], because the
  # request.POST.get('<variable>') returns None if the
  # value does not exist, while request.POST['<variable>']
  # will raise a KeyError exception.
    username = request.POST.get('username')
    password = request.POST.get('password')
  # Use Django's machinery to attempt to see if the username/password
  # combination is valid - a User object is returned if it is.
    user = authenticate(username=username, password=password)
    # If we have a User object, the details are correct.
    # If None (Python's way of representing the absence of a value), no user
    # with matching credentials was found.
    if user:
    # Is the account active? It could have been disabled.
      if user.is_active:
      # If the account is valid and active, we can log the user in.
      # We'll send the user back to the homepage.
        login(request, user)
        return redirect(reverse('rango:index'))
      else:
      # An inactive account was used - no logging in!
        return HttpResponse("Your Rango account is disabled.")
    else:
    # Bad login details were provided. So we can't log the user in.
      print(f"Invalid login details: {username}, {password}")
      return HttpResponse("Invalid login details supplied.")
  else:
  # No context variables to pass to the template system, hence the
  # blank dictionary object...
    return render(request, 'rango/login.html')

@login_required
def restricted(request):
  return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
# Since we know the user is logged in, we can now just log them out.
  logout(request)
  # Take the user back to the homepage.
  return redirect(reverse('rango:index'))

def get_server_side_cookie(request, cookie, default_val=None):
  val = request.session.get(cookie)
  if not val:
    val = default_val
  return val

def visitor_cookie_handler(request):
  visits = int(get_server_side_cookie(request, 'visits', '1'))
  last_visit_cookie = get_server_side_cookie(request,
  'last_visit',
  str(datetime.now()))
  last_visit_time = datetime.strptime(last_visit_cookie[:-7],
  '%Y-%m-%d %H:%M:%S')
  # If it's been more than a day since the last visit...
  if (datetime.now() - last_visit_time).days > 0:
    visits = visits + 1
    # Update the last visit cookie now that we have updated the count
    request.session['last_visit'] = str(datetime.now())
  else:
  # Set the last visit cookie
    request.session['last_visit'] = last_visit_cookie
  # Update/set the visits cookie
  request.session['visits'] = visits








