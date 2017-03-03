from django import forms

class SearchName(forms.Form):
    TV_Show_title = forms.CharField(max_length=100)