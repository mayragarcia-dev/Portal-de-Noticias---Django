# Prueba de escapado automático (Punto 12)

## Qué se guardó

En la base de datos existe la noticia publicada **«Una etiqueta HTML de prueba: `<b>esto debe verse como texto</b>`»**
(slug: `prueba-escapado-automatico`, categoría Cultura) cuyo campo `content` contiene:

```
Esta noticia sirve para comprobar el escapado automático (autoescape) de las plantillas.

El cuerpo contiene una etiqueta HTML: <b>texto en negrita</b> y además un intento de
<script>alert("esto no debe ejecutarse")</script> que Django debe convertir en texto
inofensivo en lugar de interpretarlo.

Si la página muestra los símbolos < y > tal cual, el escapado está funcionando correctamente.
```

Se puede regenerar en cualquier momento con:

```bash
python manage.py seed_news
```

## Qué muestra la página

URL: `http://127.0.0.1:8000/articulo/prueba-escapado-automatico/`

La página muestra **el texto literal** con los símbolos `<` y `>` visibles:

> El cuerpo contiene una etiqueta HTML: **`<b>`**texto en negrita**`</b>`** y además un intento de
> **`<script>`**alert("esto no debe ejecutarse")**`</script>`** …

- La etiqueta `<b>` **no produce negrita**: se ven los caracteres `<`, `b` y `>` tal cual.
- El `<script>` **no se ejecuta**: no aparece ningún `alert(...)`.

## Por qué ocurre

1. Las plantillas de Django activan **`autoescape` por defecto**: todo lo que se inserta con
   `{{ variable }}` se pasa por `django.utils.html.escape`, que convierte `&`, `<`, `>` y `"`
   en sus entidades HTML (`&amp;`, `&lt;`, `&gt;`, `&#x27;`).
2. En `templates/news/article_detail.html` el cuerpo se dibuja con
   `{{ article.content|linebreaks }}`. El filtro `linebreaks` convierte los saltos de línea en
   `<p>`/`<br>`, pero **no desactiva** el escapado: primero escapa el contenido y después aplica
   los párrafos. Por eso el HTML del autor se emite como `&lt;b&gt;` y el navegador lo pinta
   como texto en lugar de interpretarlo.
3. Es un mecanismo de seguridad: impide que un usuario inyecte `<script>` u otros HTML
   maliciosos en los campos de texto (XSS).

## Cómo se comprobó (automático)

Caso de prueba en `news/tests.py` → `EscapadoAutomaticoTestCase`:

- `test_etiqueta_html_se_muestra_como_texto`: la respuesta contiene `&lt;b&gt;etiqueta HTML&lt;/b&gt;`
  y **no** contiene `<b>etiqueta HTML</b>`.
- `test_script_no_se_ejecuta`: la respuesta contiene `&lt;script&gt;` y **no** contiene `<script>alert`.

```bash
python manage.py test news.tests.EscapadoAutomaticoTestCase
```

Evidencia HTML de la página real: `docs/evidencias/03_detalle_escape.html`.
