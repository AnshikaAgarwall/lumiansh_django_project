import re
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Candle, Order

# ─────────────────────────────────────────────
# PUBLIC VIEWS
# ─────────────────────────────────────────────

def home_landing(request):
    return render(request, 'shop/home.html')


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

        phone_clean = re.sub(r'^(\+91|0)', '', phone)
        if not re.fullmatch(r'[6-9]\d{9}', phone_clean):
            errors.append("Please enter a valid 10-digit Indian mobile number.")

        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            errors.append("Please enter a valid email address.")

        if not re.fullmatch(r'[\w.\-]+@[\w]+', upi_id):
            errors.append("Please enter a valid UPI ID (e.g. name@paytm).")

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

        try:
            if candle.stock < quantity:
                messages.error(request, f"Sorry, only {candle.stock} units left in stock.")
                return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

            # Calculation using Decimal to prevent precision errors
            total_price = Decimal(candle.price) * quantity
            
            Order.objects.create(
                candle=candle, candle_name=candle.name,
                customer_name=name, customer_phone=phone,
                customer_email=email, customer_address=address,
                upi_id=upi_id, quantity=quantity, total_price=total_price
            )
            candle.stock -= quantity
            candle.save()
            return render(request, 'shop/success.html')

        except Exception:
            messages.error(request, "There was an error processing your order. Please try again.")
            return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

    return render(request, 'shop/buy.html', {'candle': candle})


def customer_story(request):
    return render(request, 'shop/about_customers.html')


def buy_landing(request):
    return render(request, 'shop/buy_landing.html')


# ─────────────────────────────────────────────
# CUSTOM ADMIN AUTHENTICATION
# ─────────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid username or password, or you don't have admin access.")
            return render(request, 'shop/admin_login.html')
            
    return render(request, 'shop/admin_login.html')


def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home_landing')


# ─────────────────────────────────────────────
# CUSTOM ADMIN DASHBOARD (staff only)
# ─────────────────────────────────────────────

@login_required(login_url='/dashboard/login/')
def admin_dashboard(request):
    candles = Candle.objects.all().order_by('-created_at')
    orders = Order.objects.select_related('candle').order_by('-created_at')[:20]
    total_orders = Order.objects.count()
    
    try:
        # We wrap the aggregation in a try block to catch database-level Decimal errors
        stats = Order.objects.aggregate(
            total_rev=Coalesce(Sum('total_price'), Decimal('0.00'), output_field=DecimalField())
        )
        total_rev = stats['total_rev']
    except (InvalidOperation, Exception):
        # Fallback: Calculate in Python if the Database/SQL sum fails
        all_prices = Order.objects.values_list('total_price', flat=True)
        total_rev = sum([Decimal(str(p)) for p in all_prices if p])

    low_stock = Candle.objects.filter(stock__lte=3).count()

    return render(request, 'shop/admin_dashboard.html', {
        'candles': candles,
        'orders': orders,
        'total_orders': total_orders,
        'total_rev': total_rev,
        'low_stock': low_stock,
    })
    candles      = Candle.objects.all().order_by('-created_at')
    orders       = Order.objects.select_related('candle').order_by('-created_at')[:20]
    total_orders = Order.objects.count()
    
    # FIX: Use Coalesce to handle empty orders and prevent Decimal crash
    stats = Order.objects.aggregate(
        total_rev=Coalesce(Sum('total_price'), Decimal('0.00'), output_field=DecimalField())
    )
    total_rev = stats['total_rev']
    
    low_stock = Candle.objects.filter(stock__lte=3).count()

    return render(request, 'shop/admin_dashboard.html', {
        'candles': candles,
        'orders':  orders,
        'total_orders': total_orders,
        'total_rev':    total_rev,
        'low_stock':    low_stock,
    })


@login_required(login_url='/dashboard/login/')
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


@login_required(login_url='/dashboard/login/')
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


@login_required(login_url='/dashboard/login/')
@require_POST
def admin_product_delete(request, candle_id):
    candle = get_object_or_404(Candle, id=candle_id)
    name   = candle.name
    candle.delete()
    messages.success(request, f'"{name}" deleted.')
    return redirect('admin_dashboard')


