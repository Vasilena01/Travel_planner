from django import forms

class HotelSearchForm(forms.Form):
    destination = forms.CharField(max_length=100)
    arrival_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    adults = forms.IntegerField(required=False, min_value=1, initial=1)
    children_age = forms.CharField(required=False, initial='')
    room_qty = forms.IntegerField(required=False, initial=1)