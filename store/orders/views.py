from http import HTTPStatus


from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
import stripe
from common.views import TitleMixin
from orders.models import Order
from products.models import CartItem

from .forms import OrderForm

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = "orders/success.html"
    title = "Спасибо за заказ"


class CanceledTemplateView(TitleMixin, TemplateView):
    template_name = "orders/canceled.html"
    title = 'Заказ отменен'


class OrderListView(TitleMixin, ListView):
    template_name = "orders/orders.html"
    title = "Заказы"
    queryset = Order.objects.all()
    ordering = "-created"
    context_object_name = "orders"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(DetailView):
    template_name = "orders/order.html"
    model = Order
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Заказ #{self.object.id}"
        return context


class OrderCreateView(TitleMixin, CreateView):
    template_name = "orders/order-create.html"
    form_class = OrderForm
    success_url = reverse_lazy("orders:create")
    title = "Оформление заказа"

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        cart_items = CartItem.objects.filter(user=self.request.user)

        checkout_session = stripe.checkout.Session.create(
            line_items=cart_items.stripe_products(),
            metadata={"order_id": self.object.id},
            mode="payment",
            success_url=f"{settings.DOMAIN_NAME}{reverse('orders:success')}",
            cancel_url=f"{settings.DOMAIN_NAME}{reverse('orders:canceled')}",
        )
        return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super().form_valid(form)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event["data"]["object"]["id"],
            expand=["line_items"],
        )

    # line_items = session.line_items
    # Fulfill the purchase...
    fulfill_order(session)

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(session):
    order_id = int(session.metadata.order_id)
    order = Order.objects.get(id=order_id)
    order.update_after_payment()
