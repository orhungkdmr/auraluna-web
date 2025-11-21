import django_filters
from django import forms
from .models import Product, Color, Size, Category

class ProductFilter(django_filters.FilterSet):
    # Kategorileri çoklu seçilebilir yapıyoruz (name='category')
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Kategoriler",
        conjoined=False  # False = VEYA mantığı (Gömlek VEYA Pantolon getir)
    )

    color = django_filters.ModelMultipleChoiceFilter(
        field_name='variants__color', 
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Renk"
    )
    
    size = django_filters.ModelMultipleChoiceFilter(
        field_name='variants__size', 
        queryset=Size.objects.all().order_by('order'), 
        widget=forms.CheckboxSelectMultiple,
        label="Beden"
    )

    class Meta:
        model = Product
        fields = ['category', 'color', 'size']