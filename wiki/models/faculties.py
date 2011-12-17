from django.db import models

class Faculty(models.Model):
	class Meta:
		app_label = 'wiki'

	# Ex: "Agricultural and environmental sciences"
	name = models.CharField(max_length=100)
	# For use in URLs. Ex: "agriculture" "dentistry" "music" "medicine" "science" "arts" "continuing" etc
	slug = models.CharField(max_length=15)

	def __unicode__(self):
		return self.name

	def get_url(self):
		return "/faculty/%s" % self.slug

	def get_image(self):
		return "/static/img%s.png" % self.get_url()
