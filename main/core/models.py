from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from user_auths.models import Users
from taggit.managers import TaggableManager


STATUS_CHOICE = (
    ("process", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),

)

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),

)


def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id,filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")

    class Meta:
        verbose_name_plural = "Categories"
    
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title

class Tags(models.Model):
    pass

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path)
    cover_image = models.ImageField(upload_to=user_directory_path)
    description = models.TextField(null=True,blank=True,default='iam a vender')

    address = models.CharField(max_length=100, default="Calicut,Nadapuram")
    contact = models.CharField(max_length=100, default="+91")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")


    user = models.ForeignKey(Users,on_delete=models.SET_NULL,null=True)
    date = models.DateTimeField(auto_now_add=True,null=True,blank=True)


    class Meta:
        verbose_name_plural = "Vendors"
    
    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345")

    user = models.ForeignKey(Users,on_delete=models.SET_NULL,null=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="category")
    vendor = models.ForeignKey(Vendor,on_delete=models.SET_NULL,null=True,related_name="product")

    title = models.CharField(max_length=100, default="Fresh Pear")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True,blank=True, default="this is the product")
    price = models.IntegerField(default=1000)
    old_price = models.IntegerField(default=1000)

    


    specification = models.TextField(null=True,blank=True, default="this is the product")
    type = models.CharField(max_length=100,default="organic",null=True,blank=True)
    stoke = models.CharField(max_length=100,default="10",null=True,blank=True)
    life = models.CharField(max_length=100,default="100 Days",null=True,blank=True)
    mfd = models.DateField(auto_now_add=False,null=True,blank=True)

    tags = TaggableManager(blank=True,)

    
    # tags = models.ForeignKey(Tags,on_delete=models.SET_NULL,null=True)

    product_status = models.CharField(choices=STATUS,max_length=10, default="in_review")

    status = models.BooleanField(default=True)
    in_stoke = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=20, prefix="sku", alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True,blank=True)

    class Meta:
        verbose_name_plural = "Products"
    
    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
    def get_precentage(self):
        dics = self.old_price - self.price
        new_price = (dics / self.old_price) * 100
        return new_price


class ProductImages(models.Model):
    image = models.ImageField(upload_to="product-images",default="product.jpg")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,related_name="p_images")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"



######################## Cart, Order, OrderItems ###################################
######################## Cart, Order, OrderItems ###################################
######################## Cart, Order, OrderItems ###################################
######################## Cart, Order, OrderItems ###################################



class CartOrder(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    price = models.IntegerField(default=1000)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    
    class Meta:
        verbose_name_plural = "Cart Orders"


class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder,on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=100)
    total = models.IntegerField(default=100)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50", height="50" />' % (self.image))


######################## Product Review, Wishlists, Address ###################################
######################## Product Review, Wishlists, Address ###################################
######################## Product Review, Wishlists, Address ###################################
######################## Product Review, Wishlists, Address ###################################


class ProductReview(models.Model):
    user = models.ForeignKey(Users,on_delete=models.SET_NULL,null=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING,default=None)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Product Reviews"
    
    def __str__(self):
        return self.title
    
    def get_rating(self):
        return self.rating




class Wishlist(models.Model):
    user = models.ForeignKey(Users,on_delete=models.SET_NULL,null=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Wishlists"
    
    def __str__(self):
        return self.product.title
    
    

class Address(models.Model):
    user = models.ForeignKey(Users,on_delete=models.SET_NULL,null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"
    





    
