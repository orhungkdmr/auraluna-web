from .cart import Cart
from products.models import Category

def cart(request):
    """
    Sepeti (Cart sınıfını) tüm şablonlara ekler.
    """
    return {'cart': Cart(request)}


def main_categories(request):
    """
    Ürün listesi sayfasındaki sol menü (sidebar) için kategorileri hazırlar.
    """
    categories = Category.objects.filter(parent=None)
    
    # GÜNCELLEME: Sol menüdeki 'torun' kategorilerini (örn: Gömlek)
    # çekebilmek için prefetch'i derinleştiriyoruz.
    categories = categories.prefetch_related('children__children')
    
    return {'main_categories': categories}


def structured_nav_categories(request):
    """
    Header'daki mega-menü için kategorileri hazırlar.
    (HATALI KOD DÜZELTİLDİ: Basit ve 3 seviyeli çalışan yapı)
    """
    categories = Category.objects.filter(parent=None).prefetch_related('children__children')
    
    structured_data = []
    
    for top_category in categories: # Örn: Erkek
        top_cat_data = {
            'id': top_category.id,
            'name': top_category.name,
            'url': top_category.get_absolute_url(),
            'children': []
        }
        
        for inter_category in top_category.children.all(): # Örn: Giysi, Ayakkabı
            inter_cat_data = {
                'id': inter_category.id,
                'name': inter_category.name,
                'url': inter_category.get_absolute_url(),
                'icon_class': inter_category.icon_class,
                'children': [] # Torunlar için listeyi hazırla
            }
            
            for final_category in inter_category.children.all(): # Örn: Gömlek, Pantolon
                inter_cat_data['children'].append({
                    'id': final_category.id,
                    'name': final_category.name,
                    'url': final_category.get_absolute_url(),
                })
            
            # Ara kategoriyi (çocukları olsun veya olmasın) ana listeye ekle
            top_cat_data['children'].append(inter_cat_data)
        
        structured_data.append(top_cat_data)
        
    return {'structured_nav_categories': structured_data}