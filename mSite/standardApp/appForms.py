from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder':'Username','class':'form-control'}))
    password = forms.CharField(max_length=50,widget=forms.PasswordInput(attrs={'placeholder':'Password','class':'form-control'}))
    
class PasswordChangeForm(forms.Form):
    password0 = forms.CharField(max_length=50,widget=forms.PasswordInput)
    password1 = forms.CharField(max_length=50,widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=50,widget=forms.PasswordInput)
