from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import person, group, results, game
from .forms import creategroup
from .templatetags.custom_tags import getvalue
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

#Home--------------------------------------------------------------------------------------------------------

def home(response):
	return render(response, "home_app/home.html", {})

#Groups and Games--------------------------------------------------------------------------------------------

def groups(response):
	if response.user.is_authenticated:
		username = response.user.username
		grp = response.user.group.all()
		sharedgroups = response.user.profile.sharedgroups.all()
	return render(response, "home_app/groups.html", {"sharedgroups": sharedgroups})

def groupview(response, id):
	grp = group.objects.get(id = id)
	users = User.objects.all()

	#Restricting view to only user's groups
	if grp in response.user.group.all() or grp in response.user.profile.sharedgroups.all():
		username = response.user.username

		#Creating a new game within group
		count = 1
		for i in grp.game_set.all():
			count += 1
		if response.method == "POST":
			if response.POST.get("newgame"):
				for person in grp.person_set.all():
					person.points = 0
					person.placing = 1
					person.save()
				gamename = "Game " + str(count)
				newgame = grp.game_set.create(name = gamename)
				return HttpResponseRedirect("/groups/%i/%i" % (grp.id, newgame.id))
			#Deleting Group
			elif response.POST.get("delete"):
				grp.delete()
				return HttpResponseRedirect("/groups")
			#Sharing the group with another user
			elif response.POST.get("share"):
				recipientname = response.POST.get("shareduser")
				if User.objects.filter(username = recipientname).exists() == False:
					messages.error(response, 'User does not exist')
				elif recipientname == username:
					messages.error(response, 'Cannot use your own username')
				else:
					recipient = User.objects.get(username = recipientname)
					recipient.profile.sharedgroups.add(grp)
					recipient.save()
					recipient.profile.save()
					grp.shared = True
					grp.save()
					return render(response, "home_app/groupview.html", {"group": grp, "users": users, "username": username})

		return render(response, "home_app/groupview.html", {"group": grp, "users": users, "username": username})

	return render(response, "home_app/groups.html", {"group": grp})

