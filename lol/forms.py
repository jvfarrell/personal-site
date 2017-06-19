from django import forms


class SummonerForm(forms.Form):
    summoner_name = forms.CharField(label='Summoner Name', widget=forms.TextInput(attrs={'placeholder': 'Summoner Name'}))
