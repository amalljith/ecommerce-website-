from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .models import Category,Tags,Vendor,Product,ProductImages,CartOrder,CartOrderItems,ProductReview,Wishlist,Address
from user_auths.models import ContactUs, Profile
from taggit.models import Tag
from django.db.models import Avg, Q, Count
from .forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages


from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from django.core import serializers

import calendar
from django.db.models.functions import ExtractMonth

def home(request):
    products = Product.objects.all()

    context ={"products":products}
    return render(request,"core/index.html",context)


def product_list(request):
    products = Product.objects.filter(product_status="published")

    context ={"products":products}
    return render(request,"core/product-list.html",context)



def category_list(request):
    category = Category.objects.all()

    context ={"category":category}
    return render(request,"core/category-list.html",context)


def category_product_list(request,cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published",category=category)

    context ={"category":category,
              "products":products
              }
    return render(request,"core/category-product-list.html",context)


def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {"vendors":vendors}

    return render(request,'core/ventor_list.html',context)


def vendor_product_list(request,vid):
    vendors = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendors,product_status="published")
    context = {"vendors":vendors,
               "products":products}

    return render(request,'core/vendor-product-list.html',context)


def product_details(request,pid):
    
    product = Product.objects.get(pid=pid)
    # product = get_object_or_404(Product,pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    # Getting all reviews related a product
    review = ProductReview.objects.filter(product=product).order_by("-date")
    
    #Getting average review
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    #product review form
    review_form = ProductReviewForm()
    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user,product=product).count()

        if user_review_count >0:
            make_review = False


    p_image = product.p_images.all()


    context = {
        "make_review":make_review,
        "p":product,
        "product":products,
        "p_image":p_image,
        "review_form":review_form,
        "average_rating":average_rating,
        "review":review,
        
    }

    return render(request,"core/product-details.html",context)


def tags(request,tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")

    tag = get_object_or_404(Tag, slug =tag_slug)
    products = products.filter(tags__in = [tag])

    context = {
        "products":products,
        "tag":tag
    }

    return render(request,"core/tag.html",context)

def ajax_addreview(request,pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user = user,
        product = product,
        review = request.POST['review'],
        rating = request.POST['rating'],

    )
    context ={
        'user':user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],

    }
    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))
    return JsonResponse(
        {
            'bool':True,
        'context':context,
        'average_reviews':average_reviews,
        }
    )


def search_view(request):
    if request.method == "GET":
            products = request.GET['searched']

            products = Product.objects.filter(Q(title__icontains=products) | Q(description__icontains=products))
           
            context = {
                
                "products": products,
               
            }

            return render(request,"core/search.html",context)




def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()


    data = render_to_string("core/ajax/product-list.html",{"products":products})
    return JsonResponse({"data":data})




