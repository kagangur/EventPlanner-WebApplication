from django.contrib import admin
from .models import Kullanıcılar, Profile
from .models import Etkinlikler

class EtkinliklerAdmin(admin.ModelAdmin):
    list_display = ('etkinlik_adi', 'tarih', 'saat', 'konum', 'kategori', 'kullanici_id')  # Görüntülenecek alanlar
    search_fields = ('etkinlik_adi', 'konum', 'kategori')  # Arama alanları
    list_filter = ('kategori', 'tarih')  # Filtreleme alanları

# Admin paneline etkinlik modelini kaydediyoruz
admin.site.register(Etkinlikler, EtkinliklerAdmin)


@admin.register(Kullanıcılar)
class KullanıcılarAdmin(admin.ModelAdmin):
    list_display = ('kullanici_adi', 'ad', 'soyad', 'e_posta')
    search_fields = ('kullanici_adi', 'ad', 'soyad', 'e_posta')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'birth_date', 'gender', 'photo_preview')
    search_fields = ('user__username', 'phone_number', 'interests')
    list_filter = ('gender', 'birth_date')
    readonly_fields = ('photo_preview',)
    
    def photo_preview(self, obj):
        if obj.photo:
            return f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius: 50%;"/>'
        return "No Image"
    photo_preview.allow_tags = True
    photo_preview.short_description = "Photo Preview"