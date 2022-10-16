from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import person, group, game
from .forms import creategroup
from .templatetags.custom_tags import getvalue
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.models import User
import json, statistics

#Home---------------------------------------------------------------------------------------------------------------------------------------

def home(request):
	return render(request, "home_app/home.html", {})

#Groups and Games---------------------------------------------------------------------------------------------------------------------------

def groups(request):
	if request.user.is_authenticated:
		username = request.user.username
		grp = request.user.group.all()
		groups = []
		for group in grp:
			count = len(group.game_set.all())
			groups.append({"data": group, "count": count})
		sharedgroups = request.user.profile.sharedgroups.all() #Groups other users have shared with current user
		groupsShared = list(filter(lambda group: group.shared == True, grp)) #Groups current user has shared with others
		return render(request, "home_app/groups.html", {"sharedgroups": sharedgroups, "groupsShared": groupsShared, "groups": groups})
	return render(request, "home_app/groups.html")

def groupview(request, id):
	grp = group.objects.get(id = id)
	users = User.objects.all()

	#Restricting view to only user's groups
	if grp in request.user.group.all() or grp in request.user.profile.sharedgroups.all():
		username = request.user.username
		user = request.user

		#Creating a new game within group
		count = 1
		for i in grp.game_set.all():
			count += 1

		if request.method == "POST":

			#Deleting Group
			if request.POST.get("delete"):
				grp.delete()
				return HttpResponseRedirect("/groups")
			#Sharing the group with another user
			elif request.POST.get("share"):
				recipientname = request.POST.get("shareduser")
				if User.objects.filter(username = recipientname).exists() == False:
					messages.error(request, 'User does not exist')
				elif recipientname == username:
					messages.error(request, 'Cannot use your own username')
				else:
					recipient = User.objects.get(username = recipientname)
					recipient.profile.sharedgroups.add(grp)
					recipient.save()
					recipient.profile.save()
					grp.shared = True
					grp.save()
					messages.success(request, 'Group shared!')
					return render(request, "home_app/groupview.html", {"group": grp, "users": users, "username": username, "user": user})

		return render(request, "home_app/groupview.html", {"group": grp, "users": users, "username": username, "gameNumber": count})

	return render(request, "home_app/groups.html", {"group": grp})

def game_(request, groupid, gameNumber):
	grp = group.objects.get(id = groupid)
	gameName = "Game " + str(gameNumber)

	#Restricting view to only user's items
	if grp in request.user.group.all() or grp in request.user.profile.sharedgroups.all():
		if request.method == "POST":
			data = request.POST.get("formData")
			formData = json.loads(data)

			newGame = grp.game_set.create(
				name = gameName,
				group = grp,
				results = formData
			)
			gameID = newGame.id

			for player in formData:
				index = next((i for i, p in enumerate(grp.stats) if p["name"] == player["name"]), None)
				grp.stats[index]["hands"].extend(player["hands"])
				grp.stats[index]["placings"].append(player["placing"])
				grp.stats[index]["queens"] += player["queens"]
				grp.stats[index]["moonshots"] += player["moonshots"]
				grp.save()

				person = request.user.person.filter(name__exact = player["name"])[0]
				person.stats["hands"].extend(player["hands"])
				person.stats["placings"].append(player["placing"])
				person.stats["queens"] += player["queens"]
				person.stats["moonshots"] += player["moonshots"]
				person.save()
				print(person.stats["hands"])

			return HttpResponseRedirect("/groups/%i/results/%i" % (grp.id, gameID))

		return render(request, "home_app/game.html", {"group": grp, "gameName": gameName})

			#Ending game
			# if request.POST.get("endgame"):
			# 	gme.complete = True
			# 	gme.save()
			# 	for person in grp.person_set.all():
			# 		for i in grp.person_set.all():
			# 			if i.id == person.id:
			# 				pass
			# 			elif i.points < person.points:
			# 				person.placing += 1
			# 				person.save()
			# 	# Adding stats to person
			# 	for person in grp.person_set.all():
			# 		person.stats += str(person.placing) + "." + str(grp.id) + "-" + str(gme.id) + ";"
			# 		person.save()
			# 	Creating results
			# 	res = results.objects.create(game = gme, groupname = grp.name)
			# 	for i in grp.person_set.all():
			# 		res.stats += str(i.name) + "," + str(i.points) + "," + str(i.placing) + ";"
			# 		res.save()
			# 	return HttpResponseRedirect("/results/%i" %res.id)

	else: 
		return render(request, "home_app/groups.html", {"group": grp, "gameName": gameName})

def result(request, groupID, gameID):
	gme = game.objects.get(id = gameID)
	grp = gme.group
	results = gme.results

	print(results)

	for player in results:
		player["welldones"] = player["hands"].count(0)

	return render(request, "home_app/results.html", {"game": gme, "results": gme.results, "group": grp})


