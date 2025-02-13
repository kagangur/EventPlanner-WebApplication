from django.contrib.auth.forms import AuthenticationForm
from django.utils.safestring import mark_safe
import json
from django.contrib import messages
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import logout
from .forms import RegisterForm, MessageForm
from django.shortcuts import render, redirect
from .models import Kullanıcılar
from django.db import connection
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from geopy.distance import geodesic
from geopy.geocoders import Nominatim  # Eğer geopy kullanıyorsanız
from geopy.distance import geodesic
# veya
import googlemaps  # Eğer Google Maps API kullanıyorsanız


# Varsayılan şehir koordinatları
DEFAULT_CITY_COORDINATES = {
    'İstanbul': (41.0082, 28.9784),
    'Ankara': (39.9334, 32.8597),
    'İzmir': (38.4237, 27.1428),
    'Bursa': (40.1956, 29.0603),
    'Antalya': (36.8841, 30.7056),
    'Edirne': (41.6760, 26.5550),
    'Kayseri': (38.7200, 35.4826),
    'Bolu': (40.7391, 31.6090),
    'Çeşme': (38.3137, 26.3031),
    'Gaziantep': (37.0662, 37.3833),
    'Sakarya': (40.8647, 30.4101),
    'Konya': (37.8714, 32.4844),
    'Mersin': (36.8139, 34.6399),
    'Trabzon': (41.0034, 39.7227),
    'Kocaeli': (40.8667, 29.9167),
    'Tekirdağ': (40.9785, 27.5110),
}

@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def profile(request):
    # Giriş yapan kullanıcının username bilgisi
    current_username = request.user.username
    rozet = "Çaylak"  # Varsayılan rozet
    profile_photo_url = None  # Varsayılan profil fotoğrafı
    interest = None  # Varsayılan ilgi alanı
    e_posta = None
    konum = None
    ad = None
    soyad = None
    dogum_tarihi = None
    cinsiyet = None

    with connection.cursor() as cursor:
        # Kullanıcı bilgilerini al
        cursor.execute("""
            SELECT kullanici_id, profil_fotograf, ilgi_alanı, e_posta, konum, ad, soyad, dogum_tarihi, cinsiyet
            FROM kullanıcılar
            WHERE kullanici_adi = %s
        """, [current_username])
        row = cursor.fetchone()

        if row:
            kullanici_id = row[0]
            profile_photo_url = row[1]  # Profil fotoğrafı
            interest = row[2]  # İlgi alanı
            e_posta = row[3]  # E-posta
            konum = row[4]  # Konum
            ad = row[5]  # Ad
            soyad = row[6]  # Soyad
            dogum_tarihi = row[7]  # Doğum tarihi
            cinsiyet = row[8]  # Cinsiyet

            # Kullanıcının toplam puanını al
            cursor.execute("""
                SELECT SUM(puan)
                FROM puanlar
                WHERE kullanici_id = %s
            """, [kullanici_id])
            points_row = cursor.fetchone()

            if points_row and points_row[0]:
                total_points = points_row[0]

                # Rozet belirleme
                if total_points <= 30:
                    rozet = "Çaylak"
                elif 30 < total_points < 60:
                    rozet = "Deneyimli"
                elif 60 <= total_points < 90:
                    rozet = "Kıdemli"
                else:  # total_points >= 90
                    rozet = "Usta"

    return render(request, 'profile.html', {
        'profile_photo_url': profile_photo_url,
        'rozet': rozet,
        'interest': interest,
        'e_posta': e_posta,
        'konum': konum,
        'ad': ad,
        'soyad': soyad,
        'dogum_tarihi': dogum_tarihi,
        'cinsiyet': cinsiyet
    })

def save_profile_photo(request):
    if request.method == 'POST':
        user = request.user
        try:
            # Kullanıcıyı `Kullanıcılar` tablosunda bul
            profile = Kullanıcılar.objects.get(kullanici_adi=user.username)
            photo_url = request.POST.get('photo_url')  # Formdan gelen URL'yi al
            if photo_url:
                profile.profil_fotograf = photo_url  # URL'yi kaydet
                profile.save()
                messages.success(request, 'Profil fotoğrafınız başarıyla güncellendi.')
            else:
                messages.error(request, 'Geçerli bir fotoğraf URL\'si girin.')
        except Kullanıcılar.DoesNotExist:
            messages.error(request, 'Profil bilgileri bulunamadı.')
        return redirect('profile')  # Profil sayfasına yönlendir

    return redirect('profile')


def save_interests(request):
    if request.method == 'POST':
        selected_interests = request.POST.getlist('interests')
        # Save selected_interest to user profile
        messages.success(request, 'İlgi alanı başarıyla kaydedildi.')
    return redirect('profile')

def save_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        # Save latitude and longitude to user profile
        messages.success(request, 'Konum başarıyla kaydedildi.')
    return redirect('profile')

def save_profile(request):
    if request.method == "POST":
        # İlgi alanlarını al
        selected_interests = request.POST.getlist('interests')
        
        # Konum bilgilerini al
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Bilgileri kullanıcı profiline kaydetme işlemlerini burada yapabilirsiniz
        # Örneğin:
        # user.profile.interests = selected_interests
        # user.profile.latitude = latitude
        # user.profile.longitude = longitude
        # user.profile.save()

        messages.success(request, "Profil başarıyla güncellendi.")
        return redirect('profile')  # Profil sayfasına yönlendirme

    return render(request, 'profile.html')



