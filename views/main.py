from django.shortcuts import render, redirect
from django.db import transaction, connection
from django.db import DatabaseError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from wiki.models.courses import Course
from wiki.models.departments import Department
from wiki.models.courses import CourseSemester
from wiki.models.history import HistoryItem
from wiki.utils.users import validate_username
from wiki.models.pages import Page,MathjaxCache
from blog.models import BlogPost
from django.http import Http404, HttpResponse
from urls import static_urls
import os
import json
import hashlib
# welcome is only set to true when called from register()
# Triggers the display of some sort of welcome message

def index(request, show_welcome=False):
	if request.user.is_authenticated():
		page_cache={}
		course_cache={}
		user_cache={}
		user = request.user.get_profile()
		watched_courses = user.courses.all()
		columns = (
		#hardcoding the indices because table lookups are more expensive
		"wiki_historyitem.user_id",#[0]
		"wiki_historyitem.action",#[1]
		"wiki_historyitem.timestamp",#[2]
		"wiki_historyitem.message",#[3]
		"wiki_coursesemester.term",#[4]
		"wiki_coursesemester.year",#[5]
		"wiki_page.slug",#[6]
		"wiki_page.page_type",#[7]
		"wiki_page.title",#[8]
		"wiki_page.subject",#[9]
		"wiki_department.short_name",#[10]
		"wiki_course.number",#[11]
		"wiki_page.id",#[12]
		"wiki_course.id"#[13]
				)
		columns_place_holder = (",".join(["%s"]*len(columns)))
		def parse_result_table(res,get_user):
			#initialize caches
			if not hasattr(parse_result_table,"course_cache"):
				parse_result_table.course_cache = {}
			if not hasattr(parse_result_table,"page_cache"):
				parse_result_table.page_cache = {}
			if not hasattr(parse_result_table,"user_cache"):
				parse_result_table.user_cache = {}
			if not hasattr(parse_result_table,"cs_cache"):#coursesemester
				parse_result_table.cs_cache = {}
				
			items = []
			for row in res:
				item = HistoryItem()
				course = None
				page = None
				if get_user:
					if row[0] in parse_result_table.user_cache:
						item.user = parse_result_table.user_cache[row[0]]
					else:
						item.user = User.objects.get(pk=row[0])
						parse_result_table.user_cache[row[0]] = item.user
				item.action = row[1]
				item.timestamp = row[2]
				item.message = row[3]
				
				#create the course associated with this history
				if row[13] in parse_result_table.course_cache:
					course = parse_result_table.course_cache[row[13]]
				else:
					course = Course()
					department = Department()
					department.short_name = row[10]
					course.department = department
					course.number = row[11]
					parse_result_table.course_cache[row[13]] = course
				item.course = course
				
				#no pages associated with this history, we're done
				if not row[12]:
					items.append(item)
					continue
				
				#get the page associated with this history
				if row[12] in parse_result_table.page_cache:
					page = parse_result_table.page_cache[row[12]]
				else:
					page = Page()
					page.course = course;
					page.page_type = row[7]
					coursesemester = None
					if "%s%s"%(row[4],row[5]) in parse_result_table.cs_cache:
						coursesemester = parse_result_table.cs_cache["%s%s"%(row[4],row[5])]
					else:
						coursesemester = CourseSemester()
						coursesemester.course = course
						coursesemester.term = row[4]
						coursesemester.year = row[5]
						parse_result_table.cs_cache["%s%s"%(row[4],row[5])] = coursesemester
					page.course_sem = coursesemester
					page.title = row[8]
					page.subject = row[9]
					page.slug = row[6]
					parse_result_table.page_cache[row[12]] = page
				item.page = page
				items.append(item)
			return items
		cursor = connection.cursor()
		# First get things done to courses user is watching (exclude self actions)
		cursor.execute(("\
		SELECT "+columns_place_holder+'\
		FROM wiki_historyitem\
		JOIN wiki_course ON wiki_course.id = wiki_historyitem.course_id\
		JOIN wiki_department ON wiki_course.department_id = wiki_department.short_name\
		OUTER LEFT JOIN wiki_page ON wiki_page.id=wiki_historyitem.page_id\
		OUTER LEFT JOIN wiki_coursesemester ON wiki_coursesemester.id=wiki_page.course_sem_id\
		WHERE ("wiki_historyitem"."course_id" IN\
		(SELECT U0."id" FROM "wiki_course" U0 INNER JOIN "wiki_userprofile_courses" U1 ON (U0."id" = U1."course_id")\
		WHERE U1."userprofile_id" = %s ) AND NOT ("wiki_historyitem"."user_id" = %s ))\
		ORDER BY timestamp DESC\
		LIMIT 10')%(columns+(user.pk,user.pk)))
		history_items = parse_result_table(cursor.fetchall(),True);
		# Now get things the user has done
		cursor.execute(("\
		SELECT "+columns_place_holder+"\
		FROM wiki_historyitem\
		JOIN wiki_course ON wiki_course.id = wiki_historyitem.course_id\
		JOIN wiki_department ON wiki_course.department_id = wiki_department.short_name\
		OUTER LEFT JOIN wiki_page ON wiki_page.id=wiki_historyitem.page_id\
		OUTER LEFT JOIN wiki_coursesemester ON wiki_coursesemester.id=wiki_page.course_sem_id\
		WHERE wiki_historyitem.user_id = %s\
		ORDER BY timestamp DESC\
		LIMIT 10")%(columns+(user.pk,)))
		your_actions = parse_result_table(cursor.fetchall(),False)	
		
		# Show the user's dashboard
		data = {
			'watched_courses': watched_courses,
			'your_actions': your_actions,
			'history_items': history_items,
			'show_welcome': show_welcome,
			'latest_post': None
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