#Statistic Views-------------------------------------------------------------------------------------------------------------------------------------
def groupStats (request, groupID):
	grp = group.objects.get(id = groupID)
	stats = {
		"avgPlace": [],
		"modePlace": [],
		"numberQueens": [],
		"numberWellDones": [],
		"numberMoonshots": [],
		"avgPointsGame": [],
		"avgQueensGame": [],
		"avgWellDonesGame": [],
		"avgPointsHand": [],
		"avgQueensHand": [],
		"avgWellDonesHand": [],
	}

	numberGames = len(grp.stats[0]["placings"])
	numberHands = len(grp.stats[0]["hands"])

	for player in grp.stats:
		sumPoints = sum(player["hands"])

		stats["avgPlace"].append({"name": player["name"], "value": round(sum(player["placings"]) / numberGames, 2)})
		stats["modePlace"].append({"name": player["name"], "value": statistics.mode(player["placings"])})
		stats["numberQueens"].append({"name": player["name"], "value": player["queens"]})
		stats["numberWellDones"].append({"name": player["name"], "value": player["hands"].count(0)})
		stats["numberMoonshots"].append({"name": player["name"], "value": player["moonshots"]})
		stats["avgPointsGame"].append({"name": player["name"], "value": round(sumPoints / numberGames, 2)})
		stats["avgQueensGame"].append({"name": player["name"], "value": round(player["queens"] / numberGames, 2)})
		stats["avgWellDonesGame"].append({"name": player["name"], "value": round(player["hands"].count(0) / numberGames)})
		stats["avgPointsHand"].append({"name": player["name"], "value": round(sumPoints / numberHands, 2)})
		stats["avgQueensHand"].append({"name": player["name"], "value": round(player["queens"] / numberHands, 2)})
		stats["avgWellDonesHand"].append({"name": player["name"], "value": round(player["hands"].count(0) / numberHands, 2)})

	return render(request, "home_app/groupStatistics.html", {"group": grp, "stats": stats})

def playerGroupStats(request, groupID, playerName):
	grp = group.objects.get(id = groupID)
	playerIndex = next((i for i, p in enumerate(grp.stats) if p["name"] == playerName), None)
	player = grp.stats[playerIndex]

	numberGames = len(player["placings"])
	numberHands = len(player["hands"])
	sumPoints = sum(player["hands"])

	stats = {
		"name": playerName,
		"avgPlace": round(sum(player["placings"]) / numberGames, 2),
		"modePlace": statistics.mode(player["placings"]),
		"numberQueens": player["queens"],
		"numberWellDones": player["hands"].count(0),
		"numberMoonshots": player["moonshots"],
		"avgPointsGame": round(sumPoints / numberGames, 2),
		"avgQueensGame": round(player["queens"] / numberGames, 2),
		"avgWellDonesGame": round(player["hands"].count(0) / numberGames),
		"avgPointsHand": round(sumPoints / numberHands, 2),
		"avgQueensHand": round(player["queens"] / numberHands, 2),
		"avgWellDonesHand": round(player["hands"].count(0) / numberHands, 2),
	}

	return render(request, "home_app/playerGroupStats.html", {"group": grp, "stats": stats})

def playerStatistics(request, playerName):
	player = request.user.person.filter(name__exact = playerName)[0]

	numberGames = len(player.stats["placings"])
	numberHands = len(player.stats["hands"])
	sumPoints = sum(player.stats["hands"])

	stats = {
		"name": playerName,
		"avgPlace": round(sum(player.stats["placings"]) / numberGames, 2),
		"modePlace": statistics.mode(player.stats["placings"]),
		"numberQueens": player.stats["queens"],
		"numberWellDones": player.stats["hands"].count(0),
		"numberMoonshots": player.stats["moonshots"],
		"avgPointsGame": round(sumPoints / numberGames, 2),
		"avgQueensGame": round(player.stats["queens"] / numberGames, 2),
		"avgWellDonesGame": round(player.stats["hands"].count(0) / numberGames),
		"avgPointsHand": round(sumPoints / numberHands, 2),
		"avgQueensHand": round(player.stats["queens"] / numberHands, 2),
		"avgWellDonesHand": round(player.stats["hands"].count(0) / numberHands, 2),
	}

	return render(request, "home_app/playerStatistics.html", {"stats": stats})


#Create---------------------------------------------------------------------------------------------------------------------------------------------

def create(request):
	if request.user.is_authenticated:
		username = request.user.username

		if request.method == "POST":
			data = request.POST.get("formData")
			formData = json.loads(data)

			stats = []

			for player in formData["players"]:
				info = {
					"name": player,
					"hands": [],
					"queens": 0,
					"moonshots": 0,
					"placings": []
				}
				stats.append(info)

			newgroup = group(
				name = formData["name"],
				maxpoints = formData["maxPoints"],
				user = request.user,
				owner = username,
				stats = stats,
				rotation = formData["rotation"]
			)
			newgroup.save()

			for player in formData["players"]:
				if request.user.person.filter(name__exact = player).exists() == False:
					newPerson = person(
						name = player,
						stats = {
							"hands": [],
							"queens": 0,
							"moonshots": 0,
							"placings": []
						},
						user = request.user
						)
					newPerson.save()
					newPerson.group.add(newgroup)

			return HttpResponseRedirect("/groups")

	return render(request, "home_app/create.html", {"people": request.user.person.all()})


