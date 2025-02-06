from django import forms

class FlightSearchForm(forms.Form):
    from_location = forms.CharField(max_length=255, required=True, label='From')
    to_location = forms.CharField(max_length=255, required=True, label='To')
    departure_date = forms.DateField(required=True, label='Departure Date', widget=forms.DateInput(attrs={'type': 'date'}))
    return_date = forms.DateField(required=False, label='Return Date', widget=forms.DateInput(attrs={'type': 'date'}))
    adults = forms.IntegerField(required=False, min_value=1, initial=1, label='Adults')
    children = forms.IntegerField(required=False, min_value=0, initial=0, label='Children')
    cabin_class = forms.ChoiceField(
        choices=[('ECONOMY', 'Economy'), ('BUSINESS', 'Business'), ('FIRST', 'First Class')],
        required=False,
        initial='ECONOMY',
        label='Cabin Class'
    )