from django.shortcuts import render, redirect
from django.db import transaction, connection
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from wiki.models.courses import Course
from wiki.models.history import HistoryItem
from wiki.utils.users import validate_username
from wiki.models.pages import Page,MathjaxCache
from blog.models import BlogPost
from django.http import Http404, HttpResponse
from urls import static_urls
import os
import json
import hashlib
from wiki.utils.profiler import profiler
# welcome is only set to true when called from register()
# Triggers the display of some sort of welcome message

def index(request, show_welcome=False):
	if request.user.is_authenticated():
		page_cache = {}
		course_cache = {}
		user_cache = {}
		user = request.user.get_profile()
		watched_courses = user.courses.all()
		cursor = connection.cursor()
		def parse(row):
			temp_action = HistoryItem()
			temp_action.action = row[0]
			temp_action.timestamp = row[1]
			if row[2] in page_cache:
				temp_action.page = page_cache[row[2]]
			else:
				try:
					temp_action.page = Page.objects.get(pk=row[2])
					page_cache[row[2]] = temp_action.page
				except Page.DoesNotExist:
					temp_action.page = None
			temp_action.message = row[3]
			if row[4] in course_cache:
				temp_action.course = course_cache[row[4]]
			else:
				temp_action.course = Course.objects.get(pk=row[4])
				course_cache[row[4]] = temp_action.course
			return temp_action
		
		
		# First get things done to courses user is watching (exclude self actions)
		cursor.execute('SELECT action,timestamp,page_id,message,course_id,user_id FROM wiki_historyitem \
						WHERE ("wiki_historyitem"."course_id" IN \
						(SELECT U0."id" FROM "wiki_course" U0 INNER JOIN "wiki_userprofile_courses" U1 ON (U0."id" = U1."course_id")\
						 WHERE U1."userprofile_id" = %s ) AND NOT ("wiki_historyitem"."user_id" = %s )) ORDER BY timestamp DESC LIMIT 10'%(user.pk,user.pk))
		history_items = [];
		for row in cursor.fetchall():
			temp_action = parse(row)
			if row[5] in user_cache:
				temp_action.user = user_cache[row[5]]
			else:
				temp_action.user = User.objects.get(pk=row[5])
				user_cache[row[5]] = temp_action.user
			history_items.append(temp_action)
			
			
		# Now get things the user has done
		cursor.execute("SELECT action,timestamp,page_id,message,course_id FROM wiki_historyitem \
						WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10"%user.pk)
		your_actions = [];
		for row in cursor.fetchall():
			your_actions.append(parse(row))
			
			
		try:
			latest_post = BlogPost.objects.order_by('-timestamp')[0]
		except IndexError:
			latest_post = {'title': 'Nothing', 'summary': 'Nothing'}

		# Show the user's dashboard
		data = {
			'watched_courses': watched_courses,
			'your_actions': your_actions,
			'history_items': history_items,
			'show_welcome': show_welcome,
			'latest_post': latest_post
		}
		return render(request, 'main/dashboard.html', data)
	else:
		# Implement this later ... for now just hardcode the course lol
		featured = Course.objects.get(pk=1)
		data = {
			'featured': featured,
		}
		# Show the main page for logged-out users
		return render(request, 'main/index.html', data)

# POSTed to by the login form; should never be accessed by itself
def login_logout(request):
	# Check if the user is already logged in and is trying to log out
	if request.user.is_authenticated():
		if 'logout' in request.POST:
			logout(request)
	else:
		if request.POST['login']:
			try:
				username = User.objects.get(username__iexact=request.POST['username'])
				password = request.POST['password']
				user = authenticate(username=username, password=password)
				if user is not None:
					if user.is_active:
						login(request, user)
				else:
					raise User.DoesNotExist
			except User.DoesNotExist:
				return render(request, 'main/login_error.html')

	# Redirect to the index page etc
	return redirect('/')

# Recent changes
def recent(request, num_days=1, show_all=False):
	data = {
		'history': HistoryItem.objects.get_since_x_days(num_days, show_all),
		'num_days': num_days,
		'base_url': '/recent/all' if show_all else '/recent', # better way of doing this?
		'show_all': show_all
	}
	return render(request, 'main/recent.html', data)

def all_recent(request, num_days=1):
	return recent(request, num_days=num_days, show_all=True)

def profile(request, username):
	this_user = User.objects.get(username__iexact=username)
	data = {
		'this_user': this_user, # can't call it user because the current user is user
		'profile': this_user.get_profile(),
		'recent_activity': HistoryItem.objects.filter(user=this_user),
		'user_pages': Page.objects.filter(historyitem__user=this_user),
	}
	return render(request, 'main/profile.html', data)

