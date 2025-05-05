from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from .models import UserProfile

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # En Django, por defecto el User usa username para autenticación
        # Pero podemos buscar por email y autenticar con username
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Credenciales inválidas')
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
                
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')  # nombre
        last_name = request.POST.get('last_name')    # apellidos
        rut = request.POST.get('rut')         # rut         
        phone = request.POST.get('phone')           # celular
        password = request.POST.get('password')        # contraseña                 
        
        # Verificar si ya existe un usuario con ese email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado')
            return render(request, 'register.html')
        
        # Crear usuario (usamos email como username)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Crear perfil con campos adicionales
        UserProfile.objects.create(
            user=user,
            rut=rut,
            phone=phone
        )
        
        # Iniciar sesión y redirigir
        auth_login(request, user)
        return redirect('index')
        
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('index')
