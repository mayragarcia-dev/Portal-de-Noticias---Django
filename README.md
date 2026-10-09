# Portal de Noticias - Django

Portal de noticias completo desarrollado con Django 6.1, que incluye gestión de artículos, categorías, autores, panel de administración y plantillas responsive con Bootstrap 5.

## Características

- **Gestión de contenido**: Artículos con imagen destacada, resumen, contenido completo, estado (borrador/publicado) y fecha de publicación
- **Categorías**: Organización temática con slugs automáticos
- **Autores**: Perfiles extendidos de usuario (bio, avatar, redes sociales)
- **Panel de administración**: Interface completa para gestión de contenido
- **Plantillas responsive**: Bootstrap 5, tarjetas reutilizables, paginación
- **Servicio de medios**: Configurado para desarrollo y producción

## Estructura del proyecto

```
Portal de Noticias - Django/
├── config/                 # Configuración principal del proyecto
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # URLs principales + media en desarrollo
│   └── wsgi.py
├── news/                   # Aplicación principal
│   ├── models.py           # Article, Category, Author
│   ├── views.py            # Class-based views (ListView, DetailView)
│   ├── urls.py             # URLs con namespace 'news'
│   ├── admin.py            # Configuración del admin
│   └── migrations/
├── templates/
│   ├── base.html           # Plantilla base con bloques
│   ├── _article_card.html  # Fragmento reutilizable tarjeta artículo
│   └── news/
│       ├── home.html       # Portada con listado paginado
│       ├── category_detail.html  # Listado por categoría
│       └── article_detail.html   # Detalle de artículo
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── media/                  # Archivos subidos por usuarios
├── manage.py
└── db.sqlite3              # Base de datos SQLite (desarrollo)
```

## Requisitos

- Python 3.11+
- Django 6.1
- Pillow (para ImageField)

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/mayragarcia-dev/Portal-de-Noticias---Django.git
cd Portal-de-Noticias---Django

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt  # Si existe, o:
pip install Django Pillow

# Aplicar migraciones
python manage.py migrate

# Cargar datos de ejemplo: superusuario admin/admin123, 3 categorías, 3 autores y 6 noticias
python manage.py seed_news

# Casos de prueba (13 tests: plantillas, URLs, static, admin, escapado automático, semilla)
python manage.py test news

