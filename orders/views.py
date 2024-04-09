from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.core.mail import send_mail
# Create your views here.


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # Сохранение объекта заказа без записи в базу данных
            order.save()  # Теперь объект заказа сохранен и имеет идентификатор
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # Очистка корзины
            cart.clear()
            order_created.delay(order.id)
            message="Ваш заказ успешно сформирован.\n"\
            f"Номер {order.id}."\
            f"Адрес {order.address}."\
            f"Индекс {order.postal_code}."\
            f"Город {order.city}."\
            f"На вашу почту {order.email} отправлено письмо с информацией о заказе."
            if 'email' in form.cleaned_data:
                send_mail(
                    'Заказ сформирован',
                    message,
                    'tpushopvz@outlook.com',
                    [form.cleaned_data['email']],
                    fail_silently=False,
                )
            return render(request, 'orders/created.html',
                          {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/create.html',
                  {'cart': cart, 'form': form})