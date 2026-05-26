from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category, Review, Cart, CartItem, ContactMessage


# ── Home ─────────────────────────────────────────────────
def home(request):
    products = Product.objects.filter(is_active=True)[:3]
    return render(request, 'home/index.html', {'products': products})


# ── About ────────────────────────────────────────────────
def about(request):
    return render(request, 'home/about.html')


# ── Contact ──────────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        topic       = request.POST.get('topic', 'other')
        name        = request.POST.get('name', '').strip()
        email       = request.POST.get('email', '').strip()
        description = request.POST.get('description', '').strip()

        if name and email:
            ContactMessage.objects.create(
                topic=topic,
                name=name,
                email=email,
                description=description,
            )
            messages.success(request, 'Your message has been sent! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in your name and email.')

    return render(request, 'home/contact.html')


# ── Products ─────────────────────────────────────────────
def product_list(request):
    category_slug = request.GET.get('category')
    categories    = Category.objects.all()
    products      = Product.objects.filter(is_active=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(request, 'home/products.html', {
        'products':   products,
        'categories': categories,
        'active_cat': category_slug,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = product.reviews.select_related('user').order_by('-created_at')
    user_review = None

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    return render(request, 'home/product_detail.html', {
        'product':     product,
        'reviews':     reviews,
        'user_review': user_review,
    })


# ── Reviews ──────────────────────────────────────────────
@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        rating  = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment},
        )
        messages.success(request, 'Review submitted!')

    return redirect('product_detail', pk=pk)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    product_pk = review.product.pk
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('product_detail', pk=product_pk)


# ── Cart ─────────────────────────────────────────────────
def get_or_create_cart(request):
    """Return Cart for logged-in user, or use session for guests."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    return None


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'home/cart.html', {'cart': cart})


@login_required
def cart_add(request, pk):
    product  = get_object_or_404(Product, pk=pk, is_active=True)
    cart, _  = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f'"{product.name}" added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def cart_remove(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.delete()
    return redirect('cart')


@login_required
def cart_update(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    qty  = int(request.POST.get('quantity', 1))
    if qty > 0:
        item.quantity = qty
        item.save()
    else:
        item.delete()
    return redirect('cart')


# ── Auth ─────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, f'Welcome, {username}!')
            return redirect('home')

    return render(request, 'home/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'home/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    orders  = []  # extend later with an Order model
    reviews = Review.objects.filter(user=request.user).select_related('product')
    return render(request, 'home/profile.html', {
        'reviews': reviews,
    })

# ── FAQ ──────────────────────────────────────────────────
def faq(request):
    return render(request, 'home/faq.html')