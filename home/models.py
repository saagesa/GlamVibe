from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Blog(models.Model):
    title      = models.CharField(max_length=200)
    slug       = models.SlugField(unique=True, blank=True)
    author     = models.CharField(max_length=100)
    content    = models.TextField()
    image      = models.ImageField(upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


# ── Category ─────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ── Product ──────────────────────────────────────────────
class Product(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    image       = models.ImageField(upload_to='products/', blank=True, null=True)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    stock       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_active     = models.BooleanField(default=True)
    is_featured   = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None


# ── Review ───────────────────────────────────────────────
class Review(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"


# ── Cart ─────────────────────────────────────────────────
class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


# ── Contact Message ──────────────────────────────────────
class ContactMessage(models.Model):
    TOPIC_CHOICES = [
        ('order',       'Order Inquiry'),
        ('product',     'Product Question'),
        ('return',      'Returns & Refunds'),
        ('partnership', 'Partnership'),
        ('other',       'Other'),
    ]

    topic       = models.CharField(max_length=20, choices=TOPIC_CHOICES, default='other')
    name        = models.CharField(max_length=150)
    email       = models.EmailField()
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_read     = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} — {self.get_topic_display()} ({self.created_at.strftime('%d %b %Y')})"