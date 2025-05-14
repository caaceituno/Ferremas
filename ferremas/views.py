from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.http import JsonResponse
import datetime
from .models import *
import json


# Create your views here.


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

def recover(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Aquí deberías implementar la lógica para enviar un correo de recuperación
        # Por simplicidad, solo mostramos un mensaje
        messages.success(request, 'Se ha enviado un correo de recuperación a {}'.format(email))
        
    return render(request, 'recover.html')


def index(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:   
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shopping': False}
        cartItems = order['get_cart_items']
    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'index.html', context)

def products(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:   
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shopping': False}
        cartItems = order['get_cart_items']
    
    products = Product.objects.all()
    context = {'products':products, 'cartItems': cartItems}
    return render(request, 'products.html', context)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shopping': False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'cart.html', context)

def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productID:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Producto fue agregado', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )

        
    else:
        print('Usuario no autenticado')
    return JsonResponse('Pago completado!', safe=False)
