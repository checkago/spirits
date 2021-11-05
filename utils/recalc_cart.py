from django.db import models


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Sum('qty'), models.Count('id'))
    if cart_data.get('final_price__sum', 'qty__sum'):
        cart.final_price = cart_data['final_price__sum']
        cart.qty = cart_data['qty__sum']
    else:
        cart.final_price = 0
    cart.qty = cart_data['qty__sum']
    cart.save()