# Create your views here.
@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def index(request):
    current_username = request.user.username  # Giriş yapan kullanıcının kullanıcı adı

    with connection.cursor() as cursor:
        # Kullanıcı adı ile kullanıcı ID'sini alıyoruz
        cursor.execute("""
            SELECT kullanici_id
            FROM kullanıcılar
            WHERE kullanici_adi = %s
        """, [current_username])
        row = cursor.fetchone()

    if row:
        kullanici_id = row[0]

        # Puanlar tablosunu sorgulayıp kullanıcının puanını ve puan_bildirimi_gonderildi durumunu alıyoruz
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT puan, puan_bildirimi_gonderildi
                FROM puanlar
                WHERE kullanici_id = %s
            """, [kullanici_id])
            puan_row = cursor.fetchone()

            if puan_row:
                puan = puan_row[0]
                puan_bildirimi_gonderildi = puan_row[1]

                # Eğer kullanıcının puanı 100'den fazla ve bildirimi gönderilmediyse
                if puan >= 100 and not puan_bildirimi_gonderildi:
                    # Puanlar tablosundaki puan_bildirimi_gonderildi'yi TRUE yapıyoruz
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE puanlar
                            SET puan_bildirimi_gonderildi = TRUE
                            WHERE kullanici_id = %s
                        """, [kullanici_id])

                    # Bildirimler tablosuna yeni bir bildirim ekliyoruz
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO bildirimler (kullanici_id, title, message, timestamp, is_read)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [
                            kullanici_id,
                            'Tebrikler! ',
                            'Puanınız 100\'ü geçti.',
                            datetime.now(),
                            False  # Bildirim ilk başta okunmamış olacak
                        ])

    return render(request, "index.html")

def login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Giriş işlemleri burada yapılacak
            pass
    return render(request, 'login.html', {'form': form})

def custom_logout_view(request):
    logout(request)
    return redirect('/login')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # auth_user tablosuna kullanıcı kaydı yapıyoruz
            user = form.save()

            # Kullanıcılar tablosuna verileri kaydediyoruz
            Kullanıcılar.objects.create(
                kullanici_adi=user.username,
                sifre=form.cleaned_data.get('password1'),  # Şifre hashlenmiş olacak
                e_posta=user.email,
                konum=form.cleaned_data.get('konum'),
                ad=user.first_name,
                soyad=user.last_name,
                dogum_tarihi=form.cleaned_data.get('dogum_tarihi'),
                cinsiyet=form.cleaned_data.get('cinsiyet'),
                telefon_no=form.cleaned_data.get('telefon_no'),
                profil_fotograf=form.cleaned_data.get('profil_fotograf'),
                user_id=user.id  # auth_user tablosundaki user id'yi alıyoruz

            )



                        # Yeni eklenen kullanıcının ID'sini alıyoruz
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT kullanici_id
                    FROM kullanıcılar
                    WHERE kullanici_adi = %s
                """, [user.username])  # Kayıt ettiğimiz kullanıcının adını sorguluyoruz
                yeni_kullanici_id = cursor.fetchone()[0]

            # Puanlar tablosuna giriş yapıyoruz
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO puanlar (kullanici_id, puan, ilk_katilim, kazanilan_tarih)
                    VALUES (%s, %s, %s, %s)
                """, [
                    yeni_kullanici_id,
                    0,  # Başlangıç puanı
                    False,  # İlk katılım henüz gerçekleşmedi
                    datetime.now()  # Puanın başlangıç tarihi
                ])

            


            # Başarılı mesajı
            messages.success(request, 'Hesabınız başarıyla oluşturuldu.')

            return redirect('login')  # Ana sayfaya yönlendir

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})



@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def stats(request):
    current_username = request.user.username  # Giriş yapan kullanıcının kullanıcı adı
    total_points = 0  # Varsayılan değer
    total_events = 0  # Katıldığı etkinlik sayısı
    events_participants_data = []  # Organize edilen etkinliklere katılan kişi sayısı

    with connection.cursor() as cursor:
        # İlk olarak auth_user tablosundan kullanıcı adını kullanarak user_id alıyoruz
        cursor.execute("""
            SELECT kullanici_id
            FROM kullanıcılar
            WHERE kullanici_adi = %s
        """, [current_username])
        row = cursor.fetchone()

        if row:
            kullanici_id = row[0]  # kullanıcı_id değerini al

            # Şimdi puanlar tablosundan bu kullanıcı ID'ye ait toplam puanı alıyoruz
            cursor.execute("""
                SELECT SUM(puan)
                FROM puanlar
                WHERE kullanici_id = %s
            """, [kullanici_id])
            points_row = cursor.fetchone()

            if points_row and points_row[0] is not None:
                total_points = points_row[0]

# Katıldığı etkinlik sayısını hesapla
            cursor.execute("""
                SELECT COUNT(etkinlik_id)
                FROM katılımcılar
                WHERE kullanici_id = %s
            """, [kullanici_id])
            events_row = cursor.fetchone()
            if events_row and events_row[0] is not None:
                total_events = events_row[0]

            # Etkinlikleri ve her etkinliğe katılan kişi sayısını al
            cursor.execute("""
                SELECT etkinlikler.etkinlik_adi, COUNT(katılımcılar.kullanici_id)
                FROM etkinlikler
                LEFT JOIN katılımcılar ON etkinlikler.id = katılımcılar.etkinlik_id
                WHERE etkinlikler.kullanici_id = %s
                GROUP BY etkinlikler.etkinlik_adi
            """, [kullanici_id])

            rows = cursor.fetchall()  # Sorgu sonucunu alıyoruz
        else:
            rows = []

    event_names = [row[0] for row in rows]  # Etkinlik adları
    participants_count = [row[1] for row in rows]  # Katılımcı sayıları
    # Şablona veriyi gönder
    context = {
        'total_points': total_points,
        'total_events': total_events,  # Katıldığı etkinlik sayısı
        'event_names': event_names,
        'participants_count': participants_count,

    }
    return render(request, 'stats.html', context)


