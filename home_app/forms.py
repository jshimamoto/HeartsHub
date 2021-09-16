from django import forms

class creategroup(forms.Form):
	name = forms.CharField(label="Name", max_length = 100)
	maxpoints = forms.IntegerField(label= "Maximum Points")
	addplayer = forms.CharField(label="Add Player", max_length=100)
