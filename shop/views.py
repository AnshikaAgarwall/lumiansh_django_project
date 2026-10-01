import re
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db import transaction
from django.db.models import Q, Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import Candle, Order, BulkInquiry

# Dashboard views are for active staff users only
staff_required = user_passes_test(
    lambda u: u.is_active and u.is_staff, login_url='/dashboard/login/'
)

# ─────────────────────────────────────────────
# PUBLIC VIEWS
# ─────────────────────────────────────────────

def home_landing(request):
    # Best sellers = most units ordered; newest candles fill in when there are no orders yet
    best_sellers = Candle.objects.annotate(
        sold=Coalesce(Sum('order__quantity'), 0)
    ).order_by('-sold', '-created_at')[:4]

    return render(request, 'shop/home.html', {'best_sellers': best_sellers})


def product_list(request):
    query     = request.GET.get('q')
    max_price = request.GET.get('max_price')
    candles   = Candle.objects.all().order_by('-created_at')

    if query:
        candles = candles.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if max_price:
        try:
            # Use Decimal for price filtering to match DB type
            candles = candles.filter(price__lte=Decimal(max_price))
        except (ValueError, InvalidOperation):
            pass

    return render(request, 'shop/products.html', {
        'candles': candles, 'query': query, 'max_price': max_price
    })


def place_order(request, candle_id):
    candle = get_object_or_404(Candle, id=candle_id)

    if request.method == "POST":
        name         = request.POST.get('name', '').strip()
        phone        = request.POST.get('phone', '').strip()
        email        = request.POST.get('email', '').strip()
        upi_id       = request.POST.get('upi_id', '').strip()
        address      = request.POST.get('address', '').strip()
        quantity_raw = request.POST.get('quantity', '1')

        errors = []

        if not name:
            errors.append("Please enter your full name.")

        phone_clean = re.sub(r'^(\+91|0)', '', phone)
        if not re.fullmatch(r'[6-9]\d{9}', phone_clean):
            errors.append("Please enter a valid 10-digit Indian mobile number.")

        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            errors.append("Please enter a valid email address.")

        if not re.fullmatch(r'[\w.\-]+@[\w]+', upi_id):
            errors.append("Please enter a valid UPI ID (e.g. name@paytm).")

        if not address:
            errors.append("Please enter your delivery address.")

        try:
            quantity = int(quantity_raw)
            if quantity < 1:
                errors.append("Quantity must be at least 1.")
        except ValueError:
            errors.append("Invalid quantity.")
            quantity = 1

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

        with transaction.atomic():
            # Decrement stock only if enough is left, in a single UPDATE,
            # so two simultaneous orders can never oversell.
            updated = Candle.objects.filter(
                id=candle.id, stock__gte=quantity
            ).update(stock=F('stock') - quantity)

            if not updated:
                candle.refresh_from_db()
                messages.error(request, f"Sorry, only {candle.stock} units left in stock.")
                return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

            Order.objects.create(
                candle=candle, candle_name=candle.name,
                customer_name=name, customer_phone=phone,
                customer_email=email, customer_address=address,
                upi_id=upi_id, quantity=quantity,
                total_price=candle.price * quantity,
            )

        return render(request, 'shop/success.html')

    return render(request, 'shop/buy.html', {'candle': candle})


def customer_story(request):
    return render(request, 'shop/about_customers.html')


def buy_landing(request):
    return render(request, 'shop/buy_landing.html')


def bulk_order(request):
    context = {'occasions': BulkInquiry.OCCASION_CHOICES}

    if request.method == 'POST':
        name         = request.POST.get('name', '').strip()
        company      = request.POST.get('company', '').strip()
        phone        = request.POST.get('phone', '').strip()
        email        = request.POST.get('email', '').strip()
        occasion     = request.POST.get('occasion', '')
        quantity_raw = request.POST.get('quantity', '').strip()
        needed_raw   = request.POST.get('needed_by', '').strip()
        message      = request.POST.get('message', '').strip()

        errors = []

        if not name:
            errors.append("Please enter your name.")

        phone_clean = re.sub(r'^(\+91|0)', '', phone)
        if not re.fullmatch(r'[6-9]\d{9}', phone_clean):
            errors.append("Please enter a valid 10-digit Indian mobile number.")

        if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            errors.append("Please enter a valid email address.")

        if occasion not in dict(BulkInquiry.OCCASION_CHOICES):
            errors.append("Please select an occasion.")

        try:
            quantity = int(quantity_raw)
            if quantity < 10:
                errors.append("Bulk orders start from 10 candles.")
        except ValueError:
            errors.append("Please enter how many candles you need.")
            quantity = None

        needed_by = None
        if needed_raw:
            try:
                needed_by = parse_date(needed_raw)
            except ValueError:
                pass
            if needed_by is None:
                errors.append("Please enter a valid date.")
            elif needed_by < timezone.localdate():
                errors.append("The date cannot be in the past.")

        if errors:
            for err in errors:
                messages.error(request, err)
            context['form_data'] = request.POST
            return render(request, 'shop/bulk_order.html', context)

        BulkInquiry.objects.create(
            name=name, company=company, phone=phone, email=email,
            occasion=occasion, quantity=quantity, needed_by=needed_by,
            message=message,
        )
        context['submitted'] = True

    return render(request, 'shop/bulk_order.html', context)


