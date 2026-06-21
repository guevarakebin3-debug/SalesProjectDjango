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

---

## Segundo Parcial — Módulo de Compras + Rediseño de Home

---

### Archivos Creados

| Archivo | Descripción |
|---|---|
| `billing/CustomerForm.py` | Formulario centralizado de clientes con widgets, labels, help_texts, error_messages y marcado `is-invalid` |
| `billing/templates/billing/customer_form.html` | Rediseño completo en dos columnas: formulario (izq.) + vista previa en tiempo real (der.) |
| `billing/templates/billing/dashboard.html` | Panel post-login con selector de módulo Ventas / Compras y estadísticas rápidas |
| `purchasing/__init__.py` | Inicialización del app |
| `purchasing/apps.py` | Configuración `PurchasingConfig` |
| `purchasing/models.py` | Modelos `Purchase` y `PurchaseDetail` |
| `purchasing/admin.py` | `PurchaseAdmin` con `PurchaseDetailInline` (TabularInline) |
| `purchasing/forms.py` | `PurchaseForm` + `PurchaseDetailForm` + `PurchaseDetailFormSet` |
| `purchasing/views.py` | FBVs: `purchase_list`, `purchase_create`, `purchase_detail`, `purchase_delete` |
| `purchasing/urls.py` | `app_name='purchasing'`, 4 rutas bajo `/purchases/` |
| `purchasing/migrations/0001_initial.py` | Migración inicial del app purchasing |
| `purchasing/templates/purchasing/purchase_list.html` | Lista de compras con filtros de búsqueda |
| `purchasing/templates/purchasing/purchase_form.html` | Formulario con formset y cálculo de totales en tiempo real (JS) |
| `purchasing/templates/purchasing/purchase_detail.html` | Vista de detalle de compra en dos columnas |
| `purchasing/templates/purchasing/purchase_confirm_delete.html` | Confirmación de eliminación |

### Archivos Modificados

| Archivo | Cambio |
|---|---|
| `billing/views.py` | `home` pública con redirección al dashboard; nuevo `dashboard` view; `SignUpView` redirige al dashboard; import `CustomerForm` |
| `billing/urls.py` | Nueva ruta `dashboard/`; importación de `CustomerCreateView`/`CustomerUpdateView` con `form_class` |
| `billing/templates/billing/home.html` | Reemplazado completamente por landing page pública de TecnoStock S.A. |
| `billing/templates/billing/base.html` | Navbar en español; dropdown "Ventas" con submenú; enlace "Compras"; `.nav-brand-accent` en lugar de inline style |
| `billing/templates/billing/customer_list.html` | Traducida completamente al español |
| `config/settings.py` | Añadido `'purchasing'` a `INSTALLED_APPS`; `LOGIN_REDIRECT_URL = '/dashboard/'` |
| `config/urls.py` | `path('purchases/', include('purchasing.urls'))` |
| `requirements.txt` | Añadido `django-extensions==4.1` (faltaba) |

---

### `billing/CustomerForm.py` *(creado)*

Formulario análogo a `ProductForm.py`, centraliza toda la configuración del formulario de clientes.

- `fields`: `dni`, `first_name`, `last_name`, `email`, `phone`, `address`, `is_active`
- Widgets con clases Bootstrap (`form-control`, `form-check-input role="switch"`)
- Labels en español, `help_texts` para `dni` e `is_active`, `error_messages` personalizados para `dni`, `first_name`, `last_name`
- `__init__` marca `is-invalid` automáticamente en campos con errores cuando el formulario está enviado

---

### `billing/templates/billing/customer_form.html` *(rediseñado)*

Rediseño completo en dos columnas dentro de una tarjeta con cabecera degradada verde.

- **Columna izquierda `col-md-7`**: DNI, Nombres + Apellidos (fila), Email + Teléfono (fila), switch Activo, Dirección
- **Columna derecha `col-md-5`**: tarjeta de vista previa con avatar `.cf-avatar` que muestra las iniciales y actualiza los campos en tiempo real mediante JavaScript
- IIFE en `<script>` lee todos los inputs via `{{ form.campo.auto_id }}` y actualiza el preview en cada evento `input`

---

### `billing/templates/billing/home.html` *(reemplazado)*

Página pública (sin login requerido). La vista `home` redirige al dashboard si el usuario ya está autenticado.

Secciones de la landing page:
1. **Hero**: nombre TecnoStock S.A., slogan, botones Iniciar Sesión y Registrarse
2. **Nosotros**: tarjetas Misión, Visión y ¿Qué hacemos?
3. **Características**: módulo Ventas, módulo Compras, Reportes, Seguridad
4. **Contacto**: teléfono (+593 4 234-5678), dirección (Guayaquil), email (info@tecnostock.ec), redes sociales (@TecnoStockEC)