@login_required(login_url='/dashboard/login/')
@require_POST
def admin_order_status(request, order_id):
    order  = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.id} marked as {status}.")
    return redirect('admin_dashboard')

# import re
# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Q, Sum
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_POST
# from .models import Candle, Order
# from django.db.models.functions import Coalesce
# from django.db.models import DecimalField

# # ─────────────────────────────────────────────
# # PUBLIC VIEWS
# # ─────────────────────────────────────────────

# def home_landing(request):
#     return render(request, 'shop/home.html')


# def product_list(request):
#     query     = request.GET.get('q')
#     max_price = request.GET.get('max_price')
#     candles   = Candle.objects.all().order_by('-created_at')

#     if query:
#         candles = candles.filter(
#             Q(name__icontains=query) | Q(description__icontains=query)
#         )
#     if max_price:
#         try:
#             candles = candles.filter(price__lte=float(max_price))
#         except ValueError:
#             pass

#     return render(request, 'shop/products.html', {
#         'candles': candles, 'query': query, 'max_price': max_price
#     })


# def place_order(request, candle_id):
#     candle = get_object_or_404(Candle, id=candle_id)

#     if request.method == "POST":
#         name         = request.POST.get('name', '').strip()
#         phone        = request.POST.get('phone', '').strip()
#         email        = request.POST.get('email', '').strip()
#         upi_id       = request.POST.get('upi_id', '').strip()
#         address      = request.POST.get('address', '').strip()
#         quantity_raw = request.POST.get('quantity', '1')

#         errors = []

#         phone_clean = re.sub(r'^(\+91|0)', '', phone)
#         if not re.fullmatch(r'[6-9]\d{9}', phone_clean):
#             errors.append("Please enter a valid 10-digit Indian mobile number.")

#         if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
#             errors.append("Please enter a valid email address.")

#         if not re.fullmatch(r'[\w.\-]+@[\w]+', upi_id):
#             errors.append("Please enter a valid UPI ID (e.g. name@paytm).")

#         try:
#             quantity = int(quantity_raw)
#             if quantity < 1:
#                 errors.append("Quantity must be at least 1.")
#         except ValueError:
#             errors.append("Invalid quantity.")
#             quantity = 1

#         if errors:
#             for err in errors:
#                 messages.error(request, err)
#             return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

#         try:
#             if candle.stock < quantity:
#                 messages.error(request, f"Sorry, only {candle.stock} units left in stock.")
#                 return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

#             total_price = candle.price * quantity
#             Order.objects.create(
#                 candle=candle, candle_name=candle.name,
#                 customer_name=name, customer_phone=phone,
#                 customer_email=email, customer_address=address,
#                 upi_id=upi_id, quantity=quantity, total_price=total_price
#             )
#             candle.stock -= quantity
#             candle.save()
#             return render(request, 'shop/success.html')

#         except Exception:
#             messages.error(request, "There was an error processing your order. Please try again.")
#             return render(request, 'shop/buy.html', {'candle': candle, 'form_data': request.POST})

#     return render(request, 'shop/buy.html', {'candle': candle})


# def customer_story(request):
#     return render(request, 'shop/about_customers.html')


# def buy_landing(request):
#     return render(request, 'shop/buy_landing.html')


# from django.contrib.auth import authenticate, login, logout

# # ─────────────────────────────────────────────
# # CUSTOM ADMIN AUTHENTICATION
# # ─────────────────────────────────────────────

# def admin_login(request):
#     if request.user.is_authenticated:
#         return redirect('admin_dashboard')
    
#     if request.method == 'POST':
#         username = request.POST.get('username', '').strip()
#         password = request.POST.get('password', '').strip()
        
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None and user.is_staff:
#             login(request, user)
#             messages.success(request, f"Welcome back, {user.username}!")
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request, "Invalid username or password, or you don't have admin access.")
#             return render(request, 'shop/admin_login.html')
            
#     return render(request, 'shop/admin_login.html')


# def admin_logout(request):
#     logout(request)
#     messages.success(request, "You have been logged out.")
#     return redirect('home_landing')


# # ─────────────────────────────────────────────
# # CUSTOM ADMIN DASHBOARD  (staff only)
# # ─────────────────────────────────────────────

