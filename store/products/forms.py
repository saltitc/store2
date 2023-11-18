from typing import Any

from django import forms

from .models import ProductCategory, Rating


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        required=False,
        label="Категория",
        empty_label="Выберите категорию",
        widget=forms.Select(attrs={"class": "form-control py-4", "placeholder": "Любая"}),
    )


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating", "product", "user"]

    def save(self, commit: bool = True) -> Any:
        instance = super().save(commit)
        self.cleaned_data["product"].update_average_rating()
        return instance
