from django.contrib import admin
from .models import (
    AdvUser,
    Product,
    SubCategory,
    SuperCategory,
    SubProduct,
    SuperProduct,
    AdditionalImage,
    Tip,
)
from .forms import ProductForm, SubCategoryForm


class TipInline(admin.TabularInline):
    model = Tip


class SubProductInline(admin.TabularInline):
    model = SubProduct


class SuperProductAdmin(admin.ModelAdmin):
    exclude = ("super_product",)
    inlines = (SubProductInline,)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory


class SuperCategoryAdmin(admin.ModelAdmin):
    exclude = ("super_rubric",)
    inlines = (SubCategoryInline,)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "is_activated",
        "date_joined",
        "last_request",
        "last_login",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    fields = (
        ("username", "email"),
        ("first_name", "last_name"),
        ("is_activated", "seller", "buyer"),
        ("is_staff", "is_superuser"),
        "groups",
        "user_permissions",
        ("last_login", "date_joined", "last_request"),
    )
    readonly_fields = ("last_login", "date_joined", "last_request")


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class ProductAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "descriptions",
        "price",
        "is_active",
        ("author", "category"),
        "image",
        "deadline",
    )
    list_display = ("name", "created", "price", "is_active", "deadline")
    inlines = (AdditionalImageInline, TipInline)


class AddTip(admin.ModelAdmin):
    fields = ("product_name", "value_tip", "author", "order")
    list_display = ("product_name", "value_tip", "author", "order")


admin.site.register(SuperProduct, SuperProductAdmin)
admin.site.register(SuperCategory, SuperCategoryAdmin)
admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Tip, AddTip)
