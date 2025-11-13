import django_filters
from django import forms
from .models import Product, Color, Size

class ProductFilter(django_filters.FilterSet):
    # ModelMultipleChoiceFilter, birden fazla seçeneği (checkbox)
    # aynı anda seçmemize olanak tanır.
    
    color = django_filters.ModelMultipleChoiceFilter(
        field_name='variants__color', # İlişkili model üzerinden filtreleme
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Renge Göre Filtrele"
    )
    
    size = django_filters.ModelMultipleChoiceFilter(
        field_name='variants__size', # İlişkili model üzerinden filtreleme
        queryset=Size.objects.all().order_by('order'), # Bedenleri sıralı getir
        widget=forms.CheckboxSelectMultiple,
        label="Bedene Göre Filtrele"
    )

    class Meta:
        model = Product
        # 'fields' önemlidir, ancak asıl filtrelemeyi yukarıda 
        # manuel olarak tanımladık çünkü varyantlar üzerinden gitmemiz gerekiyor.
        # Burayı sadece 'model' tanımı için kullanıyoruz.
        fields = ['color', 'size']