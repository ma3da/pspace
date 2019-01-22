from django import forms


class BlockForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=True)
