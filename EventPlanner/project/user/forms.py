from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile  # Assuming Profile model has been created
from .models import GenelMesaj


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Mesajınızı yazın...'}), required=True)

class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    telefon_no = forms.CharField(max_length=15, required=False)
    dogum_tarihi = forms.CharField(required=False ,label="Doğum Tarihi(Yıl-Ay-Gün):")
    cinsiyet = forms.ChoiceField(choices=[('Erkek', 'Erkek'), ('Kadın', 'Kadın')], required=False)
    konum = forms.CharField(max_length=100, required=False)
    profil_fotograf = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Şifreler birbirini tutmuyor.")
        return password2

    def save(self, commit=True):
        # `User` modeline verileri kaydet
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Şifreyi hashle
        if commit:
            user.save()
        return user
    

    class MesajForm(forms.ModelForm):
       class Meta:
        model = GenelMesaj
        fields = ['mesaj_metni']

    class LoginForm(AuthenticationForm):
        username = forms.CharField(label="Kullanıcı Adı")
        password = forms.CharField(label="Şifre", widget=forms.PasswordInput)        