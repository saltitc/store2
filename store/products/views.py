import json
from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from common.views import TitleMixin
from django.views.generic import ListView, DetailView, FormView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ProductFilterForm, RatingForm
from .models import CartItem, Product, ProductCategory, Rating, FavoriteProduct


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
            queryset = queryset.filter(average_rating__gte=min_rating)
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
        is_rated = Rating.objects.filter(user=user.id, product=product).exists()

        context["is_rated"] = is_rated
        context["form"] = RatingForm
        return context


class RateProductView(FormView):
    template_name = None
    form_class = RatingForm

    def form_valid(self, form):
        form.save()
        if (
            self.request.headers.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
            or self.request.headers.get("x-requested-with") == "XMLHttpRequest"
        ):
            updated_rating = form.cleaned_data["product"].average_rating
            return JsonResponse(
                {
                    "success": True,
                    "updated_rating": updated_rating,
                }
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            errors = dict(form.errors.items())
            return JsonResponse({"success": False, "errors": errors})
        return response

    def get_success_url(self):
        return reverse_lazy("products:detail", kwargs={"pk": self.kwargs["pk"]})


class WishlistView(LoginRequiredMixin, ListView):
    template_name = "products/wishlist.html"
    context_object_name = "favorite_products"
    model = FavoriteProduct
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class WishlistManageView(View):
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                redirect_url = reverse_lazy("users:signin")
                return JsonResponse({"status": "not_authenticated", "redirect_url": redirect_url})
            product_id = request.POST.get("product_id")
            product = Product.objects.get(id=product_id)

            if not FavoriteProduct.objects.filter(user=request.user, product=product).exists():
                FavoriteProduct.objects.create(user=request.user, product=product)
                wishlist_items_count = FavoriteProduct.objects.filter(user=request.user).count()
                return JsonResponse({"status": "success", "wishlist_items_count": wishlist_items_count})
            else:
                return JsonResponse({"status": "already_in_favorites"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def delete(self, request, *args, **kwargs):
        try:
            product_id = json.loads(request.body)["product_id"]
            product = Product.objects.get(id=product_id)

            favorite_product = FavoriteProduct.objects.filter(user=request.user, product=product).first()

            if favorite_product:
                favorite_product.delete()
                wishlist_items_count = FavoriteProduct.objects.filter(user=request.user).count()
                return JsonResponse({"status": "success", "wishlist_items_count": wishlist_items_count})
            else:
                return JsonResponse({"status": "not_in_favorites"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class CartView(ListView):
    model = CartItem
    template_name = "products/cart.html"
    context_object_name = "cart_items"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class CartManageView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            redirect_url = reverse_lazy("users:signin")
            return JsonResponse({"status": "not_authenticated", "redirect_url": redirect_url})
        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)
        cart_items = CartItem.objects.filter(user=request.user.id, product=product_id)

        if not cart_items.exists():
            CartItem.objects.create(user=request.user, product=product, quantity=1)
        else:
            cart_item = cart_items.first()
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({"status": "success"})

    def delete(self, request, *args, **kwargs):
        pass


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