def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title' : request.GET['title'],
        'qty' : request.GET['qty'],
        'price' : request.GET['price'],
        'image' : request.GET['image'],
        'pid' : request.GET['pid'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        request.session['cart_data_obj'] = cart_product
    
    return JsonResponse({"data":request.session['cart_data_obj'],'totalcartitems': len(request.session['cart_data_obj'])})



def cart_view(request):
    try:
        cart_total_amount = 0
        if len(request.session['cart_data_obj'])<=0:
            messages.info(request,"cart is emty.")
            return redirect("core:home")
        if 'cart_data_obj' in request.session:
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * int(item['price'])
            return render(request,"core/cart.html",({"cart_data":request.session['cart_data_obj'],'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount}))
        
        else:
            return render(request,"core/cart.html",{"cart_data":'','totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
    except:
        messages.info(request,"cart is emty.")
        return redirect("core:home")
        


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * int(item['price'])

    context = render_to_string("core/ajax/cart-list.html",{"cart_data":request.session['cart_data_obj'],'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
    return JsonResponse({"data":context, 'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
    
    

def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * int(item['price'])

    context = render_to_string("core/ajax/cart-list.html",{"cart_data":request.session['cart_data_obj'],'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
    return JsonResponse({"data":context, 'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
    



@login_required
def checkout(request):
    cart_total_amount = 0
    total_amount = 0
    #Checking if cart_data_obj session exists
    if 'cart_data_obj' in request.session:
        #Getting total amount for Paypal
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * int(item['price'])
        
        order = CartOrder.objects.create(
            user = request.user,
            price = total_amount

        )
        #Getting total amount for cart
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * int(item['price'])

            cart_order_products = CartOrderItems.objects.create(
                order = order,
                invoice_no = "INVOICE_NO-" + str(order.id),
                item = item['title'],
                image = item['image'],
                qty = item['qty'],
                price = item['price'],
                total = int(item['qty']) * int(item['price'])
            )

    try:
        host = request.get_host()
        paypal_dict = {
            'business':settings.PAYPAL_RECEIVER_EMAIL,
            'amount':cart_total_amount,
            'item_name':'Order-Item-No-' + str(order.id),
            'invoice':'INVOICE_NO-' + str(order.id),
            'currency_code':'USD',
            'notify_url':'http://{}{}'.format(host, reverse('core:paypal-ipn')),
            'return_url':'http://{}{}'.format(host, reverse('core:payment-completed')),
            'cancel_url':'http://{}{}'.format(host, reverse('core:payment-failed')),
        }
    except:
        messages.warning(request,"add product to cart")
        return redirect("core:home")
        
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    # cart_total_amount = 0
    # if 'cart_data_obj' in request.session:
    #     for p_id, item in request.session['cart_data_obj'].items():
    #         cart_total_amount += int(item['qty']) * int(item['price'])

    active_address = Address.objects.get(user=request.user,status=True)

    return render(request,"core/checkout.html",({"cart_data":request.session['cart_data_obj'],'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount,'paypal_payment_button':paypal_payment_button,"active_address":active_address}))

@login_required
def payment_complete_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * int(item['price'])

    return render(request,"core/payment-completed.html",({"cart_data":request.session['cart_data_obj'],'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount}))


@login_required
def payment_failed_view(request):
    return render(request,'core/payment-failed.html')

@login_required
def dashboard(request):
    order_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    profile = Profile.objects.get(user=request.user)

    orders = CartOrder.objects.annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")
    month = []
    total_order = []

    for i in orders:
        month.append(calendar.month_name[i["month"]])
        total_order.append(i['count'])

    if request.method == "POST":
        address = request.POST["address"]
        mobile = request.POST["mobile"]

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request,"Address added Successfully.")
        return redirect("core:dashboard")
   

    context = {
        "profile": profile,
        'order_list':order_list,
        "address": address,
        "orders":orders,
        "month":month,
        "total_order":total_order
        
    }
    return render(request,'core/accounts.html',context)
@login_required
def order_details(request,id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request,'core/order-details.html',context)


def make_address_default(requesst):
    id = requesst.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean":True})

@login_required
def wishlist_view(request):
    try:
        if request.user.is_authenticated:
          wishlist = Wishlist.objects.all()
        else:
            messages.warning(request,"You need to login before accessing your wishlist.")
    
    
    except:
        wishlist = 0
    
    context = {"wish":wishlist}

    return render(request,"core/wishlist.html",context)



def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    print("product id is:" + product_id)

    context = {}

    wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = Wishlist.objects.create(
            user = request.user,
            product = product,
            
        )

        context = {
            "bool":True
        }

    return JsonResponse(context)



def remove_wishlist(request):
    pid = request.GET['id']
    wishlist = Wishlist.objects.filter(user=request.user)

    product = Wishlist.objects.get(id=pid)
    product.delete()

    context = {
        "bool": True,
        "wish":wishlist
    }
    wishlist_json = serializers.serialize('json',wishlist)
    data = render_to_string("core/ajax/wishlist-list.html",context)
    return JsonResponse({"data":data,"wish":wishlist_json})


#Other Pages
def contact(request):
    return render(request,"core/contact.html")

def ajax_contact_form(request):
    full_name = request.GET["full_name"]
    email = request.GET["email"]
    phone = request.GET["phone"]
    subject = request.GET["subject"]
    message = request.GET["message"]

    contact = ContactUs.objects.create(
        full_name = full_name,
        email = email,
        phone = phone,
        subject = subject,
        message = message
    )
    context = {
        "bool": True,
        "message" : "Message send successfully"
    }
    return JsonResponse({"data":context})

def about_us(request):
    return render(request,"core/about_us.html")

def purchase_quide(request):
    return render(request,"core/purchase_quide.html")

def privacy_policy(request):
    return render(request,"core/privacy_policy.html")

def terms_of_service(request):
    return render(request,"core/terms_of_service.html")