# Ejecutar servidor
python manage.py runserver
```

Acceder a:
- **Portal**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/ (usuario: `admin`, contraseña: `admin123`)

## Modelos

### Category
| Campo | Tipo | Descripción |
|-------|------|-------------|
| name | CharField(100) | Nombre único |
| slug | SlugField(100) | URL amigable (auto-generado) |
| description | TextField | Descripción opcional |

### Author
| Campo | Tipo | Descripción |
|-------|------|-------------|
| user | OneToOneField(User) | Usuario Django |
| bio | TextField | Biografía |
| avatar | ImageField | Foto de perfil |
| website | URLField | Web personal |
| twitter | CharField(100) | Usuario Twitter |
| created_at | DateTimeField | Fecha creación |

### Article
| Campo | Tipo | Descripción |
|-------|------|-------------|
| title | CharField(200) | Título |
| slug | SlugField(200) | URL amigable (auto-generado) |
| summary | TextField | Resumen/extracto |
| content | TextField | Contenido completo |
| featured_image | ImageField | Imagen destacada |
| status | CharField(10) | `draft` / `published` |
| category | ForeignKey(Category) | Categoría (nullable) |
| author | ForeignKey(Author) | Autor (nullable) |
| published_at | DateTimeField | Fecha publicación |
| created_at | DateTimeField | Auto al crear |
| updated_at | DateTimeField | Auto al actualizar |

## Vistas y URLs

| Vista | URL | Nombre | Descripción |
|-------|-----|--------|-------------|
| HomeView | `/` | `news:home` | Portada con artículos publicados paginados (6 por página) |
| CategoryDetailView | `/categoria/<slug>/` | `news:category_detail` | Artículos filtrados por categoría |
| ArticleDetailView | `/articulo/<slug>/` | `news:article_detail` | Detalle completo de artículo |

Todas las vistas:
- Filtran solo `status='published'`
- Usan `select_related('category', 'author', 'author__user')` para optimizar consultas
- Pasan `categories` al contexto para la barra lateral

## Plantillas

### base.html
Estructura común con:
- Header con navegación
- Bloque `content` (col-md-8)
- Bloque `sidebar` (col-md-4) con lista de categorías
- Footer
- Bootstrap 5 via CDN
- Bloques: `title`, `content`, `sidebar`, `extra_css`, `extra_js`

### _article_card.html
Fragmento reutilizable con:
- Imagen destacada (200px height, object-fit: cover)
- Título con enlace
- Badge de categoría
- Resumen truncado a 30 palabras
- Autor y fecha de publicación
- Botón "Leer más"

### _pagination.html
Fragmento reutilizable con los controles de paginación (Anterior / Página X de Y / Siguiente).
Se incluye desde `news/home.html` y desde `news/category_detail.html` para no repetir marcado.

### news/home.html
- Extiende `base.html`
- Grid de 2 columnas (col-md-6)
- `{% for article in articles %}` con `{% empty %}` para caso sin resultados
- Reutiliza `_article_card.html` y `_pagination.html`
- Filtros: `|date:"d M Y"` y `|truncatewords:30`

### news/category_detail.html
- Igual que home pero filtrado por categoría
- Muestra nombre y descripción de la categoría
- Reutiliza `_article_card.html` y `_pagination.html`

### news/article_detail.html
- Header con categoría, título, autor y fecha
- Imagen destacada a ancho completo
- Contenido con filtro `|linebreaks`
- Botones de navegación (Inicio, Más en categoría)

### Observaciones sobre las plantillas
- **Herencia**: todas las páginas heredan de `base.html` y rellenan los bloques
  `title`, `content` y `sidebar`; el marcado común (cabecera, barra lateral, pie) se escribe una sola vez.
- **Fragmentos sin repetir marcado**: `_article_card.html` (tarjeta de noticia) y `_pagination.html`
  (paginación) se incluyen con `{% include %}` desde varias plantillas.
- **Sin lógica de negocio**: las plantillas solo recorren (`for`), condicionan (`if`/`empty`) y
  formatean (`date`, `truncatewords`, `linebreaks`); el filtrado por `status='published'` y la
  paginación se resuelven en las vistas.
- **Enlaces con `{% url %}`**: no hay direcciones escritas a mano en ninguna plantilla.
- **Escapado automático**: el contenido del artículo se pinta con `{{ article.content|linebreaks }}`;
  `autoescape` convierte el HTML en texto seguro (ver `docs/prueba_escapado_automatico.md`).
- **Contenido dinámico**: noticias, categorías y autores provienen del panel de administración;
  cambiar un dato en el panel se refleja en el sitio sin tocar plantillas.

## Panel de Administración

Registrados en `news/admin.py`:

- **Category**: list_display, prepopulated_fields (slug), search_fields
- **Author**: list_display, search_fields, raw_id_fields (user)
- **Article**: list_display, list_filter, search_fields, prepopulated_fields, raw_id_fields, date_hierarchy, ordering, fieldsets organizados en pestañas

## Configuración de Settings

```python
# Templates
TEMPLATES['DIRS'] = [BASE_DIR / 'templates']

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

En desarrollo, `config/urls.py` sirve archivos media:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Producción (notas)

1. `DEBUG = False`
2. `ALLOWED_HOSTS = ['tu-dominio.com']`
3. `SECRET_KEY` desde variable de entorno
4. Base de datos PostgreSQL/MySQL
5. `python manage.py collectstatic` → sirve `staticfiles/` con Nginx/Apache
6. Media files servidos por servidor web (no Django)

## Documentación y evidencias

- `docs/prueba_escapado_automatico.md` → punto 12: qué muestra la página con HTML en el cuerpo y por qué (autoescape).
- `docs/evidencias/` → verificación de servidores (200 en portada, categoría, detalle, CSS y media), capturas HTML de las páginas y del panel admin, y resultado de los 13 casos de prueba.

## Licencia

MIT