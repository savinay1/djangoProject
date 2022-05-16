from django import forms


class Form(forms.Form):
    choices = (
        ("Post_Text", "Posts"),
        ("Comments", "Comments"),
        ("Replies", "Replies")
    )

    Enter_movie_title = forms.CharField(label="Movie Title")
    Filter = forms.ChoiceField(choices=choices)
    Results = forms.IntegerField(label="Samples")