Datos de contacto ficticios solo para el ejercicio académico.

---

### `billing/templates/billing/dashboard.html` *(creado)*

Página post-login (`@login_required`) accesible en `/dashboard/`. Muestra:
- Tarjeta **Módulo de Ventas** (gradiente azul) con accesos rápidos a Facturas, Clientes, Productos
- Tarjeta **Módulo de Compras** (gradiente púrpura) con accesos rápidos a lista y nueva compra
- Fila de estadísticas: total productos, clientes, facturas y productos con stock bajo (≤5)

---

### `purchasing/models.py` *(creado)*

#### `Purchase`
| Campo | Tipo | Notas |
|---|---|---|
| `supplier` | `ForeignKey(Supplier, PROTECT)` | Importado de `billing.models` |
| `document_number` | `CharField(20)` | N° de factura/remisión del proveedor |
| `purchase_date` | `DateField(auto_now_add)` | Fecha automática de registro |
| `subtotal` | `DecimalField` | Calculado al guardar |
| `tax` | `DecimalField` | IVA 15% del subtotal |
| `total` | `DecimalField` | `subtotal + tax` |
| `is_active` | `BooleanField` | Estado del registro |

**Bonus:** `UniqueConstraint` sobre `(document_number, supplier)` → evita registrar el mismo documento dos veces para el mismo proveedor.

#### `PurchaseDetail`
| Campo | Tipo | Notas |
|---|---|---|
| `purchase` | `ForeignKey(Purchase, CASCADE)` | Elimina detalles al eliminar compra |
| `product` | `ForeignKey(Product, PROTECT)` | No permite eliminar producto con compras |
| `quantity` | `PositiveIntegerField` | Cantidad comprada |
| `unit_cost` | `DecimalField` | Costo por unidad |
| `subtotal` | `DecimalField` | Calculado en `save()`: `unit_cost × quantity` |

---

### `purchasing/views.py` *(creado)*

#### `purchase_list`
- Filtra por: texto libre (documento/proveedor), proveedor específico (select), rango de fechas
- Inyecta lista de proveedores activos al contexto para el `<select>` de filtros

#### `purchase_create`
1. Valida `PurchaseForm` + `PurchaseDetailFormSet` juntos
2. Guarda la compra, asocia el formset, calcula subtotal/IVA/total
3. **Bonus stock**: por cada `PurchaseDetail` guardado, ejecuta `Product.objects.filter(pk=...).update(stock=F('stock') + quantity)` — usa expresión `F()` para actualizar atómicamente

#### `purchase_detail`
- Usa `select_related('supplier')` + `prefetch_related('details__product')` para optimizar queries

#### `purchase_delete`
- Elimina por `POST`; los detalles se eliminan en cascada automáticamente
- **Nota al usuario**: el stock actualizado al crear no se revierte al eliminar (indicado en el template)

---

### `purchasing/forms.py` *(creado)*

- `PurchaseForm`: campos `supplier` y `document_number` con widgets Bootstrap y validación de unicidad
- `PurchaseDetailForm`: campos `product`, `quantity`, `unit_cost` con clases CSS funcionales (`pd-product`, `pd-qty`, `pd-cost`) usadas por el JavaScript del formulario
- `PurchaseDetailFormSet = inlineformset_factory(Purchase, PurchaseDetail, extra=1, min_num=1, validate_min=True, can_delete=True)`

---

### `purchasing/templates/purchasing/purchase_form.html` *(creado)*

Formulario en dos cards:
1. **Datos de la Compra**: proveedor + N° documento (cabecera púrpura)
2. **Detalle de Productos**: tabla formset con columnas Producto / Cantidad / Costo Unit. / Subtotal / Quitar

#### JavaScript (IIFE)
- `recalcRow(row)` → calcula `qty × cost` para cada fila, actualiza celda `.line-sub`
- `recalcAll()` → suma todas las filas, calcula IVA 15%, actualiza `#summary-sub`, `#summary-tax`, `#summary-total`
- Botón **"+ Agregar Fila"** → clona la primera `<tr>`, reindexiza los campos (`details-N-campo`), limpia valores y actualiza `TOTAL_FORMS`
- Botón **"✕"** → elimina la fila (mínimo 1 fila protegida) y recalcula totales
- Todos los eventos delegados sobre `tbody` para funcionar con filas dinámicas

---

## Mejoras de UX — Modo Oscuro + Botón Editar en Modal

---

### Archivos Modificados

