# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile 

# UserProfile'ı User admin sayfasında inline olarak göstermek için
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Bilgileri'
    fk_name = 'user'
    
    # YENİ: Admin panelinde daha düzenli bir görünüm için alanları grupla
    fieldsets = (
        (None, {
            'fields': ('profile_picture', 'phone_number')
        }),
        ('Adres Bilgileri', {
            'fields': ('city', 'district', 'postal_code', 'address_detail')
        })
    )

# Mevcut UserAdmin'i genişleterek inline profili ekle
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile',) 

    # Profil bilgilerini getiren bir fonksiyon (isteğe bağlı)
    def get_profile_phone(self, instance):
        return instance.profile.phone_number
    get_profile_phone.short_description = 'Telefon'

# Mevcut User admin kaydını kaldırıp yenisini ekle
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
