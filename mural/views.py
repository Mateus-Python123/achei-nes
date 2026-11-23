from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BuscaForm, ItemForm
from .models import Categoria, Item


def home_view(request):
    contexto = {
        "lista_itens": Item.objects.all().order_by("nome"),
        "categorias": Categoria.objects.all().order_by("nome"),
    }
    return render(request, "home.html", contexto)


def detalhe_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    contexto = {"item": item}
    return render(request, "detalhe.html", contexto)


def categoria_slug_view(request, slug_categoria):
    categoria = get_object_or_404(
        Categoria,
        slug=slug_categoria,
    )

    itens = Item.objects.filter(
        categoria=categoria,
    ).order_by("nome")

    contexto = {
        "titulo_categoria": categoria.nome,
        "lista_itens": itens,
    }
    return render(request, "lista_categoria.html", contexto)


def categoria_nome_view(request, nome_categoria):
    itens = Item.objects.filter(
        categoria__nome__iexact=nome_categoria,
    ).order_by("nome")

    contexto = {
        "titulo_categoria": nome_categoria,
        "lista_itens": itens,
    }
    return render(request, "lista_categoria.html", contexto)


def item_criar_view(request):
    """GET mostra o formulário vazio; POST valida e salva (padrão Post/Redirect/Get)."""
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, "Objeto cadastrado com sucesso!")
            return redirect("mural:detalhe", pk=item.pk)
    else:
        form = ItemForm()

    return render(request, "item_form.html", {"form": form})


def busca_view(request):
    """Busca por GET: consultar não altera dados, então não usa POST."""
    form = BuscaForm(request.GET or None)
    itens = None

    if form.is_valid():
        itens = Item.objects.select_related("categoria").order_by("nome")
        termo = form.cleaned_data["termo"]
        categoria = form.cleaned_data["categoria"]

        if termo:
            itens = itens.filter(
                Q(nome__icontains=termo) | Q(descricao__icontains=termo)
            )
        if categoria:
            itens = itens.filter(categoria=categoria)

    return render(request, "busca.html", {"form": form, "lista_itens": itens})
