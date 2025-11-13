# pages/context_processors.py

from .models import SiteSetting, AnnouncementBanner 

def site_settings(request):
    """
    Site ayarlarını ve TÜM AKTİF duyuru bantlarını tüm şablonlara ekler.
    """
    settings = None
    # YENİ: Aktif bantları liste olarak tutacak değişken
    active_banners_list = None 
    
    try:
        settings = SiteSetting.objects.first() 
    except SiteSetting.DoesNotExist:
        pass 
        
    try:
        # YENİ: Aktif olan TÜM duyuru bantlarını al (Modeldeki ordering'e göre sıralanır)
        active_banners_list = AnnouncementBanner.objects.filter(is_active=True)
    except AnnouncementBanner.DoesNotExist:
        pass # Aktif bant yoksa hata verme

    return {
        'site_settings': settings,
        # YENİ: Context değişkeninin adını çoğul yapıyoruz ve listeyi gönderiyoruz
        'active_announcement_banners': active_banners_list 
    }