@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def addevent(request):

    if request.method == 'POST':
        # Form verilerini al
        etkinlik_adi = request.POST.get('etkinlik_adi')
        aciklama = request.POST.get('aciklama')
        tarih = request.POST.get('tarih')
        saat = request.POST.get('saat')
        sure = request.POST.get('sure')
        konum = request.POST.get('konum')
        kategori = request.POST.get('kategori')

        # Giriş yapan kullanıcının ID'sini al
        current_username = request.user.username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kullanici_id 
                FROM kullanıcılar 
                WHERE kullanici_adi = %s
            """, [current_username])
            kullanici_id = cursor.fetchone()[0]

        # Puanlar tablosundan ilk katılım bilgisini al
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ilk_katilim
                FROM puanlar 
                WHERE kullanici_id = %s
            """, [kullanici_id])
            ilk_katilim_data = cursor.fetchone()

            if ilk_katilim_data:
                ilk_katilim = ilk_katilim_data[0]
            else:
                ilk_katilim = False  # Eğer kullanıcı için puanlar tablosunda kayıt yoksa ilk katılım False kabul edelim

        # Etkinliği veritabanına ekle ve etkinlik_id'yi al
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO etkinlikler (etkinlik_adi, aciklama, tarih, saat, sure, konum, kategori, kullanici_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [etkinlik_adi, aciklama, tarih, saat, sure, konum, kategori, kullanici_id])

            # Son eklenen etkinliğin ID'sini al
            cursor.execute("SELECT LAST_INSERT_ID()")
            etkinlik_id = cursor.fetchone()[0]

        # Katılımcılar tablosuna etkinliği oluşturan kullanıcıyı ekle
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO katılımcılar (kullanici_id, etkinlik_id)
                VALUES (%s, %s)
            """, [kullanici_id, etkinlik_id])

        # Kullanıcıya puan ekleme işlemi
        with connection.cursor() as cursor:
            if not ilk_katilim:  # İlk katılım durumu
                bonus_puan = 20  # İlk katılım bonusu
                etkinlik_kurulma_puani = 15  # Etkinlik kurma puanı
                katilim_puani = 10  # Katılım puanı

                # Kullanıcının mevcut puanını getir
                cursor.execute("""
                    SELECT puan
                    FROM puanlar
                    WHERE kullanici_id = %s
                """, [kullanici_id])
                result = cursor.fetchone()

                if result:
                    mevcut_puan = result[0]
                    yeni_puan = mevcut_puan + bonus_puan + etkinlik_kurulma_puani + katilim_puani  # Bonus, kurma ve katılım puanı
                    cursor.execute("""
                        UPDATE puanlar
                        SET puan = %s, ilk_katilim = TRUE, kazanilan_tarih = %s
                        WHERE kullanici_id = %s
                    """, [yeni_puan, datetime.now(), kullanici_id])



            else:
                # Eğer daha önce katılmışsa sadece 10 puan ekle
                katilim_puani = 10
                etkinlik_kurulma_puani = 15  # Etkinlik kurma puanı
                eklenecek_puan = katilim_puani + etkinlik_kurulma_puani
                cursor.execute("""
                    UPDATE puanlar
                    SET puan = puan + %s, kazanilan_tarih = %s
                    WHERE kullanici_id = %s
                """, [eklenecek_puan, datetime.now(), kullanici_id])

        # Kullanıcılar tablosundaki tüm kullanıcılara bildirim gönder
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kullanici_id
                FROM kullanıcılar
            """)
            all_users = cursor.fetchall()

            for user in all_users:
                cursor.execute("""
                    INSERT INTO bildirimler (kullanici_id, title, message, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, [user[0], 'Yeni Etkinlik Oluşturuldu', f'{etkinlik_adi} etkinliği oluşturuldu.', datetime.now()])

        messages.success(request, "Etkinlik başarıyla eklendi ve katılımcı olarak eklendiniz!")
        return redirect('addevent')

    return render(request, 'addevent.html')


@login_required(login_url='login')
def events(request):
    username = request.user.username  # Oturum açmış kullanıcının kullanıcı adı

    # Kullanıcı ID'sini almak
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()

        if user_id_result:
            user_id = user_id_result[0]
        else:
            user_id = None

        if user_id:
            # Kullanıcının katıldığı etkinlikleri almak
            cursor.execute("""
                SELECT e.id, e.etkinlik_adi, e.aciklama, e.tarih, e.saat, e.konum, e.kategori
                FROM etkinlikler e
                INNER JOIN katılımcılar k ON e.id = k.etkinlik_id
                WHERE k.kullanici_id = %s
            """, [user_id])
            events = cursor.fetchall()
        else:
            events = []

    # Verileri şablona gönder
    return render(request, 'events.html', {'events': events})
@login_required(login_url='login')
def notifications(request):
    # Kullanıcı ID'sini al
    username = request.user.username
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, message, timestamp, is_read
            FROM bildirimler
            WHERE kullanici_id = (SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s)
            ORDER BY timestamp DESC  -- Zaman damgasına göre ters sırala
        """, [username])
        notifications_data = cursor.fetchall()

    # Bildirimleri şablona aktar
    notifications = [{
        'id': notification[0],
        'title': notification[1],
        'message': notification[2],
        'timestamp': notification[3],
        'is_read': notification[4],
    } for notification in notifications_data]

    return render(request, "notifications.html", {'notifications': notifications})

