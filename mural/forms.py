from django import forms

from .models import Categoria, Item


class ItemForm(forms.ModelForm):
    """Cadastro de um objeto encontrado (ModelForm: gera os campos a partir do model)."""

    class Meta:
        model = Item
        fields = [
            "nome",
            "descricao",
            "categoria",
            "local_encontrado",
            "local_retirada",
        ]
        labels = {
            "nome": "Nome do objeto",
            "descricao": "Descrição",
            "categoria": "Categoria",
            "local_encontrado": "Onde foi encontrado",
            "local_retirada": "Onde retirar",
        }
        help_texts = {
            "descricao": "Cor, marca, características que ajudem o dono a reconhecer o objeto.",
        }
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Ex.: Garrafa azul"}),
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "local_encontrado": forms.TextInput(attrs={"placeholder": "Ex.: Quadra"}),
            "local_retirada": forms.TextInput(attrs={"placeholder": "Ex.: Secretaria"}),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()
        if len(nome) < 3:
            raise forms.ValidationError("O nome deve ter pelo menos 3 caracteres.")
        return nome

    def clean_descricao(self):
        descricao = self.cleaned_data["descricao"].strip()
        if len(descricao) < 10:
            raise forms.ValidationError(
                "Descreva o objeto com pelo menos 10 caracteres."
            )
        return descricao


class BuscaForm(forms.Form):
    """Formulário simples (não ligado a model) usado na busca, via GET."""

    termo = forms.CharField(
        label="Buscar por nome ou descrição",
        required=False,
        min_length=2,
        max_length=80,
    )
    categoria = forms.ModelChoiceField(
        label="Categoria",
        queryset=Categoria.objects.order_by("nome"),
        required=False,
        empty_label="Todas as categorias",
    )
