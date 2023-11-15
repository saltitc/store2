from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from common.views import TitleMixin
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST


from .forms import ProductFilterForm, RatingForm
from .models import CartItem, Product, ProductCategory, Rating


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
            queryset = queryset.filter(Q(title__icontains=words_to_search) | Q(description__icontains=words_to_search))
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


class ProductDetailView(TitleMixin, DetailView):
    title = ""
    template_name = "products/product_detail.html"
    model = Product
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        product = context["product"]
        is_rated = Rating.objects.filter(user=user, product=product).exists()

        context["is_rated"] = is_rated
        context["form"] = RatingForm
        return context


class RateProductView(FormView):
    template_name = None
    form_class = RatingForm

    def form_valid(self, form):
        messages.success(self.request, f"{self.request.user.first_name}, спасибо за оставленную вами оценку!")
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("products:detail", kwargs={"pk": self.kwargs["pk"]})


class CartView(ListView):
    model = CartItem
    template_name = "products/cart.html"
    context_object_name = "cart_items"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


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


@require_POST
def update_cart_item_quantity(request):
    try:
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")

        cart_item = CartItem.objects.get(product_id=product_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
