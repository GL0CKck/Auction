from decimal import Decimal

from django.conf import settings
from main.models import Product, Category, AdvUser


class Cart(object):
    def __init__(self,request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self,pp,quantity=1,update_quantity=False):

        pk = str(pp.pk)
        if pk not in self.cart:
            self.cart[pk] = {'quantity':0,'price':str(pp.price)}
        if update_quantity:
            self.cart[pk]['quantity'] = quantity
        else:
            self.cart[pk]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self,pp):

        pk = str(pp.pk)
        if pk in self.cart:
            del self.cart[pk]
            self.save()

    def __iter__(self):
        pp_ids = self.cart.keys()
        pps = Product.objects.filter(id__in=pp_ids)
        for pp in pps:
            self.cart[str(pp.pk)]['pp']=pp

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = False
