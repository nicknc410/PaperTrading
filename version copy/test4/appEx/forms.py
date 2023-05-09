from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class InvestForm(forms.Form):
    stock=forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    shares=forms.FloatField()

class SendForm(forms.Form):
    send=forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message=forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'class': 'form-control'}))