# @login_required(login_url='/dashboard/login/')
# def admin_dashboard(request):
#     candles      = Candle.objects.all().order_by('-created_at')
#     orders       = Order.objects.select_related('candle').order_by('-created_at')[:20]
#     total_orders = Order.objects.count()
#     total_rev    = Order.objects.aggregate(t=Sum('total_price'))['t'] or 0
#     low_stock    = Candle.objects.filter(stock__lte=3).count()

#     return render(request, 'shop/admin_dashboard.html', {
#         'candles': candles,
#         'orders':  orders,
#         'total_orders': total_orders,
#         'total_rev':    total_rev,
#         'low_stock':    low_stock,
#     })


# @login_required(login_url='/dashboard/login/')
# def admin_product_add(request):
#     if request.method == 'POST':
#         name      = request.POST.get('name', '').strip()
#         desc      = request.POST.get('description', '').strip()
#         price_raw = request.POST.get('price', '').strip()
#         stock_raw = request.POST.get('stock', '0').strip()
#         image_url = request.POST.get('image_url', '').strip()

#         errors = []
#         if not name:
#             errors.append("Product name is required.")
#         try:
#             price = float(price_raw)
#             if price <= 0:
#                 errors.append("Price must be a positive number.")
#         except ValueError:
#             errors.append("Enter a valid price.")
#             price = 0
#         try:
#             stock = int(stock_raw)
#             if stock < 0:
#                 errors.append("Stock cannot be negative.")
#         except ValueError:
#             errors.append("Enter a valid stock count.")
#             stock = 0

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             return render(request, 'shop/admin_product_form.html', {
#                 'form_data': request.POST, 'action': 'Add'
#             })

#         Candle.objects.create(
#             name=name, description=desc,
#             price=price, stock=stock, image_url=image_url or None
#         )
#         messages.success(request, f'"{name}" added successfully!')
#         return redirect('admin_dashboard')

#     return render(request, 'shop/admin_product_form.html', {'action': 'Add'})


# @login_required(login_url='/dashboard/login/')
# def admin_product_edit(request, candle_id):
#     candle = get_object_or_404(Candle, id=candle_id)

#     if request.method == 'POST':
#         name      = request.POST.get('name', '').strip()
#         desc      = request.POST.get('description', '').strip()
#         price_raw = request.POST.get('price', '').strip()
#         stock_raw = request.POST.get('stock', '0').strip()
#         image_url = request.POST.get('image_url', '').strip()

#         errors = []
#         if not name:
#             errors.append("Product name is required.")
#         try:
#             price = float(price_raw)
#             if price <= 0:
#                 errors.append("Price must be a positive number.")
#         except ValueError:
#             errors.append("Enter a valid price.")
#             price = candle.price
#         try:
#             stock = int(stock_raw)
#             if stock < 0:
#                 errors.append("Stock cannot be negative.")
#         except ValueError:
#             errors.append("Enter a valid stock count.")
#             stock = candle.stock

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             return render(request, 'shop/admin_product_form.html', {
#                 'candle': candle, 'form_data': request.POST, 'action': 'Edit'
#             })

#         candle.name        = name
#         candle.description = desc
#         candle.price       = price
#         candle.stock       = stock
#         candle.image_url   = image_url or candle.image_url
#         candle.save()
#         messages.success(request, f'"{name}" updated successfully!')
#         return redirect('admin_dashboard')

#     return render(request, 'shop/admin_product_form.html', {
#         'candle': candle, 'action': 'Edit'
#     })


# @login_required(login_url='/dashboard/login/')
# @require_POST
# def admin_product_delete(request, candle_id):
#     candle = get_object_or_404(Candle, id=candle_id)
#     name   = candle.name
#     candle.delete()
#     messages.success(request, f'"{name}" deleted.')
#     return redirect('admin_dashboard')


# @login_required(login_url='/dashboard/login/')
# @require_POST
# def admin_order_status(request, order_id):
#     order  = get_object_or_404(Order, id=order_id)
#     status = request.POST.get('status')
#     if status in dict(Order.STATUS_CHOICES):
#         order.status = status
#         order.save()
#         messages.success(request, f"Order #{order.id} marked as {status}.")
#     return redirect('admin_dashboard')