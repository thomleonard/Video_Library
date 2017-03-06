from django import forms

class LowerCharField(forms.CharField):
    def to_python(self, value):
        return value.lower()

class SearchName(forms.Form):
    name = LowerCharField(max_length=100, help_text="Please enter the title of the TV show.")
