from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Brand, Invoice, InvoiceDetail, CreditNote


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields: self.fields[f].widget.attrs['class'] = 'form-control'

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

class InvoiceForm(forms.ModelForm):
    """Formulario para cabecera de factura."""
    class Meta:
        model = Invoice
        fields = ['customer']
        labels = {'customer': 'Cliente'}
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
        }


InvoiceDetailFormSet = inlineformset_factory(
    Invoice,
    InvoiceDetail,
    fields=['product', 'quantity', 'unit_price'],
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    widgets={
        'product':    forms.Select(attrs={'class': 'form-select id-product'}),
        'quantity':   forms.NumberInput(attrs={'class': 'form-control id-qty', 'min': 1}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control id-price', 'step': '0.01', 'min': '0.01'}),
    }
)


class CreditNoteForm(forms.ModelForm):
    """Formulario para crear una Nota de Crédito sobre una factura emitida."""
    class Meta:
        model  = CreditNote
        fields = ['tipo', 'amount', 'reason']
        labels = {
            'tipo':   'Tipo de Nota',
            'amount': 'Monto',
            'reason': 'Motivo',
        }
        widgets = {
            'tipo':   forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                            'placeholder': 'Describa el motivo de la devolución o descuento…'}),
        }