def game_(response, groupid, gameid):
	grp = group.objects.get(id = groupid)
	gme = grp.game_set.get(id = gameid)

	#Restricting view to only user's items
	if grp in response.user.group.all() or grp in response.user.profile.sharedgroups.all():

		if response.method == "POST":
			if response.POST.get("save"):
				#Checking if points add up to 13
				countpoints = 0
				for person in grp.person_set.all():
					if not response.POST.get("p" + str(person.id)):
						countpoints += 0
					else:
						countpoints += int(response.POST.get("p" + str(person.id)))
				if countpoints != 13:
					messages.error(response, 'Total hearts for players must add up to 13.')
					return HttpResponseRedirect("/groups/%i/%i" % (grp.id, gme.id))
				#Checking if only one queen box is checked
				countqueen = 0
				for person in grp.person_set.all():
					if response.POST.get("c" + str(person.id)) == "clicked":
						countqueen += 1
				if countqueen > 1:
					messages.error(response, 'Only one queen box can be selected')
					return HttpResponseRedirect("/groups/%i/%i" % (grp.id, gme.id))
				elif countqueen < 1:
					messages.error(response, 'A queen box must be selected')
					return HttpResponseRedirect("/groups/%i/%i" % (grp.id, gme.id))
				#Adding points after input is valid
				for person in grp.person_set.all():
					# if response.POST.get("c" + str(person.id)) == "clicked":
					# 	person.points += 13
					# elif response.POST.get("p" + str(person.id)) == "":
					# 	person.points += 0
					# else:
					# 	person.points += int(response.POST.get("p" + str(person.id)))
					# person.save()

					tempstats = 0

					if response.POST.get("p" + str(person.id)) == "":
						person.points += 0
						tempstats = 0
					else:
						person.points += int(response.POST.get("p" + str(person.id)))
						tempstats = int(response.POST.get("p" + str(person.id)))

					if response.POST.get("c" + str(person.id)) == "clicked":
						person.points += 13
						tempstats += 13
						tempstats = str(tempstats) + "q"
					else:
						tempstats = str(tempstats)

					# tempstats += "." + str(grp.id) + "-" + str(gme.id) + ","
					# person.stats += tempstats

					person.save()

					#Ending the game when maxpoints is reached
					for person in grp.person_set.all():
						if person.points >= grp.maxpoints:
							gme.complete = True
							gme.save()
							for person in grp.person_set.all():
								for i in grp.person_set.all():
									if i.id == person.id:
										pass
									elif i.points < person.points:
										person.placing += 1
										person.save()
							#Adding stats to person
							# for person in grp.person_set.all():
							# 	person.stats += str(person.placing) + "." +str(grp.id) + "-" + str(gme.id) + ";"
							# 	person.save()
							#Creating results
							res = results.objects.create(game = gme, groupname = grp.name)
							for i in grp.person_set.all():
								res.stats += str(i.name) + "," + str(i.points) + "," + str(i.placing) + ";"
								res.save()
							return HttpResponseRedirect("/results/%i" %res.id)

			#Future scope
			#Auto end game when points > maxpoints
			#elif response.POST.get("moonshot"):

			#Ending game
			if response.POST.get("endgame"):
				gme.complete = True
				gme.save()
				for person in grp.person_set.all():
					for i in grp.person_set.all():
						if i.id == person.id:
							pass
						elif i.points < person.points:
							person.placing += 1
							person.save()
				#Adding stats to person
				for person in grp.person_set.all():
					person.stats += str(person.placing) + "." + str(grp.id) + "-" + str(gme.id) + ";"
					person.save()
				#Creating results
				res = results.objects.create(game = gme, groupname = grp.name)
				for i in grp.person_set.all():
					res.stats += str(i.name) + "," + str(i.points) + "," + str(i.placing) + ";"
					res.save()
				return HttpResponseRedirect("/results/%i" %res.id)

		return render(response, "home_app/game.html", {"group": grp, "game": gme})

	return render(response, "home_app/groups.html", {"group": grp})

def result(response, resultid):
	res = results.objects.get(id = resultid)
	grp = group.objects.get(name__exact = res.groupname)
	gme = res.game

	#Restricting view to only user's items
	if grp in response.user.group.all() or grp in response.user.profile.sharedgroups.all():

		resdict = {}
		splitbyplayer = res.stats.split(";")
		splitcleaned = [i for i in splitbyplayer if i != ""]
		for i in splitcleaned:
			splitstats = i.split(",")
			resdict[splitstats[0]] = [splitstats[1], splitstats[2]]

		return render(response, "home_app/results.html", {"result":res, "game": gme, "resdict": resdict, "group":grp})

	return render(response, "home_app/groups.html", {"group": grp})

#Statistic Views------------------------------------------------------------------------------------------------------

# def groupstats(response, groupid):
# 	grp = group.objects.get(id = groupid)

# 	if grp in response.user.group.all():
# 		for person in grp.person_set.all():
# 			pstats = person.stats
# 			personstatsclean = pstats.split(";")
# 			personstatsclean = personstatsclean.remove("")




# 	return render(groupstats.html)

# def personstats(response, personid):
# 	return render(personstats.html)

#Create------------------------------------------------------------------------------------------------------

