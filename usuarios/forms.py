from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'telefono', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('Usuario o contraseña incorrectos')
            if self.user.bloqueado:
                raise forms.ValidationError('Tu cuenta está bloqueada')
        return self.cleaned_data
    
    def get_user(self):
        return self.user
    
#class ReviewForm(forms.ModelForm):
#    class Meta:
#        model = Review
#        fields = ['calificacion', 'comentario']
#        widgets = {
#            'comentario': forms.Textarea(attrs={'rows': 4}),
#        }