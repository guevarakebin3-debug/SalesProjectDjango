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

## Archivos Creados

| Archivo | Descripción |
|---|---|
| `billing/templates/billing/_pagination.html` | Partial reutilizable de paginación Bootstrap |
| `billing/templates/billing/_export_buttons.html` | Partial reutilizable de botones PDF/Excel |
| `CAMBIOS.md` | Este archivo |

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
