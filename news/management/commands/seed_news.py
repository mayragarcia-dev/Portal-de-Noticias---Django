from datetime import timedelta
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from news.models import Article, Author, Category

CATEGORIES = [
    {'name': 'Tecnología', 'description': 'Noticias sobre programación, inteligencia artificial y gadgets.'},
    {'name': 'Deportes', 'description': 'Resultados, convocatorias y análisis de la actualidad deportiva.'},
    {'name': 'Cultura', 'description': 'Cine, música, literatura y arte en general.'},
]

ARTICLES = [
    {
        'title': 'Django 6.1 llega con mejoras de rendimiento',
        'category': 'Tecnología',
        'author': 'ana',
        'summary': 'La nueva versión del framework favorito de Python trae optimizaciones en consultas y una plantilla de seguridad más estricta.',
        'content': (
            'El equipo de Django ha publicado la versión 6.1, centrada en rendimiento y seguridad.\n\n'
            'Entre las novedades destacan la mejora del ORM para consultas relacionadas y nuevas '
            'opciones de caché. La comunidad ya puede probarla en entornos de desarrollo.\n\n'
            'Los proyectos existentes deberán revisar los avisos de deprecación antes de actualizar.'
        ),
        'color': (13, 110, 253),
    },
    {
        'title': 'Inteligencia artificial: cómo cambia el trabajo de los programadores',
        'category': 'Tecnología',
        'author': 'ana',
        'summary': 'Las herramientas de IA asistida ya forman parte del día a día de los equipos de desarrollo.',
        'content': (
            'La adopción de asistentes basados en inteligencia artificial ha transformado las tareas '
            'repetitivas del desarrollo de software.\n\n'
            'Los equipos que integran estas herramientas reportan revisiones de código más rápidas, '
            'aunque insisten en que la revisión humana sigue siendo imprescindible.'
        ),
        'color': (108, 117, 125),
    },
    {
        'title': 'La selección define su convocatoria para el próximo torneo',
        'category': 'Deportes',
        'author': 'luis',
        'summary': 'El cuerpo técnico anunció los nombres que acompañarán al equipo en la competición internacional.',
        'content': (
            'El seleccionador nacional dio a conocer la lista de convocados durante una rueda de prensa '
            'en la que destacó el buen momento de varios jóvenes.\n\n'
            'El equipo iniciará su preparación la próxima semana con dos sesiones diarias.'
        ),
        'color': (25, 135, 84),
    },
    {
        'title': 'Resumen de la jornada: goles y sorpresas en el campeonato local',
        'category': 'Deportes',
        'author': 'luis',
        'summary': 'Los resultados de la fecha dejaron cambios en la tabla de posiciones.',
        'content': (
            'La jornada terminó con dos victorias visitantes y un empate que complica la pelea por el '
            'liderato.\n\n'
            'El próximo fin de semana se juega la fecha decisiva con tres partidos simultáneos.'
        ),
        'color': (220, 53, 69),
    },
    {
        'title': 'El cine independiente español gana presencia en festivales',
        'category': 'Cultura',
        'author': 'maria',
        'summary': 'Tres producciones nacionales fueron seleccionadas en certámenes internacionales.',
        'content': (
            'Las películas conformadas por equipos jóvenes conquistaron al público y a la crítica '
            'en los últimos festivales.\n\n'
            'Los directores involucrados reivindican el apoyo a las salas de barrio como espacio '
            'fundamental para el sector.'
        ),
        'color': (111, 66, 193),
    },
    {
        'slug': 'prueba-escapado-automatico',
        'title': 'Una etiqueta HTML de prueba: <b>esto debe verse como texto</b>',
        'category': 'Cultura',
        'author': 'maria',
        'summary': 'Noticia de prueba del escapado automático de Django: el cuerpo contiene una etiqueta HTML que debe mostrarse literalmente.',
        'content': (
            'Esta noticia sirve para comprobar el escapado automático (autoescape) de las plantillas.\n\n'
            'El cuerpo contiene una etiqueta HTML: <b>texto en negrita</b> y además un intento de '
            '<script>alert("esto no debe ejecutarse")</script> que Django debe convertir en texto '
            'inofensivo en lugar de interpretarlo.\n\n'
            'Si la página muestra los símbolos < y > tal cual, el escapado está funcionando correctamente.'
        ),
        'color': (255, 193, 7),
    },
]


class Command(BaseCommand):
    help = 'Crea superusuario, 3 categorías, 3 autores y 6 noticias publicadas con imagen destacada.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superusuario admin/admin123 creado.'))
        else:
            self.stdout.write('El superusuario admin ya existe.')

        categorias = {}
        for item in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=item['name'],
                defaults={'description': item['description']},
            )
            categorias[cat.name] = cat

        autores = {}
        for username, full_name in [('ana', 'Ana García'), ('luis', 'Luis Pérez'), ('maria', 'María López')]:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'first_name': full_name.split()[0], 'last_name': full_name.split()[1],
                          'email': f'{username}@example.com'},
            )
            autor, _ = Author.objects.get_or_create(
                user=user,
                defaults={'bio': f'Periodista de la redacción. {full_name}.'},
            )
            autores[username] = autor

        for index, item in enumerate(ARTICLES):
            article, created = Article.objects.update_or_create(
                slug=item.get('slug') or _slugify(item['title']),
                defaults={
                    'title': item['title'],
                    'summary': item['summary'],
                    'content': item['content'],
                    'category': categorias[item['category']],
                    'author': autores[item['author']],
                    'status': 'published',
                    'published_at': timezone.now() - timedelta(days=index),
                },
            )
            if not article.featured_image:
                article.featured_image.save(
                    f'{article.slug}.png',
                    _placeholder_image(item['color'], item['title']),
                    save=False,
                )
            article.save()
            action = 'creada' if created else 'actualizada'
            self.stdout.write(self.style.SUCCESS(f'Noticia {action}: {article.title}'))

        total = Article.objects.filter(status='published').count()
        self.stdout.write(self.style.SUCCESS(f'Listo: {total} noticias publicadas en {Category.objects.count()} categorías.'))


def _slugify(text):
    from django.utils.text import slugify
    return slugify(text)


def _placeholder_image(color, title):
    from io import BytesIO

    from PIL import Image, ImageDraw

    width, height = 1200, 630
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([40, 40, width - 40, height - 40], outline=(255, 255, 255), width=6)

    text = title if len(title) <= 48 else title[:45] + '...'
    draw.text((80, height // 2 - 12), text, fill=(255, 255, 255))

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