def geocode_location(location):
    geolocator = Nominatim(user_agent="event_advice")
    try:
        # Geocode işlemi
        geocode_result = geolocator.geocode(location)

        # Eğer geocode sonucu varsa, koordinatları döndür
        if geocode_result:
            return (geocode_result.latitude, geocode_result.longitude)

        # Geocode edilemezse, şehrin varsayılan koordinatlarını döndür
        city_name = location.split(',')[0]  # Şehri almak için virgülden önceki kısmı alıyoruz
        city_name = city_name.strip()  # Extra boşluklardan arındırıyoruz
        if city_name in DEFAULT_CITY_COORDINATES:
            return DEFAULT_CITY_COORDINATES[city_name]

        # Eğer şehir de bulunamazsa, None döndür
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


@login_required(login_url='login')
def eventadvice(request):
    username = request.user.username
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id = cursor.fetchone()[0]

    with connection.cursor() as cursor:
        cursor.execute("SELECT ilgi_alanı FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_interest = cursor.fetchone()[0]

    with connection.cursor() as cursor:
        cursor.execute("SELECT konum FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_location = cursor.fetchone()[0]

    user_coords = geocode_location(user_location)
    if not user_coords:
        return render(request, "eventadvice.html", {"error": "Kullanıcının konumu bulunamadı."})

    # Etkinlikleri ve katılım geçmişini alıyoruz
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.etkinlik_adi, e.tarih, e.saat, e.aciklama, e.konum, e.kategori
            FROM etkinlikler e
            WHERE e.id NOT IN (
                SELECT etkinlik_id FROM katılımcılar WHERE kullanici_id = %s
            )
            AND e.tarih NOT IN (
                SELECT tarih FROM etkinlikler e2
                JOIN katılımcılar k ON e2.id = k.etkinlik_id
                WHERE k.kullanici_id = %s
            )
        """, [user_id, user_id])
        all_events = cursor.fetchall()

    # Kullanıcının en çok katıldığı kategori
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.kategori, COUNT(*) AS katilim_sayisi
            FROM etkinlikler e
            JOIN katılımcılar k ON e.id = k.etkinlik_id
            WHERE k.kullanici_id = %s
            GROUP BY e.kategori
            ORDER BY katilim_sayisi DESC
            LIMIT 1
        """, [user_id])
        most_frequent_category = cursor.fetchone()
        most_frequent_category = most_frequent_category[0] if most_frequent_category else None

    recommendations = {
        "by_interest": [],
        "by_proximity": [],
        "by_category": [],
        "best_match": None
    }
    distance_threshold = 180
    # Etkinlikleri analiz et
    for event in all_events:
        event_id, name, date, time, description, location, category = event
        event_coords = geocode_location(location)
        if not event_coords:
            continue

        # 1. Kullanıcının ilgi alanına uygun etkinlikler
        if category == user_interest:
            recommendations["by_interest"].append(event)

        # 2. Konuma göre yakınlık hesaplama
        distance = geodesic(user_coords, event_coords).kilometers
        if distance <= distance_threshold:
            recommendations["by_proximity"].append((distance, event))

        # 3. Kullanıcının en çok katıldığı kategorideki etkinlikler
        if category == most_frequent_category:
            recommendations["by_category"].append(event)

    # Yakınlık listesi sıralaması
    recommendations["by_proximity"].sort(key=lambda x: x[0])

    # En çok katıldığı kategoriye katılmadığı etkinlikleri öner
    recommendations["by_category"] = [
        event for event in recommendations["by_category"]
        if event[0] not in {e[0] for e in recommendations["by_interest"]}  # Katılmadığı etkinlikleri hariç tut
    ]

    # En iyi eşleşme: 3 kriterde de ortak olanları öner
    interest_ids = {event[0] for event in recommendations["by_interest"]}
    proximity_ids = {event[1][0] for event in recommendations["by_proximity"]}
    category_ids = {event[0] for event in recommendations["by_category"]}
    common_ids = interest_ids & proximity_ids & category_ids

    # Eğer 3 kriterde de ortak bir etkinlik yoksa, iki kriterde ortak olanları bul
    if not common_ids:
        common_ids = (interest_ids & proximity_ids) or (proximity_ids & category_ids) or (interest_ids & category_ids)

    if common_ids:
        best_event_id = next(iter(common_ids))
        recommendations["best_match"] = next(event for event in all_events if event[0] == best_event_id)

    context = {
        "recommendations": recommendations,
        "base_url": "/events/basic/"  # Detay sayfası URL'si
    }

    return render(request, "eventadvice.html", context)

@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def chats(request):
    username = request.user.username  # Oturum açmış kullanıcının kullanıcı adı

    # Kullanıcı ID'sini almak
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()

        if user_id_result:
            user_id = user_id_result[0]
        else:
            user_id = None

        if user_id:
            # Kullanıcının katıldığı etkinliklerin ID'lerini almak
            cursor.execute("""
                SELECT e.id, e.etkinlik_adi, e.kategori
                FROM etkinlikler e
                INNER JOIN katılımcılar k ON e.id = k.etkinlik_id
                WHERE k.kullanici_id = %s
            """, [user_id])
            events = cursor.fetchall()

            # Sohbet odalarını oluştur
            chat_rooms = []
            for event in events:
                event_id = event[0]
                event_name = event[1]
                event_category = event[2]

                # Her etkinliğin son mesajını almak
                cursor.execute("""
                    SELECT m.mesaj_metni, m.gonderim_zamani
                    FROM mesajlar m
                    WHERE m.etkinlik_id = %s
                    ORDER BY m.gonderim_zamani DESC
                    LIMIT 1
                """, [event_id])
                last_message = cursor.fetchone()

                if last_message:
                    last_message_text = last_message[0]
                    last_message_time = last_message[1]
                else:
                    last_message_text = "Henüz mesaj yok"
                    last_message_time = timezone.now()

                chat_rooms.append({
                    "id": event_id,
                    "name": event_name,
                    "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbWkwwhs3t-ytQ5tTc5SsMH-9IynTu67AO5w&s",  # Varsayılan görsel
                    "last_message": last_message_text,
                    "last_message_time": last_message_time,
                })
        else:
            chat_rooms = []

    return render(request, 'chats.html', {'chat_rooms': chat_rooms})


@login_required(login_url='login')  # Kullanıcı giriş kontrolü
def eventmap(request):
    # Veritabanından etkinlik verilerini alalım
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, etkinlik_adi, konum
            FROM etkinlikler
        """)

        # Sorgudan dönen sonuçları al
        events = cursor.fetchall()

    context = {
        "events": json.dumps(events)   # Etkinlikleri şablona geçiriyoruz
    }

    return render(request, "eventmap.html", context)



@login_required(login_url='login')  # Kullanıcı giriş yapmadıysa login sayfasına yönlendirir
def eventdetail(request, id):
    username = request.user.username  # Oturum açmış kullanıcının kullanıcı adı

    # Kullanıcı ID'sini almak
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()

        if user_id_result:
            user_id = user_id_result[0]
        else:
            user_id = None

        if user_id:
            # Kullanıcının katıldığı etkinliklerin detaylarını almak
            cursor.execute("""
                SELECT e.id, e.etkinlik_adi, e.aciklama, e.tarih, e.saat, e.konum, e.kategori, e.kullanici_id
                FROM etkinlikler e
                INNER JOIN katılımcılar k ON e.id = k.etkinlik_id
                WHERE k.kullanici_id = %s AND e.id = %s
            """, [user_id, id])
            event = cursor.fetchone()
        else:
            event = None

    if event:
        event_detail = {
            "id": event[0],
            "name": event[1],
            "description": event[2],
            "date": event[3],
            "time": event[4],
            "location": event[5],
            "category": event[6],
            "creator": event[7],
            "image": {
                "url": "https://img.freepik.com/free-photo/abstract-solid-shining-yellow-gradient-studio-wall-room-background_1258-88679.jpg?semt=ais_hybrid"  # Placeholder image
            }
        }
    else:
        event_detail = None  # Eğer etkinlik bulunmazsa

    return render(request, "eventdetail.html", {"event": event_detail, "user_id": user_id})



@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def chatroom(request, room_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.id, m.gonderici_id, m.mesaj_metni, m.gonderim_zamani, e.etkinlik_adi, u.ad, u.soyad, u.kullanici_adi
            FROM mesajlar m
            JOIN etkinlikler e ON m.etkinlik_id = e.id
            JOIN kullanıcılar u ON m.gonderici_id = u.kullanici_id
            WHERE e.id = %s
            ORDER BY m.gonderim_zamani ASC
        """, [room_id])
        messages = cursor.fetchall()

    # Mesajları işleme
    messages = [
        {
            'id': message[0],
            'gonderici_id': message[1],
            'mesaj_metni': message[2],
            'gonderim_zamani': message[3],
            'etkinlik_adi': message[4],
            'first_name': message[5],  # Kullanıcının ismi
            'last_name': message[6],   # Kullanıcının soyismi
            'username': message[7],    # Kullanıcı adı
        }
        for message in messages
    ]

    # Eğer mesaj yoksa etkinlik adını almak için bir sorgu yap
    if not messages:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT etkinlik_adi
                FROM etkinlikler
                WHERE id = %s
            """, [room_id])
            etkinlik_adi = cursor.fetchone()[0] if cursor.rowcount > 0 else "Bilinmeyen Etkinlik"
    else:
        etkinlik_adi = messages[0]['etkinlik_adi']

    # Oda verisi
    room = {'id': room_id, 'name': f"Etkinlik {room_id}"}

    return render(request, 'chatroom.html', {
        'messages': messages,
        'room': room,
        'etkinlik_adi': etkinlik_adi
    })


@login_required(login_url='login')
def send_message(request, room_id):
    if request.method == "POST":
        mesaj_metni = request.POST.get('message')  # Formdan gelen mesaj
        username = request.user.username  # Oturum açmış kullanıcının kullanıcı adı
        # Kullanıcı ID'sini almak
        with connection.cursor() as cursor:
            cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
            user_id_result = cursor.fetchone()
        if not mesaj_metni:
            print("Mesaj metni boş!")
            return redirect('chatroom', room_id=room_id)
        if mesaj_metni:
            print(f"Mesaj metni: {mesaj_metni}")
            # Mesajı veritabanına kaydet
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO mesajlar (gonderici_id, mesaj_metni, gonderim_zamani, etkinlik_id)
                    VALUES (%s, %s, %s, %s)
                """, [user_id_result, mesaj_metni, timezone.now(), room_id])
                #print("Mesaj veritabanına kaydedildi.")
            # Mesajı kaydettikten sonra chatroom'a yönlendir
            return redirect('chatroom', room_id=room_id)