| Archivo | Cambio |
|---|---|
| `billing/templates/billing/base.html` | Script de tema temprano, toggle 🌙/☀️, botón Editar en modal, CSS con variables Bootstrap, `showDetail()` actualizado |
| `billing/templates/billing/brand_list.html` | `data-dm-edit-url` en botón Ver; eliminado botón Editar independiente de la fila |
| `billing/templates/billing/productgroup_list.html` | Traducido al español; `data-dm-edit-url`; eliminado botón Editar independiente |
| `billing/templates/billing/supplier_list.html` | Traducido al español; `data-dm-edit-url`; eliminado botón Editar independiente |
| `billing/templates/billing/product_list.html` | Traducido al español; `data-dm-edit-url`; eliminado botón Editar independiente |
| `billing/templates/billing/customer_list.html` | `data-dm-edit-url`; eliminado botón Editar independiente de la fila |
| `billing/templates/billing/invoice_list.html` | Traducido al español (sin botón Editar — no existe vista de actualización) |

---

### Modo claro / oscuro

#### Script de inicialización temprana (`<head>`)
Se añade un `<script>` inline antes de la hoja de estilos de Bootstrap que lee `localStorage.getItem('theme')` y aplica `data-bs-theme` en `<html>` antes de que el navegador renderice cualquier elemento. Esto evita el parpadeo de tema (FOUC) al recargar la página.

#### Botón de alternancia en la barra de navegación
Se agregó un botón con icono 🌙 / ☀️ en la barra de navegación derecha. Al hacer clic llama a `toggleTheme()`:
1. Lee el valor actual de `data-bs-theme` en `<html>`
2. Aplica el opuesto (`light` ↔ `dark`)
3. Guarda en `localStorage` para persistir entre páginas y sesiones
4. Actualiza el icono del botón

#### Soporte nativo de Bootstrap 5.3 Color Modes
Bootstrap 5.3 adapta automáticamente todos sus componentes (tablas, cards, modals, formularios, dropdowns, navbar) cuando `data-bs-theme="dark"` está en `<html>`. No se requiere CSS adicional para los componentes del framework.

#### Variables CSS en estilos propios
Los estilos de `.dm-field`, `.dm-label`, `.dm-value` y `.dm-divider` se migraron de colores hardcoded (`#f8f9fa`, `#212529`, etc.) a variables CSS de Bootstrap:

| Propiedad | Antes | Después |
|---|---|---|
| `dm-field` background | `#f8f9fa` | `var(--bs-tertiary-bg)` |
| `dm-label` color | `#6c757d` | `var(--bs-secondary-color)` |
| `dm-value` color | `#212529` | `var(--bs-body-color)` |
| `dm-divider` border | `#dee2e6` | `var(--bs-border-color)` |
| `pf-img-wrapper` border | `#dee2e6` | `var(--bs-border-color)` |

---

### Botón Editar dentro del modal de detalle

#### Cambio en `base.html` — modal footer
Se agregó un `<a id="dmEditLink">` (botón amarillo) en el footer del modal, antes del botón "Ver detalle completo":

```html
<a href="#" class="btn btn-warning d-none" id="dmEditLink">✎ Editar</a>
```

#### Cambio en `showDetail()` — lectura de `data-dm-edit-url`
Se agregó el bloque de control del nuevo botón:

```javascript
var editLink = document.getElementById('dmEditLink');
if (d.dmEditUrl) {
  editLink.href = d.dmEditUrl;
  editLink.classList.remove('d-none');
} else {
  editLink.classList.add('d-none');
}
```

El botón solo aparece si el botón "Ver" del template tiene el atributo `data-dm-edit-url`. Si no existe (facturas, compras), el botón permanece oculto.

#### Eliminación del botón Editar independiente en las filas
Dado que el acceso a Editar ahora está dentro del modal, se eliminó el botón `btn-warning Editar` de la columna de acciones en los 5 templates de lista que lo tenían. La columna ahora solo contiene **Ver** y **Eliminar**.

Módulos afectados: Marcas, Grupos, Proveedores, Productos, Clientes.
Módulos sin botón Editar en modal (no tienen vista de actualización): Facturas, Compras.

---

## Ciclo de Vida de Facturas — Anular / Nota de Crédito / Sustitución

---

### Nuevo campo en Invoice: `estado`

Se agregó el campo `estado` (PositiveSmallIntegerField) con tres valores:

| Valor | Nombre | Descripción |
|---|---|---|
| 0 | Borrador | Factura recién creada; se puede editar y eliminar; **no descuenta stock** |
| 1 | Emitida | Factura confirmada; stock descontado; solo se puede anular, obtener nota de crédito o sustituir |
| 2 | Anulada | Factura cancelada; stock revertido; registro histórico visible pero inactivo |

Las facturas pre-existentes en la base de datos fueron migradas automáticamente a `estado=1` (Emitida) mediante la migración de datos `0005_backfill_invoice_estado`.

### Propiedades de permiso en el modelo

