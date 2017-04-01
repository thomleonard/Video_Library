from django import forms

class SearchName(forms.Form):
    name = forms.CharField(max_length=100, help_text="Please enter the title of the TV show.")

