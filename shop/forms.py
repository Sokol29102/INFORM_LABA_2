from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['client', 'drone', 'date']

        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'number_of_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'country': forms.Select(attrs={'class': 'form-control',}),

        }