# Resumen de Cambios del Proyecto SalesDjango

## Índice
1. [Archivos Modificados](#archivos-modificados)
2. [Archivos Creados](#archivos-creados)
3. [Detalle por Archivo](#detalle-por-archivo)

---

## Archivos Modificados

| Archivo | Tipo de cambio |
|---|---|
| `shared/mixins.py` | Agregados 3 nuevos mixins |
| `billing/views.py` | Refactorización completa de los ListViews |
| `billing/urls.py` | Actualización de 2 rutas |
| `billing/templates/billing/product_list.html` | Búsqueda, paginación y exportación |
| `billing/templates/billing/brand_list.html` | Reescrito con búsqueda, paginación y exportación |
| `billing/templates/billing/productgroup_list.html` | Reescrito con búsqueda, paginación y exportación |
| `billing/templates/billing/supplier_list.html` | Reescrito con búsqueda, paginación y exportación |
| `billing/templates/billing/customer_list.html` | Reescrito con búsqueda, paginación y exportación |
| `billing/templates/billing/invoice_list.html` | Reescrito con búsqueda, paginación y exportación |
| `requirements.txt` | Agregadas dependencias de exportación |
| `billing/templates/billing/base.html` | Modal genérico de detalle + clases CSS + función JS `showDetail()` |
| `billing/templates/billing/brand_list.html` | Agregado botón "Ver" con modal de detalle |
| `billing/templates/billing/productgroup_list.html` | Agregado botón "Ver" con modal de detalle |
| `billing/templates/billing/supplier_list.html` | Agregado botón "Ver" con modal de detalle |
| `billing/templates/billing/product_list.html` | Botón "Ver" + columna Balance |
| `billing/templates/billing/customer_list.html` | Agregado botón "Ver" con modal de detalle |
| `billing/templates/billing/invoice_list.html` | Agregado botón "Ver" con modal de detalle |
| `billing/templates/billing/invoice_detail.html` | Rediseño completo en dos columnas |
| `billing/templates/billing/product_form.html` | Rediseño completo (campos izquierda / imagen + balance derecha) |
| `billing/models.py` | Campo `photo` + propiedad `@property balance` en `Product` |
| `billing/forms.py` | Eliminado `ProductForm` e import de `Product` |
| `billing/views.py` | Import de `ProductForm`, `form_class` en Create/Update, columna Balance en `export_fields` |
| `config/settings.py` | Agregado `MEDIA_URL` y `MEDIA_ROOT` |
| `config/urls.py` | Servir archivos de media en desarrollo |

## Archivos Creados

| Archivo | Descripción |
|---|---|
| `billing/templates/billing/_pagination.html` | Partial reutilizable de paginación Bootstrap |
| `billing/templates/billing/_export_buttons.html` | Partial reutilizable de botones PDF/Excel |
| `CAMBIOS.md` | Este archivo |
| `billing/ProductForm.py` | Formulario de producto independiente con widgets, validaciones y help_texts |
| `billing/migrations/0003_add_photo_to_product.py` | Migración para el campo `photo` en el modelo `Product` |

---

## Detalle por Archivo

---

### `shared/mixins.py`

**Qué se hizo:** Se agregaron tres clases nuevas al módulo de mixins compartidos.

#### `SearchListMixin` *(nuevo)*
Mixin declarativo genérico que permite agregar búsqueda filtrada y paginación a cualquier `ListView` de Django. Cada vista solo necesita declarar `search_fields` con una lista de dicts.

Tipos de filtro soportados:

| `type` | Uso | Ejemplo |
|---|---|---|
| `text` (default) | Texto con `icontains` | `{'param': 'phone', 'field': 'phone__icontains'}` |
| `fields` (OR) | Busca en múltiples campos | `{'param': 'q', 'fields': ['name__icontains', 'email__icontains']}` |
| `bool` | Filtra `True` / `False` | `{'param': 'is_active', 'field': 'is_active', 'type': 'bool'}` |
| `number` | Filtro numérico (`gte`, `lte`) | `{'param': 'price_min', 'field': 'unit_price__gte', 'type': 'number'}` |
| `date` | Filtro de fecha | `{'param': 'date_from', 'field': 'invoice_date__date__gte', 'type': 'date'}` |

Además fija `paginate_by = 10` e inyecta `search_params` al contexto del template automáticamente.

#### `ExportMixin` *(nuevo)*
Mixin genérico que agrega exportación a PDF y Excel a cualquier `ListView`. Intercepta `?export=pdf` y `?export=excel` antes de que el `ListView` pagine, y usa `get_queryset()` para exportar **todos** los registros del filtro activo (sin paginación).

Cada vista declara:
- `export_fields`: lista de tuplas `('Cabecera', 'campo_o_callable')`. Soporta rutas con `__` (`'brand__name'`) y lambdas (`lambda obj: str(obj.customer)`).
- `export_filename`: nombre del archivo descargado (sin extensión).

**PDF** — generado con `reportlab`: landscape A4, cabecera oscura, filas alternadas, grid fino.

**Excel** — generado con `openpyxl`: cabecera estilizada, filas alternadas, ancho de columna automático.

#### `SearchExportMixin` *(nuevo)*
Hereda de `ExportMixin` y `SearchListMixin`. Es el mixin que se usa directamente en las vistas: combina búsqueda filtrada + paginación + exportación en una sola línea de herencia.

```python
class MiListView(LoginRequiredMixin, SearchExportMixin, ListView):
    search_fields = [...]
    export_fields = [...]
    export_filename = 'mi_archivo'
```

---

### `billing/views.py`

**Qué se hizo:** Refactorización completa de todos los `ListViews` para usar `SearchExportMixin`. Dos FBVs fueron convertidas a CBVs.

#### `BrandListView` *(nuevo CBV — reemplaza FBV `brand_list`)*
- Busca por: nombre, descripción, estado (activo/inactivo)
- Exporta: Nombre, Descripción, Activo

#### `ProductGroupListView` *(actualizado)*
- Antes: `ListView` simple sin búsqueda
- Ahora: `SearchExportMixin` con búsqueda por nombre y estado
- Exporta: Nombre, Activo

#### `SupplierListView` *(actualizado)*
- Antes: `ListView` simple sin búsqueda
- Ahora: `SearchExportMixin` con búsqueda por nombre/contacto/email, teléfono y estado
- Exporta: Nombre, Contacto, Email, Teléfono, Activo

#### `ProductListView` *(refactorizado)*
- Antes: `ExportMixin` + `get_queryset()` manual con ~25 líneas de código de filtrado
- Ahora: `SearchExportMixin` con `search_fields` declarativo (9 entradas) — elimina todo el código manual
- Busca por: nombre/descripción, marca, grupo, proveedor, precio (min/max), stock (min/max), estado
- El `queryset` base tiene `select_related('brand','group')` y `prefetch_related('suppliers')` para optimizar queries
- Exporta: Nombre, Descripción, Marca, Grupo, Precio, Stock, Activo

#### `CustomerListView` *(actualizado)*
- Antes: `ListView` simple sin búsqueda
- Ahora: `SearchExportMixin` con búsqueda por nombre/DNI/email y teléfono
- Exporta: DNI, Apellido, Nombre, Email, Teléfono, Activo

#### `InvoiceListView` *(nuevo CBV — reemplaza FBV `invoice_list`)*
- El `queryset` base tiene `select_related('customer')` para optimizar queries
- Busca por: nombre/DNI del cliente, rango de fechas, rango de total
- Exporta: #, Cliente (nombre completo via lambda), Fecha (formateada via lambda), Subtotal, Tax, Total

#### FBVs eliminadas
- `brand_list` — reemplazada por `BrandListView`
- `invoice_list` — reemplazada por `InvoiceListView`

> Las FBVs de creación, edición y eliminación no fueron tocadas.

---

### `billing/urls.py`

**Qué se hizo:** Dos rutas actualizadas para apuntar a los nuevos CBVs.

```python
# Antes
path('brands/',   views.brand_list,   name='brand_list'),
path('invoices/', views.invoice_list, name='invoice_list'),

# Después
path('brands/',   views.BrandListView.as_view(),   name='brand_list'),
path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
```

Los nombres de URL (`brand_list`, `invoice_list`) no cambiaron, por lo que todos los `{% url %}` del resto de templates siguen funcionando sin modificación.

---

### `billing/templates/billing/_pagination.html` *(creado)*

Partial reutilizable de paginación. Se incluye en cualquier template con:
```django
{% include 'billing/_pagination.html' %}
```

Características:
- Muestra contador de registros y "página X de Y"
- Botones: Primera `«`, Anterior `‹`, Siguiente `›`, Última `»`
- Los botones se deshabilitan (`disabled`) automáticamente en los extremos
- Los números de página se renderizan con un `<script>` inline (hijo válido de `<ul>` según el HTML spec), mostrando ±2 páginas alrededor de la actual
- Las URLs de paginación preservan todos los parámetros de búsqueda activos y excluyen `page` y `export`

---

### `billing/templates/billing/_export_buttons.html` *(creado)*

Partial reutilizable de botones de exportación. Se incluye con:
```django
{% include 'billing/_export_buttons.html' %}
```

Contiene:
- Botón **PDF** (rojo) → descarga el listado filtrado en PDF
- Botón **Excel** (verde) → descarga el listado filtrado en `.xlsx`
- Función JavaScript `exportList(fmt)` que toma la URL actual, agrega `?export=pdf/excel` y elimina `?page`, preservando todos los filtros activos

---

### Templates de lista actualizados

Los siguientes 6 templates fueron reescritos siguiendo el mismo patrón:

| Template | Campos de búsqueda |
|---|---|
| `brand_list.html` | Nombre/Descripción, Estado |
| `productgroup_list.html` | Nombre, Estado |
| `supplier_list.html` | Nombre/Contacto/Email, Teléfono, Estado |
| `product_list.html` | Nombre/Descripción, Marca, Grupo, Proveedor, Precio (min/max), Stock (min/max), Estado |
| `customer_list.html` | Nombre/DNI/Email, Teléfono, Estado |
| `invoice_list.html` | Cliente (nombre/DNI), Fecha (desde/hasta), Total (min/max) |

Todos incluyen al final:
```django
{% include 'billing/_pagination.html' %}
```

Y en la barra de acciones:
```django
{% include 'billing/_export_buttons.html' %}
```

---

### `requirements.txt`

**Qué se hizo:** Agregadas las dependencias necesarias para la exportación.

| Paquete | Versión | Uso |
|---|---|---|
| `reportlab` | 4.5.1 | Generación de archivos PDF |
| `openpyxl` | 3.1.5 | Generación de archivos Excel (`.xlsx`) |
| `pillow` | 12.2.0 | Requerido por reportlab para imágenes |
| `et-xmlfile` | 2.0.0 | Requerido por openpyxl |
| `charset-normalizer` | 3.4.7 | Dependencia transitiva |

Instalación: `pip install -r requirements.txt`

---

## Flujo de herencia de mixins

```
ListView (Django)
    ↑
SearchListMixin       → declara search_fields, paginate_by=10, search_params en contexto
    ↑
ExportMixin           → intercepta ?export=pdf/excel, genera archivo con get_queryset()
    ↑
SearchExportMixin     → combina ambos (herencia múltiple)
    ↑
LoginRequiredMixin    → verifica autenticación (dispatch)
    ↑
BrandListView         → declara search_fields, export_fields, export_filename
ProductListView
CustomerListView
...etc
```

## Cómo agregar el mixin a una nueva vista

```python
# En billing/views.py
class MiModeloListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = MiModelo
    template_name = 'billing/mimodelo_list.html'
    context_object_name = 'items'
    export_filename = 'mi_reporte'
    export_fields = [
        ('Columna 1', 'campo'),
        ('Relación',  'fk__campo'),
        ('Custom',    lambda obj: obj.metodo()),
    ]
    search_fields = [
        {'param': 'q',         'fields': ['nombre__icontains', 'email__icontains']},
        {'param': 'is_active', 'field':  'is_active', 'type': 'bool'},
        {'param': 'desde',     'field':  'fecha__date__gte', 'type': 'date'},
    ]
```

```django
{# En el template #}
{% include 'billing/_export_buttons.html' %}
{# ... tabla con datos ... #}
{% include 'billing/_pagination.html' %}
```

---

## Tarea 6 — Modal de detalle genérico + botones "Ver"

---

### `billing/templates/billing/base.html` *(modificado)*

**Qué se hizo:** Se añadió el bloque `<style>` con todas las clases CSS del modal de detalle y del formulario de producto, el HTML del modal genérico `#dmModal`, y la función JavaScript `showDetail()`.

#### Clases CSS añadidas

| Clase | Propósito |
|---|---|
| `.dm-avatar` | Círculo de 110×110 px con gradiente de color, letra inicial del registro |
| `.dm-field` | Tarjeta gris con borde izquierdo azul al hover para cada campo |
| `.dm-label` | Etiqueta de campo en mayúsculas pequeñas (0.68 rem) |
| `.dm-value` | Valor del campo en negrita (0.92 rem) |
| `.dm-divider` | Línea divisoria vertical entre columnas del modal |
| `.dm-section-label` | Encabezado de sección en formularios (0.75 rem, uppercase) |
| `.inv-card-header` | Gradiente azul `#0d6efd → #0943a8` para cabecera de tarjetas |
| `.inv-avatar` | Gradiente idéntico para el avatar de factura |
| `.btn-nav-link` | Sin subrayado para el botón Logout del navbar |
| `.pf-img-wrapper` | Zona de preview de imagen (260 px, borde punteado, hover con sombra) |
| `.pf-img-cover` | Imagen dentro del wrapper con `object-fit: cover` |
| `.pf-ph-icon` | Icono placeholder (3.5 rem) cuando no hay imagen |
| `.pf-balance` | Tarjeta con gradiente celeste para el balance dinámico |
| `.pf-balance-icon` | Icono de fondo semitransparente en la tarjeta de balance |

#### Modal `#dmModal`

Modal Bootstrap 5 genérico con dos columnas:
- **Izquierda (`#dmLeft`, `col-md-4`)**: avatar con inicial + badge Activo/Inactivo + subtítulo
- **Derecha (`#dmRight`, `col-md-8`)**: grilla de tarjetas `.dm-field` (una por campo del registro)
- **Footer**: botón opcional "Ver detalle completo" (`#dmDetailLink`) + botón Cerrar

#### Función `showDetail(btn)`

Lee atributos `data-dm-*` del botón que activa el modal:

| Atributo | Descripción |
|---|---|
| `data-dm-title` | Título del modal |
| `data-dm-subtitle` | Subtítulo bajo el badge de estado |
| `data-dm-initial` | Letra/símbolo dentro del avatar |
| `data-dm-color` | Color hexadecimal base del gradiente |
| `data-dm-active` | `"True"` / `"False"` — muestra badge verde o gris |
| `data-dm-url` | URL opcional del botón "Ver detalle completo" |
| `data-dm-f{N}l` | Etiqueta del campo N (1, 2, 3…) |
| `data-dm-f{N}v` | Valor del campo N |
| `data-dm-f{N}w` | `"1"` para que el campo ocupe ancho completo (`col-12`) |

Todas las cadenas se escapan con `esc()` antes de insertarse en `innerHTML` (prevención XSS).

La función auxiliar `adj(hex, amt)` oscurece el color base para el extremo inferior del gradiente.

---

### Templates de lista — botones "Ver" añadidos

Los 6 templates de listado recibieron un botón en la columna de acciones:

```html
<button type="button" class="btn btn-sm btn-info" onclick="showDetail(this)"
  data-dm-title="..."  data-dm-subtitle="..."
  data-dm-initial="..." data-dm-color="#..."
  data-dm-active="{{ item.is_active }}"
  data-dm-f1l="Campo 1"  data-dm-f1v="{{ item.campo1 }}"
  data-dm-f2l="Campo 2"  data-dm-f2v="{{ item.campo2 }}"
  ...
>&#128065; Ver</button>
```

Campos incluidos por módulo:

| Template | Campos en el modal |
|---|---|
| `brand_list.html` | Nombre, Estado, Creado, Actualizado, Descripción (ancho completo) |
| `productgroup_list.html` | Nombre, Estado, Creado, Actualizado |
| `supplier_list.html` | Nombre, Contacto, Email, Teléfono, Estado, Dirección (ancho completo) |
| `product_list.html` | Nombre, Marca, Grupo, Precio, Stock, Balance, Estado, Proveedores, Descripción |
| `customer_list.html` | Nombre completo, DNI, Email, Teléfono, Estado, Dirección |
| `invoice_list.html` | Cliente, Fecha, Subtotal, IVA, Total + enlace "Ver detalle completo" |

---

### `billing/templates/billing/invoice_detail.html` *(rediseñado)*

**Qué se hizo:** Rediseño completo del template en dos columnas con clases de `base.html`.

- **Columna izquierda (`col-md-3`)**: avatar `#` con `.dm-avatar .inv-avatar`, badge de fecha, hora, tarjeta resumen de totales
- **Columna derecha (`col-md-9`)**: información del cliente en tarjetas `.dm-field` + tabla responsive de productos
- Cabecera de la tarjeta con clase `.inv-card-header` (gradiente azul)
- Sin estilos inline — todos reemplazados por clases definidas en `base.html`

---

## Tarea 7 — Refactorización completa del formulario de productos

---

### `billing/ProductForm.py` *(creado)*

**Qué se hizo:** Formulario independiente `ProductForm(ModelForm)` extraído de `billing/forms.py` hacia su propio archivo.

Contiene:

#### `Meta`
- `fields`: `name`, `brand`, `group`, `unit_price`, `stock`, `suppliers`, `is_active`, `description`, `photo`
- `widgets`: todos con clases Bootstrap (`form-control`, `form-select`, `form-check-input`, etc.)
- `labels`: etiquetas en español para todos los campos
- `help_texts`: textos de ayuda para `unit_price`, `stock`, `suppliers`, `is_active`
- `error_messages`: mensajes de error personalizados para `name`, `brand`, `group`, `unit_price`

#### `__init__(self, *args, **kwargs)`
Cuando el formulario está enviado (`self.is_bound`) y un campo tiene errores, añade automáticamente la clase `is-invalid` al widget correspondiente. Esto activa el borde rojo de Bootstrap sin tocar el template.

#### `clean_unit_price(self)`
Valida que el precio sea estrictamente mayor que cero:
```python
if price is not None and price <= Decimal('0'):
    raise forms.ValidationError('El precio unitario debe ser mayor que cero.')
```

---

### `billing/models.py` *(modificado)*

**Qué se hizo:** Dos adiciones al modelo `Product`.

#### Campo `photo`
```python
photo = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Foto')
```
- Almacena imágenes en `media/products/`
- Requiere Pillow (ya en `requirements.txt`)
- Aplicado mediante migración `0003_add_photo_to_product`

#### Propiedad `balance`
```python
@property
def balance(self):
    return self.unit_price * self.stock
```
- Calculada en Python, no almacenada en base de datos
- Disponible en templates como `{{ item.balance }}`, en vistas como `p.balance`, y en exports como `lambda p: p.unit_price * p.stock`

---

### `billing/forms.py` *(modificado)*

**Qué se hizo:** Eliminado `ProductForm` y el import de `Product`. El archivo ahora solo contiene `SignUpForm`, `BrandForm`, `InvoiceForm` e `InvoiceDetailFormSet`.

---

### `config/settings.py` *(modificado)*

**Qué se hizo:** Configuración para servir archivos subidos por usuarios.

```python
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

### `config/urls.py` *(modificado)*

**Qué se hizo:** Servir archivos de `MEDIA_ROOT` durante el desarrollo.

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [...] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### `billing/views.py` *(modificado)*

**Qué se hizo:** Tres cambios relacionados con el formulario de productos.

#### Import de `ProductForm`
```python
# Antes
from .forms import SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet, ProductForm

# Después
from .forms import SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet
from .ProductForm import ProductForm
```

#### `ProductCreateView` y `ProductUpdateView`
Ambas vistas ahora usan `form_class = ProductForm` en lugar de `fields = [...]`. Esto elimina duplicación: un único formulario para crear y editar.

```python
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'billing/product_form.html'
    success_url = reverse_lazy('billing:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'billing/product_form.html'
    success_url = reverse_lazy('billing:product_list')
```

#### `ProductListView.export_fields`
Añadida la columna Balance compatible con PDF y Excel:
```python
('Balance', lambda p: p.unit_price * p.stock),
```

---

### `billing/templates/billing/product_list.html` *(modificado)*

**Qué se hizo:** Tres adiciones relacionadas con el balance.

- Nueva columna `<th class="text-end">Balance</th>` en la cabecera
- Nueva celda `<td class="text-end fw-semibold text-primary">${{ item.balance }}</td>` en cada fila
- `colspan` del mensaje vacío actualizado de 8 a 9
- Campo `f6l="Balance" f6v="${{ item.balance }}"` añadido al botón "Ver"

---

### `billing/templates/billing/product_form.html` *(rediseñado)*

**Qué se hizo:** Rediseño completo del formulario en dos columnas dentro de una tarjeta con cabecera degradada.

#### Columna izquierda `col-md-7` — Información del producto
- Badge con ID del registro (solo en modo edición)
- Campo Nombre con `form-control-lg`
- Fila Marca + Grupo (`col-sm-6` cada uno)
- Fila Precio (con `input-group has-validation` y prefijo `$`) + Stock (con sufijo `uds.`)
- Multi-select de Proveedores con texto de ayuda `Ctrl / Cmd`
- Switch Activo (`form-check form-switch`)
- Área de descripción

#### Columna derecha `col-md-5` — Imagen y Resumen
- Zona de preview clickeable (`#pfImgWrapper`, clase `.pf-img-wrapper`) — activa el `<input type="file">` oculto
- `<img id="pfImgPreview">` siempre renderizado, visible solo si hay imagen existente
- `<div id="pfPlaceholder">` siempre renderizado, visible solo si no hay imagen
- Botón visual "Seleccionar / Cambiar foto"
- Tarjeta de balance dinámico (`.pf-balance`) con desglose `$precio × N unidades`

#### JavaScript
- `FileReader` para preview inmediato al seleccionar imagen
- `updateBalance()` recalcula en tiempo real al cambiar precio o stock
- IDs de los inputs obtenidos via `{{ form.campo.auto_id }}` (no hardcoded)
- Al cargar en modo Editar, `updateBalance()` se llama inmediatamente mostrando el balance actual
