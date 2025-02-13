from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save  # Import post_save signal


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=16, null=True, blank=True)  # Zorunlu değil
    birth_date = models.CharField(max_length=40,null=True, blank=True)  # Zorunlu değil
    gender = models.CharField(max_length=1, choices=[('M', 'Erkek'), ('F', 'Kadın')], null=True, blank=True)  # Zorunlu değil
    location = models.CharField(max_length=100, null=True, blank=True)  # Zorunlu değil
    photo = models.CharField(max_length=400,null=True, blank=True)  # Zorunlu değil

    def __str__(self):
        return self.user.username
    


class Kullanıcılar(models.Model):
    kullanici_id = models.AutoField(primary_key=True)
    kullanici_adi = models.CharField(max_length=150, unique=True)
    sifre = models.CharField(max_length=128)
    e_posta = models.EmailField(unique=True)
    konum = models.CharField(max_length=255, blank=True, null=True)
    ad = models.CharField(max_length=100, blank=True, null=True)
    soyad = models.CharField(max_length=100, blank=True, null=True)
    dogum_tarihi = models.CharField(max_length=20, blank=True, null=True)
    cinsiyet = models.CharField(max_length=10, blank=True, null=True)
    telefon_no = models.CharField(max_length=16, blank=True, null=True)
    profil_fotograf = models.CharField(max_length=400, blank=True, null=True)

    # User tablosu ile ilişkilendir
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="kullanici")
    class Meta:
        db_table = 'kullanıcılar'

    def __str__(self):
        return f"{self.ad} {self.soyad}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class GenelMesaj(models.Model):
    gonderici = models.ForeignKey(User, on_delete=models.CASCADE)
    mesaj_metni = models.TextField()
    gonderim_zamani = models.DateTimeField(auto_now_add=True)    



class Etkinlikler(models.Model):
    id = models.AutoField(primary_key=True)
    etkinlik_adi = models.CharField(max_length=200)
    aciklama = models.TextField(blank=True, null=True)
    tarih = models.DateField()
    saat = models.TimeField()
    sure = models.IntegerField(help_text="Etkinlik süresi dakikalar olarak")
    konum = models.CharField(max_length=255)
    kategori = models.CharField(max_length=100)
    
    # 'user_id' yerine doğru 'kullanici' ilişkisini kuruyoruz
    kullanici = models.ForeignKey(Kullanıcılar, on_delete=models.CASCADE)

    class Meta:
        db_table = 'etkinlikler'
        verbose_name = 'Etkinlik'  # Tekil adı
        verbose_name_plural = 'Etkinlikler'  # Çoğul adı

    def __str__(self):
        return self.etkinlik_adi