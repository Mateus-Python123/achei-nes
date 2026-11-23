from django.urls import path
from . import views

app_name = "mural"

urlpatterns = [
    path(
        "",
        views.home_view,
        name="home",
    ),
    path(
        "itens/novo/",
        views.item_criar_view,
        name="item_criar",
    ),
    path(
        "itens/<int:pk>/",
        views.detalhe_view,
        name="detalhe",
    ),
    path(
        "busca/",
        views.busca_view,
        name="busca",
    ),
    path(
        "categorias/<slug:slug_categoria>/",
        views.categoria_slug_view,
        name="categoria_slug",
    ),
    path(
        "categoria/<str:nome_categoria>/",
        views.categoria_nome_view,
        name="categoria_nome",
    ),
]
