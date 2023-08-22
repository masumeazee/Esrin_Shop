from django.http import request
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import datetime
import json


def store(requset):

    if requset.user.is_authenticated:
        customer = requset.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0 , 'shipping' : False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems':cartItems}
    return render(requset, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0 , 'shipping' : False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(requset):
    if requset.user.is_authenticated:
        customer = requset.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0 , 'shipping' : False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(requset, 'store/checkout.html', context)

## define API
def updateItem(request):
    if request.body:
        data = json.loads(request.body)
        productId = data['productID']
        action = data['action']
        print('productId: ',productId)
        print('action: ',action)

        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()      
        if orderItem.quantity <= 0 :
            orderItem.delete()
            
        return JsonResponse('Item was added', safe=False)
    else:
        return JsonResponse('No data received', safe=False)
    
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
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],

            )    
    else:
        print('user is not logged in .. ')    
    return JsonResponse('payment complete!', safe= False)    
    
    
