import re

from django.test import Client, TestCase
from django.urls import reverse

from .forms import BuscaForm, ItemForm
from .models import Categoria, Item


def dados_validos(cat, **extra):
    """Dados de um POST válido; os testes sobrescrevem só o que querem quebrar."""
    dados = {
        "nome": "Garrafa azul",
        "descricao": "Garrafa térmica azul com adesivo na tampa.",
        "categoria": cat.pk,
        "local_encontrado": "Quadra",
        "local_retirada": "Secretaria",
    }
    dados.update(extra)
    return dados


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.eletronicos = Categoria.objects.create(
            nome="Eletronicos", slug="eletronicos"
        )
        cls.roupas = Categoria.objects.create(nome="Roupas", slug="roupas")
        cls.fone = Item.objects.create(
            nome="Fone Preto",
            descricao="Fone de ouvido preto com fio.",
            categoria=cls.eletronicos,
            local_encontrado="Sala 2",
            local_retirada="Secretaria",
        )
        cls.casaco = Item.objects.create(
            nome="Casaco Azul",
            descricao="Casaco azul de moletom, tamanho M.",
            categoria=cls.roupas,
            local_encontrado="Quadra",
            local_retirada="Portaria",
        )


class ModelTests(BaseTestCase):
    def test_str_categoria(self):
        self.assertEqual(str(self.eletronicos), "Eletronicos")

    def test_str_item(self):
        self.assertEqual(str(self.fone), "Fone Preto")


class ItemFormTests(BaseTestCase):
    def test_form_valido(self):
        form = ItemForm(data=dados_validos(self.roupas))
        self.assertTrue(form.is_valid(), form.errors)

    def test_campos_obrigatorios(self):
        form = ItemForm(data={})
        self.assertFalse(form.is_valid())
        for campo in ItemForm.Meta.fields:
            self.assertIn(campo, form.errors)

    def test_nome_muito_curto(self):
        form = ItemForm(data=dados_validos(self.roupas, nome="ab"))
        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_descricao_muito_curta(self):
        form = ItemForm(data=dados_validos(self.roupas, descricao="curta"))
        self.assertFalse(form.is_valid())
        self.assertIn("descricao", form.errors)

    def test_categoria_inexistente(self):
        form = ItemForm(data=dados_validos(self.roupas, categoria=9999))
        self.assertFalse(form.is_valid())
        self.assertIn("categoria", form.errors)

    def test_nome_e_limpo_de_espacos(self):
        form = ItemForm(data=dados_validos(self.roupas, nome="   Mochila   "))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["nome"], "Mochila")


class BuscaFormTests(BaseTestCase):
    def test_vazio_e_valido(self):
        self.assertTrue(BuscaForm(data={}).is_valid())

    def test_termo_curto_e_invalido(self):
        form = BuscaForm(data={"termo": "a"})
        self.assertFalse(form.is_valid())
        self.assertIn("termo", form.errors)


class ViewsDeConsultaTests(BaseTestCase):
    def test_home(self):
        resposta = self.client.get(reverse("mural:home"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "FONE PRETO")
        self.assertContains(resposta, "CASACO AZUL")

    def test_detalhe(self):
        resposta = self.client.get(reverse("mural:detalhe", args=[self.fone.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Fone Preto")

    def test_detalhe_inexistente_retorna_404(self):
        resposta = self.client.get(reverse("mural:detalhe", args=[9999]))
        self.assertEqual(resposta.status_code, 404)

    def test_categoria_por_slug(self):
        resposta = self.client.get(
            reverse("mural:categoria_slug", args=["roupas"])
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "CASACO AZUL")
        self.assertNotContains(resposta, "FONE PRETO")

    def test_categoria_slug_inexistente_retorna_404(self):
        resposta = self.client.get(
            reverse("mural:categoria_slug", args=["nao-existe"])
        )
        self.assertEqual(resposta.status_code, 404)

    def test_categoria_por_nome_ignora_maiusculas(self):
        resposta = self.client.get(
            reverse("mural:categoria_nome", args=["eletronicos"])
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "FONE PRETO")


class CadastroItemTests(BaseTestCase):
    url = reverse("mural:item_criar")

    def test_get_mostra_formulario_com_csrf(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertIsInstance(resposta.context["form"], ItemForm)
        self.assertContains(resposta, "csrfmiddlewaretoken")

    def test_post_valido_cria_item_e_redireciona(self):
        resposta = self.client.post(self.url, dados_validos(self.roupas))
        item = Item.objects.get(nome="Garrafa azul")
        self.assertRedirects(
            resposta, reverse("mural:detalhe", args=[item.pk])
        )
        self.assertEqual(Item.objects.count(), 3)
        self.assertEqual(item.categoria, self.roupas)

    def test_post_valido_exibe_mensagem_de_sucesso(self):
        resposta = self.client.post(
            self.url, dados_validos(self.roupas), follow=True
        )
        self.assertContains(resposta, "Objeto cadastrado com sucesso!")

    def test_post_invalido_nao_salva_e_reexibe_formulario(self):
        resposta = self.client.post(
            self.url, dados_validos(self.roupas, nome="ab")
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("nome", resposta.context["form"].errors)
        self.assertEqual(Item.objects.count(), 2)

    def test_post_invalido_preserva_o_que_o_usuario_digitou(self):
        resposta = self.client.post(
            self.url,
            dados_validos(self.roupas, nome="ab", local_retirada="Biblioteca"),
        )
        self.assertContains(resposta, "Biblioteca")


class CsrfTests(BaseTestCase):
    """Com enforce_csrf_checks=True o Client passa a validar o token como um navegador."""

    url = reverse("mural:item_criar")

    def test_post_sem_token_e_rejeitado(self):
        client = Client(enforce_csrf_checks=True)
        resposta = client.post(self.url, dados_validos(self.roupas))
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(Item.objects.count(), 2)

    def test_post_com_token_valido_e_aceito(self):
        client = Client(enforce_csrf_checks=True)
        pagina = client.get(self.url)
        token = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            pagina.content.decode(),
        ).group(1)

        dados = dados_validos(self.roupas, csrfmiddlewaretoken=token)
        resposta = client.post(self.url, dados)

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Item.objects.count(), 3)


class BuscaViewTests(BaseTestCase):
    url = reverse("mural:busca")

    def test_sem_parametros_nao_lista_resultados(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertIsNone(resposta.context["lista_itens"])

    def test_busca_por_termo_no_nome(self):
        resposta = self.client.get(self.url, {"termo": "fone"})
        self.assertContains(resposta, "FONE PRETO")
        self.assertNotContains(resposta, "CASACO AZUL")

    def test_busca_por_termo_na_descricao(self):
        resposta = self.client.get(self.url, {"termo": "moletom"})
        self.assertContains(resposta, "CASACO AZUL")

    def test_busca_por_categoria(self):
        resposta = self.client.get(self.url, {"categoria": self.roupas.pk})
        self.assertContains(resposta, "CASACO AZUL")
        self.assertNotContains(resposta, "FONE PRETO")

    def test_busca_sem_resultado_mostra_aviso(self):
        resposta = self.client.get(self.url, {"termo": "inexistente"})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Nenhum objeto encontrado")

    def test_termo_invalido_nao_executa_busca(self):
        resposta = self.client.get(self.url, {"termo": "a"})
        self.assertEqual(resposta.status_code, 200)
        self.assertIsNone(resposta.context["lista_itens"])
