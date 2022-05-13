from django import forms
class Form(forms.Form):
    choices = (
        ("Post_Text", "Post_Text"),
        ("Comments", "Comments"),
        ("Replies", "Replies")
    )

    Enter_movie_title=forms.CharField()
    Filter=forms.ChoiceField(choices=choices)
    Results=forms.IntegerField()
