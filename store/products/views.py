from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from common.views import TitleMixin
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

from .forms import ProductFilterForm
from .models import CartItem, Product, ProductCategory


class IndexView(TitleMixin, TemplateView):
    template_name = "products/index.html"
    title = "Главная страница"


class ProductsListView(TitleMixin, ListView):
    model = Product
    template_name = "products/products.html"
    context_object_name = "products"
    paginate_by = 3
    title = "Каталог"
    form_class = ProductFilterForm

    def get_queryset(self):
        queryset = super().get_queryset()

        words_to_search = self.request.GET.get("q")
        category_filter = self.request.GET.get("category")
        min_price = self.request.GET.get("price_min")
        max_price = self.request.GET.get("price_max")
        min_rating = self.request.GET.get("min_rating")

        if words_to_search:
            queryset = queryset.filter(
                Q(title__icontains=words_to_search)
                | Q(description__icontains=words_to_search)
            )
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsListView, self).get_context_data()
        context["categories"] = ProductCategory.objects.all()
        context["form"] = self.form_class(self.request.GET)
        params = self.request.GET.copy()
        if "page" in params:
            del params["page"]
        context["params"] = "&" + params.urlencode()
        return context


@login_required
def cart_add(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_items = CartItem.objects.filter(user=request.user, product=product)

    if not cart_items.exists():
        CartItem.objects.create(user=request.user, product=product, quantity=1)
    else:
        cart_item = cart_items.first()
        cart_item.quantity += 1
        cart_item.save()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def cart_remove(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