def create(response):
	if response.user.is_authenticated:
		username = response.user.username
	if response.method == "POST":
		if response.POST.get("startgroup"):
			#Group name cannot be blank
			if not response.POST.get("newgroup"):
				messages.error(response, "Group name cannot be blank")
				return render(response, "home_app/create.html", {})
			#No duplicate group names
			if response.user.group.filter(name__exact = response.POST.get("newgroup")).exists():
				messages.error(response, "Group name already used, please choose a new one")
				return render(response, "home_app/create.html", {})
			if int(response.POST.get('maxpoints')) < 13:
				messages.error(response, 'Max points must be 13 or greater')
				return render(response, "home_app/create.html", {})
			n = response.POST.get("newgroup")

			mp = int(response.POST.get("maxpoints"))

			newgroup = group(name=n, maxpoints = mp, user = response.user, owner = response.user)
			newgroup.save()
			return HttpResponseRedirect("/groups/addplayers/%i" %newgroup.id)

	return render(response, "home_app/create.html", {})

def addplayers(response, id):
	grp = group.objects.get(id = id)
	userplayers = response.user.person.all()

	if response.POST.get("addplayer"):
		if not response.POST.get("addplayer"):
			messages.error(response, 'Name cannot be blank.')
			return HttpResponseRedirect("/groups/addplayers/%i" %grp.id)
		else:
			newP = response.POST.get("newplayer")
			if response.user.person.filter(name__exact=newP).exists() == False:
				new = grp.person_set.create(name=newP, points = 0, placing = 1, user = response.user)
				grp.person_set.add(new)
				return render(response, "home_app/addplayers.html", {"group": grp})
			else:
				existing = userplayers.get(name__exact=newP)
				grp.person_set.add(existing)
				return render(response, "home_app/addplayers.html", {"group": grp})
	elif response.POST.get("createGroup"):
		count = 0
		for i in grp.person_set.all():
			count += 1
		if count < 3:
			messages.error(response, 'Group must have at least 3 players.')
			return render(response, "home_app/addplayers.html", {"group": grp})
		else:
			return HttpResponseRedirect("/groups")

	return render(response, "home_app/addplayers.html", {"group": grp, "players": userplayers})

#People------------------------------------------------------------------------------------------------------

def people(response):
	#Checking if user is authenitcated
	if response.user.is_authenticated == True:
		allplayers = []

		for person in response.user.person.all():
			allplayers.append(person)

		if response.POST.get("delete"):
			for i in allplayers:
				if response.POST.get("d" + str(i.id)) == "clicked":
					i.delete()

		return render(response, "home_app/people.html", {})

	return render(response, "home_app/home.html", {})


#----------------------------------------------------------------------------------------------------------------------------------#

#Notes/Archive

# def index(response, id):
# 	#user = person.objects.get(id = id)
# 	#return render(response, "home_app/base.html", {})

# def create(response):
# 	if response.method == "POST":
# 		form = creategroup(response.POST)
# 		if form.is_valid():
# 			n = form.cleaned_data["name"]
# 			mp = form.cleaned_data["maxpoints"]
# 			p = form.cleaned_data["addplayer"]
# 			g = group(name=n, maxpoints = mp)
# 			g.save()

# 		return HttpResponseRedirect("/%i" %g.id)	
# 	else:
# 		form = creategroup()
# 	return render(response, "home_app/create.html", {"form": form})

# <li><a href = "{% url 'results' group.id i.id results.objects.get(name__exact = str(group.id) + str(i.id)) %}">{{i.name}}</a></li>

#Make Dictionary of all games and corresponding results for id retrieval in url
# results = {}
# for game in grp.game_set.all():
# 	results[game.id] = []
# 	for i in results.objects.get(name__exact= (str(grp.id) + str())):
# 		results[game.id].append(i.id)

# resdict = {}
# for i in grp.game_set.all():
# 	resdict[i.name] = results.objects.get(name__exact=str(grp.id)+"_"+str(i.id))


# if response.method == "POST":
# 	if response.POST.get("toGroup"):
# 		return HttpResponseRedirect("/groups/%i" %grp.id)

# 	elif response.POST.get("home"):
# 		return HttpResponseRedirect("/")

# {% if messages %}
# 	<ul class="messages">
# 		{% for message in messages %}
# 			<li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
# 		{% endfor %}
# 	</ul>
# {% endif %}