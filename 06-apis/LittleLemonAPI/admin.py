from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.

"""
ユーザ名: admin
メール:admin@littlelemon.com
パスワード: lemon@789!
"""

"""
testuser
@test@test@
@test@test@

--manager--
Maneger01
    @mane@01@

Maneger02
    @mane@02@    

--delivery_crew--
Delivery01
    @deli@01@
Delivery02
    @deli@02@
Delivery03
    @deli@03@

    
    
--customer--
Customer01
    @cust@01@
Customer02
    @cust@02@
    
"""


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]


admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