```python
@property
def can_confirm(self):     return self.estado == self.BORRADOR
@property
def can_edit(self):        return self.estado == self.BORRADOR
@property
def can_delete(self):      return self.estado == self.BORRADOR
@property
def can_cancel(self):      return self.estado == self.EMITIDA
@property
def can_substitute(self):  return self.estado == self.EMITIDA
@property
def can_credit_note(self): return self.estado == self.EMITIDA
```

Los templates usan estas propiedades para mostrar/ocultar botones de acción en `invoice_detail.html`.

---

### Nuevo modelo: `CreditNote`

```
billing_creditnote
  invoice   FK→Invoice (PROTECT)
  date      DateField (auto_now_add)
  tipo      CharField choices: 'total' | 'parcial'
  amount    DecimalField
  reason    CharField(300)
  is_active BooleanField
```

Registrado en `admin.py` con `CreditNoteAdmin` y como `CreditNoteInline` en `InvoiceAdmin`.

---

### Nuevas vistas (FBV) en `billing/views.py`

| Vista | URL | Acción |
|---|---|---|
| `invoice_create` | `invoices/create/` | Crea Borrador; sin cambio en stock; redirige a detalle |
| `invoice_update` | `invoices/<pk>/edit/` | Edita un Borrador (bloquea si Emitida/Anulada) |
| `invoice_confirm` | `invoices/<pk>/confirm/` | Borrador → Emitida; descuenta stock con `F('stock') - qty` |
| `invoice_cancel` | `invoices/<pk>/cancel/` | Emitida → Anulada; revierte stock con `F('stock') + qty`; `is_active=False` |
| `invoice_substitute` | `invoices/<pk>/substitute/` | Anula original + crea Borrador copia; redirige al nuevo Borrador para edición |
| `credit_note_create` | `invoices/<pk>/credit-note/` | Crea CreditNote vinculada a factura Emitida |
| `invoice_delete` | `invoices/<pk>/delete/` | Elimina solo Borradores (bloquea Emitidas/Anuladas con mensaje de error) |

La función auxiliar `_recalc_invoice(invoice)` recalcula subtotal / IVA (15%) / total a partir de `invoice.details.all()`.

---

### Nuevas URLs en `billing/urls.py`

```python
path('invoices/<int:pk>/edit/',       views.invoice_update,     name='invoice_update'),
path('invoices/<int:pk>/confirm/',    views.invoice_confirm,    name='invoice_confirm'),
path('invoices/<int:pk>/cancel/',     views.invoice_cancel,     name='invoice_cancel'),
path('invoices/<int:pk>/substitute/', views.invoice_substitute, name='invoice_substitute'),
path('invoices/<int:pk>/credit-note/',views.credit_note_create, name='credit_note_create'),
```

---

### Archivos Modificados

| Archivo | Cambio |
|---|---|
| `billing/models.py` | Campo `estado` en `Invoice`; propiedades `can_*`; nuevo modelo `CreditNote` |
| `billing/forms.py` | `CreditNoteForm`; `InvoiceDetailFormSet` → `extra=1, min_num=1, validate_min=True`; clases CSS para JS |
| `billing/admin.py` | `CreditNoteAdmin`, `CreditNoteInline` en `InvoiceAdmin`; `readonly_fields` en InvoiceAdmin |
| `billing/views.py` | 6 nuevas vistas; `invoice_create` redirige al detalle y guarda como Borrador; `InvoiceListView` → `export_fields` añade Estado, `search_fields` añade filtro por `estado` |
| `billing/urls.py` | 5 nuevas rutas |
| `billing/templates/billing/invoice_form.html` | Rediseñado con 2 cards, cálculo JS en tiempo real, botón "Agregar Fila", botón "Quitar", totales live |
| `billing/templates/billing/invoice_detail.html` | Badge de estado; barra de botones condicional (Editar/Emitir/Anular/Nota de Crédito/Sustituir); sección de Notas de Crédito al pie |
| `billing/templates/billing/invoice_list.html` | Columna Estado junto a Acciones con badge de color; filtro por estado (Activa/Anulada/Borrador); botón contextual Eliminar/Anular según estado |

### Archivos Creados

| Archivo | Descripción |
|---|---|
| `billing/templates/billing/invoice_confirm_emit.html` | Confirmación de emisión con tabla de productos y stock actual |
| `billing/templates/billing/invoice_cancel.html` | Confirmación de anulación con tabla de reversión de stock |
| `billing/templates/billing/invoice_substitute.html` | Confirmación de sustitución con explicación del flujo |
| `billing/templates/billing/credit_note_form.html` | Formulario de Nota de Crédito (tipo/monto/motivo) |
| `billing/migrations/0004_invoice_estado_creditnote.py` | Migración auto-generada: campo `estado` + tabla `CreditNote` |
| `billing/migrations/0005_backfill_invoice_estado.py` | Migración de datos: actualiza facturas existentes a `estado=1` |
