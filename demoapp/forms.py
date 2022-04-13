from django import forms
class Form(forms.Form):
    Enter_movie_title=forms.CharField()
    Filter=forms.CharField()
    Results=forms.IntegerField()
