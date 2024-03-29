from django.db import models
from .validators import empty, isInteger
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class group(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "group", null = True)
	name = models.CharField(max_length = 100, validators=[empty])
	maxpoints = models.IntegerField(default = 50)
	owner = models.CharField(max_length = 100)
	shared = models.BooleanField(default = False)
	stats = models.JSONField()
	rotation = models.JSONField()

	def __str__(self):
		return self.name

class game(models.Model):
	group = models.ForeignKey(group, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	results = models.JSONField()
	# [{player: name, points: point, queens: queen, moonshots: moonshot}, {}...]

	def __str__(self):
		return self.name

class profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	sharedgroups = models.ManyToManyField(group, related_name="sharedUsers")
	# friends: list of all user ids that are friends [{userID: id, username: name}]
	# requests: will be the user id and a message [{userID: id, username: name, message: message}]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile.objects.create(user=instance)


class person(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "person", null = True)
	group = models.ManyToManyField(group)
	name = models.CharField(max_length = 50)
	stats = models.JSONField()

	def __str__(self):
		return self.name


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Notes/Archive

#How data will be added to each person:
	#Game set will have a Charfield of names of players in it stored as text
	#The person will not be a foreign key of game set and vice versa
	#The name of each person will be added to the game set via a dropdown menu with all player names (typing will suggest people that start with that string)
	#Each round will search the player name in the database, and then add the stats to them

# @property
# def returnresult(self):
# 	if results.objects.filter(game = self).exists() == True:
# 		return list(results.objects.filter(game = self))[0]
# 	else:
# 		pass


# @receiver(post_save, sender=User)
# def save_user_profile(post_save, instance, **kwargs):
# 	instance.profile.save()
# 	post_save.connect(create_user_profile, sender='users.CustomUser')