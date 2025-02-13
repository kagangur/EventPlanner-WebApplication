from django.db import connection

def unread_notifications(request):
    if request.user.is_authenticated:
        current_username = request.user.username
        with connection.cursor() as cursor:
            # Kullanıcı ID'yi al
            cursor.execute("""
                SELECT kullanici_id
                FROM kullanıcılar
                WHERE kullanici_adi = %s
            """, [current_username])
            row = cursor.fetchone()
            if row:
                kullanici_id = row[0]
                # Okunmamış bildirim sayısını al
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM bildirimler
                    WHERE kullanici_id = %s AND is_read = FALSE
                """, [kullanici_id])
                count_row = cursor.fetchone()
                unread_count = count_row[0] if count_row else 0
                return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}