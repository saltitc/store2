from django.urls import path

from .views import OrderCreateView, SuccessTemplateView, CanceledTemplateView, OrderListView, OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='create'),
    path('', OrderListView.as_view(), name='list'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order'),
    path('success/', SuccessTemplateView.as_view(), name='success'),
    path('canceled/', CanceledTemplateView.as_view(), name='canceled'),
    ]
