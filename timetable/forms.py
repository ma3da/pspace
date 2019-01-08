from django import forms


class BlockForm(forms.Form):
    activity_name = forms.CharField(max_length=128)
    hour_in = forms.CharField(widget=forms.NumberInput)
    hour_out = forms.CharField(widget=forms.NumberInput, required=False)
