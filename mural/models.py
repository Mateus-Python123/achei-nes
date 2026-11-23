from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        return self.nome


class Item(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.TextField()
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
    )
    local_encontrado = models.CharField(max_length=120)
    local_retirada = models.CharField(max_length=120)

    def __str__(self):
        return self.nome