@login_required(login_url='login')
def event_detail1(request, id):
    username = request.user.username
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id = cursor.fetchone()

    # Etkinlik verilerini al
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, etkinlik_adi, tarih, saat, aciklama, konum FROM etkinlikler WHERE id = %s", [id])
        event = cursor.fetchone()

    # Eğer etkinlik bulunamazsa 404 döndür
    if not event:
        return render(request, "404.html", status=404)

    # Kullanıcının bu etkinliğe katılıp katılmadığını kontrol et
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM katılımcılar WHERE kullanici_id = %s AND etkinlik_id = %s",
            [user_id, id]
        )
        already_joined = cursor.fetchone()[0] > 0

    # Aynı tarihte çakışan etkinlik kontrolü
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) FROM etkinlikler e
            JOIN katılımcılar k ON e.id = k.etkinlik_id
            WHERE k.kullanici_id = %s AND e.tarih = %s AND e.id != %s
            """,
            [user_id, event[2], id]
        )
        date_conflict = cursor.fetchone()[0] > 0

    # Context oluştur
    context = {
        "event": {
            "id": event[0],
            "name": event[1],
            "date": event[2],
            "time": event[3],
            "description": event[4],
            "location": event[5],
        },
        "already_joined": already_joined,
        "date_conflict": date_conflict,
    }

    return render(request, "eventdetail_basic.html", context)
@login_required
def change_profile(request):
    current_username = request.user.username

    if request.method == 'POST':
        # 'POST' ile gelen verileri al
        ad = request.POST.get('ad')
        soyad = request.POST.get('soyad')
        e_posta = request.POST.get('e_posta')
        konum = request.POST.get('konum', '')
        cinsiyet = request.POST.get('cinsiyet', '')
        foto_url = request.POST.get('foto_url', '')  # Profil fotoğrafı URL'si

        # Kullanıcı bilgilerini güncelleme sorgusu
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE kullanıcılar 
                SET 
                    e_posta = %s, 
                    konum = %s, 
                    ad = %s, 
                    soyad = %s, 
                    cinsiyet = %s, 
                    profil_fotograf = %s 
                WHERE 
                    kullanici_adi = %s;
            """, [e_posta, konum, ad, soyad, cinsiyet, foto_url, current_username])

        # Güncellenen kullanıcının ID'sini al
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kullanici_id
                FROM kullanıcılar
                WHERE kullanici_adi = %s
            """, [current_username])
            kullanici_id = cursor.fetchone()[0]

        # Kullanıcıya bildirim gönder
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO bildirimler (kullanici_id, title, message, timestamp)
                VALUES (%s, %s, %s, %s)
            """, [kullanici_id, 'Profil Güncellemesi', 'Profil bilgilerinizi başarıyla güncellediniz.', datetime.now()])

        # Başarı mesajı
        messages.success(request, "Profil bilgileri başarıyla güncellendi.")
        return redirect('change_profile')

    # Profil bilgilerini render etmek için verileri al
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ad, 
                soyad, 
                e_posta, 
                konum, 
                cinsiyet, 
                profil_fotograf
            FROM 
                kullanıcılar
            WHERE 
                kullanici_adi = %s;
        """, [current_username])

        user_data = cursor.fetchone()

    # Veriyi şablona aktar
    if user_data:
        ad, soyad, e_posta, konum, cinsiyet, profil_fotograf = user_data
    else:
        ad, soyad, e_posta, konum, cinsiyet, profil_fotograf = "", "", "", "", "", "", ""

    return render(request, 'changeprofile.html', {
        'ad': ad,
        'soyad': soyad,
        'e_posta': e_posta,
        'konum': konum,
        'cinsiyet': cinsiyet,
        'foto_url': profil_fotograf
    })

@login_required(login_url='login')
def update_event(request, id):
    username = request.user.username

    # Kullanıcı ID'sini al
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()
        user_id = user_id_result[0] if user_id_result else None

    if not user_id:
        return redirect('dashboard')

    if request.method == 'POST':
        etkinlik_adi = request.POST.get('etkinlik_adi')
        aciklama = request.POST.get('aciklama')
        tarih = request.POST.get('tarih')
        saat = request.POST.get('saat')
        konum = request.POST.get('konum')
        kategori = request.POST.get('kategori')

        # Etkinliği güncelle
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE etkinlikler
                SET etkinlik_adi = %s, aciklama = %s, tarih = %s, saat = %s, konum = %s, kategori = %s
                WHERE id = %s AND kullanici_id = %s
            """, [etkinlik_adi, aciklama, tarih, saat, konum, kategori, id, user_id])

        messages.success(request, "Etkinlik başarıyla güncellendi!")
        return redirect('eventdetail', id=id)

    # Mevcut etkinlik bilgilerini al
    with connection.cursor() as cursor:
        cursor.execute("SELECT etkinlik_adi, aciklama, tarih, saat, konum, kategori FROM etkinlikler WHERE id = %s AND kullanici_id = %s", [id, user_id])
        event = cursor.fetchone()

    if not event:
        messages.error(request, "Etkinlik bulunamadı!")
        return redirect('dashboard')

    event_detail = {
        "name": event[0],
        "description": event[1],
        "date": event[2],
        "time": event[3],
        "location": event[4],
        "category": event[5],
    }
    return render(request, "update_event.html", {"event": event_detail})

