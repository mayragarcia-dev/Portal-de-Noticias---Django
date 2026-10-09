from pathlib import Path
from urllib.request import urlopen

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, TestCase
from django.urls import reverse

from .management.commands.seed_news import ARTICLES, CATEGORIES
from .models import Article, Author, Category

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class PlantillasTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Tecnología', description='Noticias de tecnología')
        user = User.objects.create_user(username='autor', password='x')
        cls.author = Author.objects.create(user=user, bio='Biografía de prueba')
        cls.article = Article.objects.create(
            title='Noticia de prueba',
            summary='Resumen de la noticia de prueba para la portada.',
            content='Contenido de la noticia.',
            category=cls.category,
            author=cls.author,
            status='published',
        )
        cls.client = Client()

    def test_portada_muestra_noticia_y_usa_fragmento(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noticia de prueba')
        self.assertContains(response, 'Leer más')

    def test_portada_muestra_vacio_cuando_no_hay_noticias(self):
        Article.objects.all().delete()
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No hay noticias disponibles')

    def test_listado_categoria_reutiliza_fragmento(self):
        url = reverse('news:category_detail', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Noticia de prueba')
        self.assertContains(response, 'Leer más')

    def test_detalle_hereda_de_base_y_muestra_imagen_autor_categoria(self):
        url = reverse('news:article_detail', kwargs={'slug': self.article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'news/article_detail.html')
        self.assertContains(response, self.category.name)
        self.assertContains(response, str(self.author))

    def test_rutas_tienen_nombre_propio(self):
        self.assertEqual(reverse('news:home'), '/')
        self.assertEqual(reverse('news:category_detail', kwargs={'slug': 'tec'}), '/categoria/tec/')
        self.assertEqual(reverse('news:article_detail', kwargs={'slug': 'hola'}), '/articulo/hola/')

    def test_plantillas_enlazan_con_url_sin_direcciones_a_manos(self):
        templates = PROJECT_ROOT / 'templates'
        for path in templates.rglob('*.html'):
            source = path.read_text(encoding='utf-8')
            self.assertNotIn('href="/categoria', source, f'{path.name} escribe la URL a mano')
            self.assertNotIn('href="/articulo', source, f'{path.name} escribe la URL a mano')

    def test_hoja_de_estilos_local_cargada_con_static(self):
        source = (PROJECT_ROOT / 'templates' / 'base.html').read_text(encoding='utf-8')
        self.assertIn('{% load static %}', source)
        self.assertIn("{% static 'css/styles.css' %}", source)

    def test_fragmentos_reutilizados_sin_repetir_marcado(self):
        home = (PROJECT_ROOT / 'templates' / 'news' / 'home.html').read_text(encoding='utf-8')
        category = (PROJECT_ROOT / 'templates' / 'news' / 'category_detail.html').read_text(encoding='utf-8')
        self.assertIn("{% include '_article_card.html' %}", home)
        self.assertIn("{% include '_article_card.html' %}", category)
        self.assertIn("{% include '_pagination.html' %}", home)
        self.assertIn("{% include '_pagination.html' %}", category)
        self.assertNotIn('<nav', home)
        self.assertNotIn('<nav', category)


class EstilosServidosTestCase(StaticLiveServerTestCase):
    """Punto 10: la hoja de estilos se sirve correctamente en el servidor."""

    def test_hoja_de_estilos_responde_200(self):
        with urlopen(f'{self.live_server_url}/static/css/styles.css') as response:
            self.assertEqual(response.status, 200)
            self.assertIn('text/css', response.headers.get('Content-Type', ''))
            self.assertIn('--portal-primary', response.read().decode())


class EscapadoAutomaticoTestCase(TestCase):
    """Punto 12: qué ocurre cuando el cuerpo de una noticia contiene HTML."""

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Cultura')
        user = User.objects.create_user(username='prueba', password='x')
        author = Author.objects.create(user=user)
        cls.article = Article.objects.create(
            title='Noticia con HTML',
            summary='Prueba de escapado automático.',
            content='Texto con <b>etiqueta HTML</b> y <script>alert("x")</script>.',
            category=category,
            author=author,
            status='published',
        )
        cls.client = Client()

    def test_etiqueta_html_se_muestra_como_texto(self):
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('&lt;b&gt;etiqueta HTML&lt;/b&gt;', html)
        self.assertNotIn('<b>etiqueta HTML</b>', html)

    def test_script_no_se_ejecuta(self):
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        html = response.content.decode()
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>alert', html)


class AdminTestCase(TestCase):
    """Punto 11: personalización del administrador de las tres entidades."""

    def test_admin_personalizado_en_las_tres_entidades(self):
        for model in (Article, Category, Author):
            model_admin = admin.site._registry[model]
            self.assertTrue(model_admin.list_display, f'{model.__name__} sin list_display')
            self.assertTrue(model_admin.list_filter, f'{model.__name__} sin list_filter')
            self.assertTrue(model_admin.search_fields, f'{model.__name__} sin search_fields')

    def test_admin_accesible(self):
        User.objects.create_superuser('admin2', 'a@a.com', 'pass12345')
        client = Client()
        client.login(username='admin2', password='pass12345')
        for path in ('/admin/news/article/', '/admin/news/category/', '/admin/news/author/'):
            self.assertEqual(client.get(path).status_code, 200)


class SemillaDeDatosTestCase(TestCase):
    """Punto 11: 6 noticias publicadas en 3 categorías visibles en el portal."""

    def test_seed_crea_6_noticias_en_3_categorias(self):
        from django.core.management import call_command

        call_command('seed_news')
        self.assertEqual(Category.objects.count(), len(CATEGORIES))
        self.assertEqual(Article.objects.filter(status='published').count(), len(ARTICLES))
        self.assertEqual(Author.objects.count(), 3)
        self.assertTrue(all(a.featured_image for a in Article.objects.all()))

        response = Client().get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['articles'].count(), len(ARTICLES))
