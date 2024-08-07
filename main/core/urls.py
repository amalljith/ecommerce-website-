from django.urls import include, path
from . import views 

app_name = "core"
urlpatterns = [
    #Homepage
    path('',views.home,name='home'),

    #Productpage
    path('products/',views.product_list,name='product_list'),
    path('product/details/<pid>',views.product_details,name='product_details'),

    #Category
    path('categories/',views.category_list,name='category_list'),
    path('categories/list/<cid>',views.category_product_list,name='category_product_list'),

    #Vendor
    path('vendors/',views.vendor_list,name='vendor_list'),
    path('vendors/<vid>',views.vendor_product_list,name='vendor_product_list'),
    
    #Tags
    path('product/tag/<slug:tag_slug>',views.tags,name='tags'),

    #add review

    path('add-review/<pid>/',views.ajax_addreview,name='addreview'),

    #Search
    path('search/',views.search_view,name='search'),


    # filter Product URL
    path('filter-products/',views.filter_product,name='filter-product'),

    
    # Add To Cart URL
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),


    #Cart page URL
    path('cart/',views.cart_view,name='cart'),

    #Delete item from cart
    path('delete-from-cart/',views.delete_item_from_cart,name='delete-from-cart'),

    #Update cart
    path('update-cart/',views.update_cart,name='update-from-cart'),


    #Checkout URL
    path('checkout/',views.checkout,name='checkout'),


    #Paypal Url

     path('paypal/',include('paypal.standard.ipn.urls')),
   


    #payment successfull

    path('payment-completed/',views.payment_complete_view,name='payment-completed'),

    #Payment failed
    path('payment-failed/',views.payment_failed_view,name='payment-failed'),


    #Dashboard URL
    path('dashboard/',views.dashboard,name='dashboard'),


    #Dashboard URL
    path('dashboard/order/<int:id>',views.order_details,name='order-details'),


    #Making Default Address

    path('make-default-address/',views.make_address_default,name='make-default-address'),

    #wishlist

    path('wishlist/',views.wishlist_view,name='wishlist'),

    #Adding to wishlist
    path('add-to-wishlist/',views.add_to_wishlist,name='add-to-wishlist'),

    #Removing from wishlist
    path('remove-from-wishlist/',views.remove_wishlist,name='remove-from-wishlist'),

    #Contact
    path('contact/',views.contact,name='contact'),

    path('ajax-contact-form/',views.ajax_contact_form,name='contact_form'),


]
