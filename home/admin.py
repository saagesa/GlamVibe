from django.contrib import admin
from .models import Category, Product, Review, Cart, CartItem, ContactMessage,Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_active')
    list_filter  = ('is_active',)
    search_fields = ('title', 'author')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class ReviewInline(admin.TabularInline):
    model  = Review
    extra  = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'price', 'stock', 'is_active', 'avg_rating', 'created_at')
    list_filter   = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_active')
    inlines       = [ReviewInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('user', 'product', 'rating', 'created_at')
    list_filter   = ('rating',)
    search_fields = ('user__username', 'product__name')


class CartItemInline(admin.TabularInline):
    model  = CartItem
    extra  = 0
    readonly_fields = ('product', 'quantity', 'subtotal')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total', 'updated_at')
    inlines      = [CartItemInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'topic', 'is_read', 'created_at')
    list_filter   = ('topic', 'is_read')
    search_fields = ('name', 'email')
    list_editable = ('is_read',)
    readonly_fields = ('name', 'email', 'topic', 'description', 'created_at')