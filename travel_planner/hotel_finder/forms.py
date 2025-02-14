from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

class HotelSearchForm(forms.Form):
    destination = forms.CharField(max_length=100)
    arrival_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    adults = forms.IntegerField(required=False, min_value=1, initial=1)
    children_age = forms.CharField(required=False, initial='')
    room_qty = forms.IntegerField(required=False, initial=1)

    def clean_arrival_date(self):
        arrival_date = self.cleaned_data.get('arrival_date')
        if arrival_date and arrival_date < timezone.now().date():
            raise ValidationError('Dates cannot be in the past.')
        return arrival_date

    def clean_departure_date(self):
        departure_date = self.cleaned_data.get('departure_date')
        arrival_date = self.cleaned_data.get('arrival_date')
        
        if departure_date and arrival_date and departure_date < arrival_date:
            raise ValidationError('Departure date must be after arrival date.')
        
        if departure_date and departure_date < timezone.now().date():
            raise ValidationError('Departure date cannot be in the past.')
        
        return departure_date