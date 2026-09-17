# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ── Public ──────────────────────────────────────────────
    path('',                          views.home_landing,    name='home_landing'),
    path('shop/',                     views.product_list,    name='product_list'),
    path('our-customers/',            views.customer_story,  name='customer_story'),
    path('buy-now/',                  views.buy_landing,     name='buy_landing'),
    path('buy/<int:candle_id>/',      views.place_order,     name='place_order'),

    # ── Custom Admin Dashboard ───────────────────────────────
    path('dashboard/',                        views.admin_dashboard,      name='admin_dashboard'),
    path('dashboard/login/',                  views.admin_login,          name='admin_login'),
    path('dashboard/logout/',                 views.admin_logout,         name='admin_logout'),
    path('dashboard/product/add/',            views.admin_product_add,    name='admin_product_add'),
    path('dashboard/product/<int:candle_id>/edit/',   views.admin_product_edit,   name='admin_product_edit'),
    path('dashboard/product/<int:candle_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('dashboard/order/<int:order_id>/status/',    views.admin_order_status,   name='admin_order_status'),
]