from django.contrib import admin
from .models import Categoria, Item


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "local_retirada")
    list_filter = ("categoria",)
    search_fields = ("nome",)