@login_required(login_url='login')
def delete_event(request, id):
    username = request.user.username

    # Kullanıcı ID'sini al
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()
        user_id = user_id_result[0] if user_id_result else None

    if not user_id:
        return redirect('events')

    # Etkinliği sil
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM etkinlikler WHERE id = %s AND kullanici_id = %s", [id, user_id])

    messages.success(request, "Etkinlik başarıyla silindi!")
    return redirect('events')

def reset_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Şifrelerin eşleşip eşleşmediğini kontrol et
        if password1 != password2:
            messages.error(request, "Şifreler eşleşmiyor.")
            return redirect("/forgot-password/")

        # Kullanıcıyı kullanıcı adı ile al
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kullanici_id, e_posta
                FROM kullanıcılar
                WHERE kullanici_adi = %s
            """, [username])
            row = cursor.fetchone()

        # Kullanıcı bulunamazsa hata mesajı göster
        if not row:
            messages.error(request, "Kullanıcı adı bulunamadı.")
            return redirect("/forgot-password/")

        # E-postanın doğruluğunu kontrol et
        if row[1] != email:
            messages.error(request, "E-posta, kullanıcı adına ait değil.")
            return redirect("/forgot-password/")

        # Şifreyi düz bir şekilde kullanıcılar tablosuna kaydet
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE kullanıcılar
                SET sifre = %s
                WHERE kullanici_id = %s
            """, [password1, row[0]])

        # Django auth_user tablosunda şifreyi hashleyerek kaydet
        hashed_password = make_password(password1)
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE auth_user
                SET password = %s
                WHERE username = %s
            """, [hashed_password, username])

        messages.success(request, "Şifreniz başarıyla değiştirildi.")
        return redirect("/login/")

    return render(request, "forgot_password.html")

@login_required(login_url='login')
def mark_notification_as_read(request, notification_id):
    # Kullanıcı adını al
    username = request.user.username

    # Kullanıcı ID'sini al
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()
        user_id = user_id_result[0] if user_id_result else None

    if user_id:
        # Bildirimi okundu olarak işaretle
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE bildirimler
                SET is_read = TRUE
                WHERE id = %s AND kullanici_id = %s
            """, [notification_id, user_id])

        # Başarı mesajı
        messages.success(request, "Bildirim başarıyla okundu olarak işaretlendi.")
    else:
        messages.error(request, "Kullanıcı bilgisi alınamadı.")
    
    return redirect('notifications')  # Bildirimler sayfasına yönlendir

