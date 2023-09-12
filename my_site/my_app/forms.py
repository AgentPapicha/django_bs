from django import forms


class UserForm(forms.Form):
    name = forms.CharField(label='User name', max_length=20)
    age = forms.IntegerField(label='User age')
    gender = forms.CharField(label='User gender', max_length=6)
    nationality = forms.CharField(label='User nationality', max_length=100)


class PublisherForm(forms.Form):
    name = forms.CharField(max_length=300)
