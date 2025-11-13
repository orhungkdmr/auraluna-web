# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Kullanıcı Profil Modeli
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # YENİ: Profil Resmi Alanı
    # Resimlerin 'media/profile_pics/' klasörüne yüklenmesini sağlar
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True, 
        default='profile_pics/default.png', # Varsayılan bir resim (Bunu kendiniz sağlamalısınız)
        verbose_name="Profil Resmi"
    )
    
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon Numarası")
    
    # YENİ: Detaylı Adres Alanları (Eski 'address' alanı kaldırıldı)
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Şehir")
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name="İlçe")
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Posta Kodu")
    address_detail = models.TextField(blank=True, null=True, verbose_name="Açık Adres (Cadde, Sokak, No vb.)")

    def __str__(self):
        return f"{self.user.username}'s Profile"

# User nesnesi kaydedildiğinde (oluşturulduğunda) çalışacak sinyal
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save() # Mevcut profilin de kaydedildiğinden emin ol