# ─────────────────────────────────────────────
# CUSTOM ADMIN AUTHENTICATION
# ─────────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('admin_dashboard')

        messages.error(request, "Invalid username or password, or you don't have admin access.")

    return render(request, 'shop/admin_login.html')


@require_POST
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home_landing')


# ─────────────────────────────────────────────
# CUSTOM ADMIN DASHBOARD (staff only)
# ─────────────────────────────────────────────

@staff_required
def admin_dashboard(request):
    candles      = Candle.objects.all().order_by('-created_at')
    orders       = Order.objects.select_related('candle').order_by('-created_at')[:20]
    total_orders = Order.objects.count()

    # Coalesce handles the no-orders case (SUM returns NULL)
    total_rev = Order.objects.aggregate(
        total_rev=Coalesce(Sum('total_price'), Decimal('0.00'), output_field=DecimalField())
    )['total_rev']

    low_stock = Candle.objects.filter(stock__lte=3).count()

    inquiries     = BulkInquiry.objects.order_by('-created_at')[:30]
    new_inquiries = BulkInquiry.objects.filter(status='new').count()

    return render(request, 'shop/admin_dashboard.html', {
        'candles':       candles,
        'orders':        orders,
        'total_orders':  total_orders,
        'total_rev':     total_rev,
        'low_stock':     low_stock,
        'inquiries':     inquiries,
        'new_inquiries': new_inquiries,
    })


@staff_required
def admin_product_add(request):
    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        desc      = request.POST.get('description', '').strip()
        price_raw = request.POST.get('price', '').strip()
        stock_raw = request.POST.get('stock', '0').strip()
        image_url = request.POST.get('image_url', '').strip()

        errors = []
        if not name:
            errors.append("Product name is required.")

        try:
            price = Decimal(price_raw)
            if price <= 0:
                errors.append("Price must be a positive number.")
        except (ValueError, InvalidOperation):
            errors.append("Enter a valid price.")
            price = Decimal('0.00')

        try:
            stock = int(stock_raw)
            if stock < 0:
                errors.append("Stock cannot be negative.")
        except ValueError:
            errors.append("Enter a valid stock count.")
            stock = 0

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'shop/admin_product_form.html', {
                'form_data': request.POST, 'action': 'Add'
            })

        Candle.objects.create(
            name=name, description=desc,
            price=price, stock=stock, image_url=image_url or None
        )
        messages.success(request, f'"{name}" added successfully!')
        return redirect('admin_dashboard')

    return render(request, 'shop/admin_product_form.html', {'action': 'Add'})


@staff_required
def admin_product_edit(request, candle_id):
    candle = get_object_or_404(Candle, id=candle_id)

    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        desc      = request.POST.get('description', '').strip()
        price_raw = request.POST.get('price', '').strip()
        stock_raw = request.POST.get('stock', '0').strip()
        image_url = request.POST.get('image_url', '').strip()

        errors = []
        if not name:
            errors.append("Product name is required.")

        try:
            price = Decimal(price_raw)
            if price <= 0:
                errors.append("Price must be a positive number.")
        except (ValueError, InvalidOperation):
            errors.append("Enter a valid price.")
            price = candle.price

        try:
            stock = int(stock_raw)
            if stock < 0:
                errors.append("Stock cannot be negative.")
        except ValueError:
            errors.append("Enter a valid stock count.")
            stock = candle.stock

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'shop/admin_product_form.html', {
                'candle': candle, 'form_data': request.POST, 'action': 'Edit'
            })

        candle.name        = name
        candle.description = desc
        candle.price       = price
        candle.stock       = stock
        candle.image_url   = image_url or candle.image_url
        candle.save()
        messages.success(request, f'"{name}" updated successfully!')
        return redirect('admin_dashboard')

    return render(request, 'shop/admin_product_form.html', {
        'candle': candle, 'action': 'Edit'
    })


@staff_required
@require_POST
def admin_product_delete(request, candle_id):
    candle = get_object_or_404(Candle, id=candle_id)
    name   = candle.name
    candle.delete()
    messages.success(request, f'"{name}" deleted.')
    return redirect('admin_dashboard')


@staff_required
@require_POST
def admin_order_status(request, order_id):
    order  = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.id} marked as {status}.")
    return redirect('admin_dashboard')


@staff_required
@require_POST
def admin_bulk_status(request, inquiry_id):
    inquiry = get_object_or_404(BulkInquiry, id=inquiry_id)
    status  = request.POST.get('status')
    if status in dict(BulkInquiry.STATUS_CHOICES):
        inquiry.status = status
        inquiry.save()
        messages.success(request, f"Bulk inquiry #{inquiry.id} marked as {status}.")
    return redirect(reverse('admin_dashboard') + '#bulk')
