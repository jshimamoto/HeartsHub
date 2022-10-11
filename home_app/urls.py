from django.urls import path
from . import views


urlpatterns = [
	path('', views.home, name = 'home'),
	path('create/', views.create, name = 'create'),
	path('groups/', views.groups, name = 'groups'),
	#path('groups/addplayers/<int:id>', views.addplayers, name = 'addplayers'),
	path('groups/<int:id>', views.groupview, name = 'groupview'),
	path('groups/<int:groupid>/newgame/<int:gameNumber>', views.game_, name = 'newGame'),
	path('groups/<int:groupID>/results/<int:gameID>', views.result, name = 'result'),
	path('groups/<int:groupID>/stats', views.groupStats, name = 'groupStats'),
	path('groups/<int:groupID>/<str:playerName>', views.playerGroupStats, name = 'playerGroupStats'),
	path('people/', views.people, name = 'people'),
	path('people/<str:playerName>', views.playerStatistics, name = 'playerStatistics')
]