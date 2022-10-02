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

	def __str__(self):
		return self.name

class profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	sharedgroups = models.ManyToManyField(group, related_name="sharedgroups")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(post_save, instance, **kwargs):
# 	instance.profile.save()
# 	post_save.connect(create_user_profile, sender='users.CustomUser')


class person(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "person", null = True)
	group = models.ManyToManyField(group)
	name = models.CharField(max_length = 50)
	points = models.IntegerField(default=0)
	placing = models.IntegerField(default = 1)
	stats = models.TextField()

	# moonshots, welldones, points, queens, tricks, games, placing

	# {
	# 		"group": [],
	# 		"game": [],
	# 		"placing": [],
	# 		"moonshots": [],
	# 		"welldones": [],
	# 		"points": [],
	# 		"queens": [],
	# 		"rounds": 0,
	# 		"games": 0
	# 		}

	def __str__(self):
		return self.name

class game(models.Model):
	group = models.ForeignKey(group, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	complete = models.BooleanField(default = False)

	def __str__(self):
		return self.name



class results(models.Model):
	game = models.OneToOneField(game, on_delete = models.CASCADE)
	groupname = models.CharField(max_length = 100)
	stats = models.CharField(max_length = 500)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#Notes/Archive

#How data will be added to each person:
	#Game set will have a Charfield of names of players in it stored as text
	#The person will not be a foreign key of game set and vice versa
	#The name of each person will be added to the game set via a dropdown menu with all player names (typing will suggest people that start with that string)
	#Each round will search the player name in the database, and then add the stats to them

#def finishround(self, stats, gs, ga, pl, mo, wd, po, q):
		#if bool(self.stats) == False:
		#	self.stats.update({"gameset": []})
		#	self.stats.update({"game": []})
		#	self.stats.update({"placing": []})
		#	self.stats.update({"moonshots": []})
		#	self.stats.update({"welldones": []})
		#	self.stats.update({"points": []})
		#	self.stats.update({"queens": []})
		#	self.stats.update({"rounds": 0})
		#else:
		#	self.stats["gameset"].append(gs)
		#	self.stats["game"].append(ga)
		#	self.stats["placing"].append(pl)
		#	self.stats["moonshots"].append(mo)
		#	self.stats["welldones"].append(wd)
		#	self.stats["points"].append(po)
		#	self.stats["queens"].append(q)
		#	self.stats["rounds"] += 1


# class player(models.Model):
# 	group = models.ForeignKey(group, on_delete = models.CASCADE)
# 	name = models.CharField(max_length = 50)
# 	points = models.IntegerField(default=0)
# 	placing = models.IntegerField(default = 1)

# 	def __str__(self):
# 		return self.name

# @property
# def returnresult(self):
# 	if results.objects.filter(game = self).exists() == True:
# 		return list(results.objects.filter(game = self))[0]
# 	else:
# 		pass

# gameresult = property(returnresult)

# def finishround(person, stats, gp, ga, mo, wd, po, q):
# 	person.stats["group"].append(gp)
# 	person.stats["game"].append(ga)
# 	person.stats["placing"].append(0)
# 	person.stats["moonshots"].append(mo)
# 	person.stats["welldones"].append(wd)
# 	person.stats["points"].append(po)
# 	person.stats["queens"].append(q)
# 	person.stats["rounds"] += 1
# 	person.stats["games"] += 0

# def finishgame(person, gp, pl):
# 	person.stats["group"].append(gp)
# 	person.stats["game"].append("NA")
# 	person.stats["placing"].append(pl)
# 	person.stats["moonshots"].append("NA")
# 	person.stats["welldones"].append("NA")
# 	person.stats["points"].append("NA")
# 	person.stats["queens"].append("NA")
# 	person.stats["rounds"] += 0
# 	person.stats["games"] += 1