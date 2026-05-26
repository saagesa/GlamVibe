from django.urls import path
from . import views

urlpatterns = [
    # ── Pages ──────────────────────────────────────────
    path('',            views.home,           name='home'),
    path('about/',      views.about,          name='about'),
    path('contact/',    views.contact,        name='contact'),
    path('faq/', views.faq, name='faq'),

    # ── Products ───────────────────────────────────────
    path('products/',            views.product_list,   name='products'),
    path('products/<int:pk>/',   views.product_detail, name='product_detail'),

    # ── Reviews ────────────────────────────────────────
    path('products/<int:pk>/review/',        views.add_review,    name='add_review'),
    path('reviews/<int:pk>/delete/',         views.delete_review, name='delete_review'),

    # ── Cart ───────────────────────────────────────────
    path('cart/',                    views.cart_view,   name='cart'),
    path('cart/add/<int:pk>/',       views.cart_add,    name='cart_add'),
    path('cart/remove/<int:pk>/',    views.cart_remove, name='cart_remove'),
    path('cart/update/<int:pk>/',    views.cart_update, name='cart_update'),

    # ── Auth ───────────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('profile/',  views.profile_view,  name='profile'),
]