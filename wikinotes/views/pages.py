from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User as RealUser
from wikinotes.models.pages import Page
from wikinotes.models.courses import Course
from django.template import TemplateDoesNotExist

def create(request, department, number, page_type):
	text = "lol"
	this_course = get_object_or_404(Course, department=department, number=int(number))
	
	# If the template specified by the page type exists, then we're good to go
	# Else, 404
	section_title = this_course
	try:
		return render_to_response('page/create-%s.html' % page_type, locals())
	except TemplateDoesNotExist:
		raise Http404
