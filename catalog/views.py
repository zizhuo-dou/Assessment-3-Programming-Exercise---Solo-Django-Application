from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import login  
from django.core.paginator import Paginator

from .models import Star, Order
from .models import Favorite
from .forms import OrderForm, UserRegistrationForm
from .forms import OrderForm, UserRegistrationForm, StarCommentForm
  


def star_list(request):
    query = request.GET.get('q', '')
    constellation_filter = request.GET.get('constellation', '')
    price_filter = request.GET.get('price', '')

    stars = Star.objects.all().order_by('id')

    # 搜索关键词
    if query:
        stars = stars.filter(name__icontains=query) | stars.filter(constellation__icontains=query)

    # 星座筛选
    if constellation_filter:
        stars = stars.filter(constellation=constellation_filter)

    # 价格筛选（根据 magnitude 映射）
    if price_filter == 'high':
        stars = stars.filter(magnitude__lte=1.5)
    elif price_filter == 'mid':
        stars = stars.filter(magnitude__gt=1.5, magnitude__lte=3.5)
    elif price_filter == 'low':
        stars = stars.filter(magnitude__gt=3.5)

    # 获取所有唯一星座用于下拉框
    constellations = Star.objects.values_list('constellation', flat=True).distinct().order_by('constellation')

    confirmed_orders = Order.objects.filter(status='confirmed')
    confirmed_dict = {o.star_id: o for o in confirmed_orders}

    paginator = Paginator(stars, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/star_list.html', {
        'page_obj': page_obj,
        'confirmed_orders': confirmed_dict,
        'total_stars': stars.count(),
        'confirmed_count': confirmed_orders.count(),
        'query': query,
        'constellations': constellations,
        'selected_constellation': constellation_filter,
        'selected_price': price_filter,
    
    })



def star_detail(request, pk):
    star = get_object_or_404(Star, pk=pk)
    confirmed_order = Order.objects.filter(star=star, status='confirmed').first()
    comments = star.comments.all().order_by('-created_at') 

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = StarCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.star = star
            comment.save()
            messages.success(request, "Your comment was posted.")
            return redirect('star_detail', pk=pk)
    else:
        comment_form = StarCommentForm()

    return render(request, 'catalog/star_detail.html', {
        'star': star,
        'confirmed_order': confirmed_order,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'pending'
            order.price = 19.99
            order.save()
            messages.success(request, "Order created. Please proceed to payment.")
            return redirect('my_orders')
    else:
        form = OrderForm()
    return render(request, 'catalog/order_form.html', {'form': form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'catalog/my_orders.html', {'orders': orders})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_orders(request):
    orders = Order.objects.all()
    return render(request, 'catalog/admin_orders.html', {'orders': orders})


@login_required
def pay_for_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status == 'pending':
        order.status = 'paid'
        order.save()
        messages.success(request, "Payment successful. Awaiting admin confirmation.")
    return redirect('my_orders')


@user_passes_test(lambda u: u.is_superuser)
def confirm_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == 'paid':
        order.status = 'confirmed'
        order.save()
        messages.success(request, f"Order '{order.name_given}' confirmed.")
    return redirect('admin_orders')


@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    orders = Order.objects.all()
    stats = orders.values('star__constellation').annotate(count=Count('id'))
    return render(request, 'catalog/dashboard.html', {
        'orders': orders,
        'stats': stats
    })

@login_required
def toggle_favorite(request, star_id):
    star = get_object_or_404(Star, id=star_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, star=star)
    if not created:
        fav.delete()
        messages.info(request, f"Removed {star.name} from favorites.")
    else:
        messages.success(request, f"Added {star.name} to favorites.")
    return redirect('star_list')

@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('star')
    return render(request, 'catalog/favorites.html', {'favorites': favorites})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect('star_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'catalog/register.html', {'form': form})

def compare_stars(request):
    id1 = request.GET.get('star1')
    id2 = request.GET.get('star2')

    if not id1 or not id2 or id1 == id2:
        messages.error(request, "Please select two different stars to compare.")
        return redirect('star_list')

    star1 = get_object_or_404(Star, pk=id1)
    star2 = get_object_or_404(Star, pk=id2)

    return render(request, 'catalog/compare_stars.html', {
        'star1': star1,
        'star2': star2
    })
