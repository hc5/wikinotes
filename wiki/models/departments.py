from django.db import models

class Department(models.Model):
	class Meta:
		app_label = 'wiki'

	short_name = models.CharField(max_length=4, primary_key=True)
	long_name = models.CharField(max_length=255)
	faculty = models.ForeignKey('Faculty')

	def __unicode__(self):
		return "Department of %s (%s)" % (self.long_name, self.short_name)

	def get_url(self):
		return "/department/%s" % self.short_name

	def get_image(self):
		return "/static/img%s.png" % self.get_url()