def register(request):
	# If the user is already logged in, go to the dashboard page
	if request.user.is_authenticated():
		return index(request)
	else:
		if request.POST and 'register' in request.POST:
			# Make sure everything checks out ...

			errors = []
			username = request.POST['username']
			email = request.POST['email'] # this can be blank. it's okay.
			password = request.POST['password']
			password_confirm = request.POST['password_confirm']
			university = request.POST['university'].lower()

			# Now check all the possible errors
			if university != 'mcgill' and university != 'mcgill university':
				errors.append("Anti-spam question wrong! Please enter the university WikiNotes was made for.")

			if username == '':
				errors.append("You didn't fill in your username!")

			if len(password) < 6:
				errors.append("Your password is too short. Please keep it to at least 6 characters.")

			if password_confirm != password:
				errors.append("Passwords don't match!")

			# First check if the username is valid (might migrate to using the form from django.contrib.auth later)
			# Only allow alphanumeric chars for now, can change later
			if username and not validate_username(username):
				errors.append("Please only use alphanumeric characters and the underscore for your username.")

			# Now check if the username (any case combination) is already being used
			if User.objects.filter(username__iexact=username).count() > 0:
				errors.append("This username is already in use! Please find a new one.")

			data = {
				'errors': errors,
				'username': username,
				'email': email,
				'password': password,
				'university': university # so if there's an unrelated error user doesn't have to enter it again
			}

			if errors:
				return render(request, 'main/registration.html', data)
			else:
				# If the registration proceeded without errors
				# Create the user, then log the user in
				User.objects.create_user(username, email, password)
				new_user = authenticate(username=username, password=password)
				login(request, new_user)
				return index(request, show_welcome=True)
		else:
			return render(request, 'main/registration.html')

def ucp(request, mode):
	# Need a better way of dealing with logged-out users
	modes = ['overview', 'account', 'profile', 'preferences']
	if mode == '' or mode not in modes:
		mode = 'overview'
	if request.user.is_authenticated():
		user = request.user
		user_profile = user.get_profile()
		data = {
			'profile': user_profile,
			'mode': mode,
			'modes': modes,
			'template': 'ucp/' + mode + '.html',
			'success': False,
		}

		# Now check if a request has been submitted
		if request.POST:
			data['success'] = True
			if mode == 'preferences':
				user_profile.show_email = request.POST['show_email'] == '1'
			if mode == 'profile':
				user_profile.bio = request.POST['ucp_bio']
				user_profile.website = request.POST['ucp_website']
				user_profile.twitter = request.POST['ucp_twitter']
				user_profile.github = request.POST['ucp_github']
				user_profile.facebook = request.POST['ucp_facebook']
				user_profile.gplus = request.POST['ucp_gplus']
				user_profile.major = request.POST['ucp_major']
			user_profile.save()

		return render(request, 'main/ucp.html', data)
	else:
		return index(request)

def markdown(request):
	if 'content' in request.POST and 'csrfmiddlewaretoken' in request.POST:
		data = {
			'content': request.POST['content']
		}
		return render(request, 'main/markdown.html', data)
	else:
		raise Http404
	
def mathjaxcache(request):
	if request.POST and 'data' in request.POST and 'csrfmiddlewaretoken' in request.POST:
		cache_objs = json.loads(request.POST['data'])
		with transaction.commit_on_success():
			for obj in cache_objs['objs']:
				eqn_type = obj['t']
				exp = obj['e']
				h = hashlib.sha256()
				h.update("%s-%s" % (eqn_type,exp))
				exp_hash = h.hexdigest()
				caches = MathjaxCache.objects.filter(hash=exp_hash)
				for cache in caches:
					setattr(cache,cache_objs['useragent'],obj['p'])
					cache.save()
		return HttpResponse(":O")
	else:
		print request.POST
		raise Http404
	
def search(request):
	if 'query' in request.GET:
		data = {
			'query': request.GET['query']
		}
		return render(request, 'search/results.html', data)
	else:
		raise Http404

def static(request, mode='', page=''):
	section_pages = ['overview'] + static_urls[mode]
	markdown_file = '%s/%s.md' % (mode, page)
	html_file = '%s/%s.html' % (mode, page)
	data = {
		'html_file': html_file if os.path.isfile('templates/' + html_file) else None,
		'markdown_file': markdown_file if os.path.isfile('templates/' + markdown_file) else None,
		'page': page,
		'mode': mode,
		'section_pages': section_pages,
	}
	return render(request, 'static.html', data)
