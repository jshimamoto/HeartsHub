from django.contrib import admin
from .models import person, group, game, results
# Register your models here.
admin.site.register(person)
admin.site.register(group)
admin.site.register(game)
admin.site.register(results)


# Notes/Archive ----------------------------------------------------------------------------------------------

# admin.site.register(player)