from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Product
from .cart import Cart
from .forms import CartAddForm


@require_POST
def cart_add(request,pk):
    cart = Cart(request)
    pp = get_object_or_404(Product,pk=pk)
    form = CartAddForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(pp=pp,quantity=cd['quantity'], update_quantity=cd['update'])
    return redirect('cart:cart_detail')


def cart_remove(request,pk):
    cart = Cart(request)
    pp=get_object_or_404(Product,pk=pk)
    cart.remove(pp)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    context = {'cart':cart}
    return render(request,'cart/cart_detail.html',context)






