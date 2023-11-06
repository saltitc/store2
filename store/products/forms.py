from django import forms
from .models import ProductCategory


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        required=False,
        label="Категория",
        empty_label="Выберите категорию",
        widget=forms.Select(
            attrs={"class": "form-control py-4", "placeholder": "Любая"}
        ),
    )