@login_required(login_url='login')
def delete_notification(request, notification_id):
    # Bildirimi silme işlemi
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM bildirimler
            WHERE id = %s AND kullanici_id = (SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s)
        """, [notification_id, request.user.username])

    # Bildirim silindiğinde kullanıcıya mesaj gösterme
    messages.success(request, "Bildirim başarıyla silindi.")
    
    # Bildirimlerin listelendiği sayfaya yönlendirme
    return redirect('notifications')


@login_required(login_url='login')  # 'login' URL'ine yönlendirir
def route_planner(request, id):
    # Etkinlik verisini al
    with connection.cursor() as cursor:
        cursor.execute("SELECT etkinlik_adi, konum FROM etkinlikler WHERE id = %s", [id])
        event = cursor.fetchone()

    if not event:
        return render(request, "404.html", status=404)

    event_name, event_location = event
    start_location = request.GET.get('start_location', '')  # Başlangıç konumu varsayılan olarak boş
    transport_mode = request.GET.get('transport_mode', '')  # Ulaşım modu varsayılan olarak boş

    context = {
        "event_name": event_name,
        "event_location": event_location,
        "start_location": start_location,
        "transport_mode": transport_mode,
        "id": id,
    }

    return render(request, "route_planner.html", context)





@login_required(login_url='login')
def join_event(request, event_id):
    # Kullanıcı giriş yapmış mı kontrol edin
    if request.user.is_authenticated:
        # Giriş yapan kullanıcının ID'sini al
        current_username = request.user.username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kullanici_id 
                FROM kullanıcılar 
                WHERE kullanici_adi = %s
            """, [current_username])
            result = cursor.fetchone()
        
        # Eğer kullanıcı bulunamazsa
        if not result:
            return redirect('login')

        kullanici_id = result[0]
        

        # Katılımcılar tablosuna yeni kaydın eklenmesi
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO katılımcılar (kullanici_id, etkinlik_id)
                VALUES (%s, %s)
            """, [kullanici_id, event_id])

        # Etkinlik verilerini al
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, etkinlik_adi, tarih, saat, aciklama, konum 
                FROM etkinlikler 
                WHERE id = %s
            """, [event_id])
            event = cursor.fetchone()

       # Kullanıcıya bildirim gönder
        if event:
            etkinlik_adi = event[1]
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bildirimler (kullanici_id, title, message, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, [
                    kullanici_id,  # Bildirimi gönderilecek kullanıcı
                    'Etkinliğe Katıldınız',  # Bildirim başlığı
                    f'"{etkinlik_adi}" adlı etkinliğe başarıyla katıldınız.',  # Bildirim mesajı
                    datetime.now()  # Zaman damgası
                ])





    # Kullanıcının bu etkinliğe katılıp katılmadığını kontrol et
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM katılımcılar WHERE kullanici_id = %s AND etkinlik_id = %s",
            [kullanici_id, id]
        )
        already_joined = cursor.fetchone()[0] > 0



        # Puanlar tablosundan ilk katılım bilgisini al
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ilk_katilim
                FROM puanlar 
                WHERE kullanici_id = %s
            """, [kullanici_id])
            ilk_katilim_data = cursor.fetchone()

            if ilk_katilim_data:
                ilk_katilim = ilk_katilim_data[0]
            else:
                ilk_katilim = False  # Eğer kullanıcı için puanlar tablosunda kayıt yoksa ilk katılım False kabul edelim

        # Kullanıcıya puan ekleme işlemi
        with connection.cursor() as cursor:
            if not ilk_katilim:  # İlk katılım durumu
                bonus_puan = 20  # İlk katılım bonusu
                katilim_puani = 10  # Katılım puanı

                # Kullanıcının mevcut puanını getir
                cursor.execute("""
                    SELECT puan
                    FROM puanlar
                    WHERE kullanici_id = %s
                """, [kullanici_id])
                result = cursor.fetchone()

                if result:
                    mevcut_puan = result[0]
                    yeni_puan = mevcut_puan + bonus_puan + katilim_puani  # Bonus ve katılım puanı
                    cursor.execute("""
                        UPDATE puanlar
                        SET puan = %s, ilk_katilim = TRUE, kazanilan_tarih = %s
                        WHERE kullanici_id = %s
                    """, [yeni_puan, datetime.now(), kullanici_id])

            else:
                # Eğer daha önce katılmışsa sadece 10 puan ekle
                katilim_puani = 10
                
                cursor.execute("""
                    UPDATE puanlar
                    SET puan = puan + %s, kazanilan_tarih = %s
                    WHERE kullanici_id = %s
                """, [katilim_puani, datetime.now(), kullanici_id])



        # Context oluştur
        context = {
            "event": {
                "id": event[0],
                "name": event[1],
                "date": event[2],
                "time": event[3],
                "description": event[4],
                "location": event[5],
                
            }
        }
        messages.success(request, 'Etkinliğe katıldınız.')

        # İşlem tamamlandıktan sonra etkinlik detay sayfasına yönlendirin
        return redirect('events')

    # Kullanıcı giriş yapmamışsa login sayfasına yönlendirin
    return redirect('login')


@login_required(login_url='login')  # Giriş yapmayan kullanıcılar için yönlendirme
def leave_event(request, id):
    username = request.user.username

    # Kullanıcı ID'sini bul
    with connection.cursor() as cursor:
        cursor.execute("SELECT kullanici_ID FROM kullanıcılar WHERE kullanici_adi = %s", [username])
        user_id_result = cursor.fetchone()
        if not user_id_result:
            messages.error(request, "Kullanıcı bulunamadı.")
            return redirect('eventdetail', id=id)

        user_id = user_id_result[0]

        # Etkinlik adı ve kullanıcı katılım kontrolü
        cursor.execute("SELECT etkinlik_adi FROM etkinlikler WHERE id = %s", [id])
        event_result = cursor.fetchone()

        if not event_result:
            messages.error(request, "Etkinlik bulunamadı.")
            return redirect('eventdetail', id=id)

        event_name = event_result[0]

        cursor.execute("SELECT 1 FROM katılımcılar WHERE kullanici_id = %s AND etkinlik_id = %s", [user_id, id])
        is_participant = cursor.fetchone()

        if not is_participant:
            messages.error(request, "Etkinliğe katılımınız bulunmamaktadır.")
            return redirect('eventdetail', id=id)

        # Kullanıcıyı katılımcılar tablosundan sil
        cursor.execute("DELETE FROM katılımcılar WHERE kullanici_id = %s AND etkinlik_id = %s", [user_id, id])

        # Kullanıcının katıldığı diğer etkinlikler var mı?
        cursor.execute("SELECT COUNT(*) FROM katılımcılar WHERE kullanici_id = %s", [user_id])
        other_events_count = cursor.fetchone()[0]

        # Puan güncelleme
        if other_events_count == 0:  # Kullanıcının ilk ve tek etkinliği
            cursor.execute("""
                UPDATE puanlar
                SET puan = puan - 30, ilk_katilim = 0
                WHERE kullanici_id = %s
            """, [user_id])
        else:  # Diğer etkinliklere de katılıyorsa
            cursor.execute("""
                UPDATE puanlar
                SET puan = puan - 10
                WHERE kullanici_id = %s
            """, [user_id])

        # Kullanıcının güncel etkinlikleri kalmadıysa, kazanilan_tarih'i NULL yap
        if other_events_count == 0:
            cursor.execute("""
                UPDATE puanlar
                SET kazanilan_tarih = NULL
                WHERE kullanici_id = %s
            """, [user_id])

        # Bildirim ekle
        cursor.execute("""
            INSERT INTO bildirimler (kullanici_id, title, message, timestamp)
            VALUES (%s, %s, %s, %s)
        """, [
            user_id,  # Bildirimi gönderilecek kullanıcı
            'Etkinlikten Ayrıldınız',  # Bildirim başlığı
            f'"{event_name}" adlı etkinlikten başarıyla ayrıldınız.',  # Bildirim mesajı
            datetime.now()  # Zaman damgası
        ])

    messages.success(request, "Etkinlikten başarıyla ayrıldınız.")
    return redirect('events', id=id)