#People-------------------------------------------------------------------------------------------------------------------------------------

def people(request):
	#Checking if user is authenitcated
	if request.user.is_authenticated == True:
		allplayers = []

		for person in request.user.person.all():
			allplayers.append(person)

		if request.POST.get("delete"):
			for i in allplayers:
				if request.POST.get("d" + str(i.id)) == "clicked":
					i.delete()

		return render(request, "home_app/people.html", {})

	return render(request, "home_app/people.html", {})


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


		# if response.method == "POST":
		# 	if response.POST.get("save"):
		# 		#Checking if points add up to 13
		# 		countpoints = 0
		# 		for person in grp.person_set.all():
		# 			if not response.POST.get("p" + str(person.id)):
		# 				countpoints += 0
		# 			else:
		# 				countpoints += int(response.POST.get("p" + str(person.id)))
		# 		if countpoints != 13:
		# 			messages.error(response, 'Total hearts for players must add up to 13.')
		# 			return HttpResponseRedirect("/groups/%i/%i" % (grp.id, gme.id))

		# 		#Checking if only one queen box is checked
		# 		countqueen = 0
		# 		for person in grp.person_set.all():
		# 			if response.POST.get("c" + str(person.id)) == "clicked":
		# 				countqueen += 1
		# 		if countqueen > 1:
		# 			messages.error(response, 'Only one queen box can be selected')
		# 			return HttpResponseRedirect("/groups/%i/%i" % (grp.id, gme.id))
		# 		elif countqueen < 1:
		# 			messages.error(response, 'A queen box must be selected')
		# 			return HttpResponseRedirect("/groups/%i/%i" % (grp.id, gme.id))

		# 		#Adding points after input is valid
		# 		for person in grp.person_set.all():
		# 			# if response.POST.get("c" + str(person.id)) == "clicked":
		# 			# 	person.points += 13
		# 			# elif response.POST.get("p" + str(person.id)) == "":
		# 			# 	person.points += 0
		# 			# else:
		# 			# 	person.points += int(response.POST.get("p" + str(person.id)))
		# 			# person.save()

		# 			tempstats = 0

		# 			if response.POST.get("p" + str(person.id)) == "":
		# 				person.points += 0
		# 				tempstats = 0
		# 			else:
		# 				person.points += int(response.POST.get("p" + str(person.id)))
		# 				tempstats = int(response.POST.get("p" + str(person.id)))

		# 			if response.POST.get("c" + str(person.id)) == "clicked":
		# 				person.points += 13
		# 				tempstats += 13
		# 				tempstats = str(tempstats) + "q"
		# 			else:
		# 				tempstats = str(tempstats)

		# 			# tempstats += "." + str(grp.id) + "-" + str(gme.id) + ","
		# 			# person.stats += tempstats

		# 			person.save()

		# 		#Ending the game when maxpoints is reached
		# 		for person in grp.person_set.all():
		# 			if person.points >= grp.maxpoints:
		# 				gme.complete = True
		# 				gme.save()
		# 				for person in grp.person_set.all():
		# 					for i in grp.person_set.all():
		# 						if i.id == person.id:
		# 							pass
		# 						elif i.points < person.points:
		# 							person.placing += 1
		# 							person.save()
		# 				#Adding stats to person
		# 				# for person in grp.person_set.all():
		# 				# 	person.stats += str(person.placing) + "." +str(grp.id) + "-" + str(gme.id) + ";"
		# 				# 	person.save()
		# 				#Creating results
		# 				res = results.objects.create(game = gme, groupname = grp.name)
		# 				for i in grp.person_set.all():
		# 					res.stats += str(i.name) + "," + str(i.points) + "," + str(i.placing) + ";"
		# 					res.save()
		# 				return HttpResponseRedirect("/results/%i" %res.id)

# def addplayers(request, id):
# 	grp = group.objects.get(id = id)
# 	userplayers = request.user.person.all()

# 	if request.POST.get("addplayer"):
# 		if not request.POST.get("addplayer"):
# 			messages.error(request, 'Name cannot be blank.')
# 			return HttprequestRedirect("/groups/addplayers/%i" %grp.id)
# 		else:
			
# 	elif request.POST.get("createGroup"):
# 		count = 0
# 		for i in grp.person_set.all():
# 			count += 1
# 		if count < 3:
# 			messages.error(request, 'Group must have at least 3 players.')
# 			return render(request, "home_app/addplayers.html", {"group": grp})
# 		else:
# 			return HttpResponseRedirect("/groups")

# 	return render(request, "home_app/addplayers.html", {"group": grp, "players": userplayers})