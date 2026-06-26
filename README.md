# TecnoStock S.A. — Sistema de Ventas y Compras

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Django-6.x-darkgreen?style=for-the-badge&logo=django">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap">
  <img src="https://img.shields.io/badge/SQLite-Base_de_Datos-lightblue?style=for-the-badge&logo=sqlite">
  <img src="https://img.shields.io/badge/Estado-En_Desarrollo-orange?style=for-the-badge">
</p>

---

## Descripción

Proyecto académico desarrollado para la asignatura de **Programación Orientada a Objetos con Python**, utilizando el framework **Django** y el entorno de desarrollo **Visual Studio Code**.

Es un sistema web para la empresa ficticia **TecnoStock S.A.** que integra dos módulos principales:

- **Módulo de Ventas** — gestión de marcas, grupos, proveedores, productos, clientes y facturación con ciclo de vida completo.
- **Módulo de Compras** — registro de compras a proveedores con actualización automática de inventario.

---

## Objetivos del Proyecto

- Aplicar el patrón MVT (Modelo - Vista - Template) de Django
- Implementar relaciones entre modelos (ForeignKey, OneToOne, ManyToMany)
- Gestionar autenticación y permisos de usuarios
- Aplicar vistas basadas en funciones (FBV) y en clases (CBV)
- Reutilizar código mediante mixins, decoradores y validadores compartidos
- Implementar formularios con formsets para documentos con detalle (facturas, compras)
- Organizar un proyecto Django multi-app de forma profesional
- Implementar ciclo de vida de documentos contables (Borrador → Emitida → Anulada)
- Gestionar stock con expresiones atómicas `F()` del ORM de Django

---

## Tecnologías Utilizadas

| Tecnología         | Uso                                             |
|--------------------|-------------------------------------------------|
| Python 3           | Lenguaje principal                              |
| Django 6           | Framework web (MVT)                             |
| Bootstrap 5.3      | Estilos, componentes UI y modo claro/oscuro     |
| Chart.js           | Gráficos del dashboard (barras y donut)         |
| SQLite             | Base de datos de desarrollo                     |
| ReportLab          | Exportación a PDF de facturas y compras         |
| OpenPyXL           | Exportación a Excel                             |
| Pillow             | Gestión de imágenes (`ImageField`)              |
| Visual Studio Code | Entorno de desarrollo                           |
| Git / GitHub       | Control de versiones                            |

---

## Estructura del Proyecto

```text
salesdjango/
│
├── manage.py                        ← Punto de entrada Django
├── requirements.txt                 ← Dependencias del proyecto
├── CAMBIOS.md                       ← Historial de cambios por archivo
├── .gitignore
│
├── config/                          ← Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── billing/                         ← App de Ventas (módulo principal)
│   ├── models.py                    ← Brand, ProductGroup, Supplier, Product,
│   │                                   Customer, Invoice, InvoiceDetail, CreditNote
│   ├── views.py                     ← FBV (facturas, PDF) + CBV (resto)
│   ├── forms.py                     ← SignUpForm, BrandForm, InvoiceForm,
│   │                                   InvoiceDetailFormSet, CreditNoteForm
│   ├── ProductForm.py               ← Formulario avanzado de Producto
│   ├── CustomerForm.py              ← Formulario avanzado de Cliente (con foto)
│   ├── urls.py                      ← Rutas de la app de ventas
│   ├── admin.py                     ← Registro con inlines y filtros
│   ├── migrations/
│   └── templates/billing/
│       ├── base.html                ← Layout base: navbar, modal detalle, modo oscuro
│       ├── home.html                ← Landing page pública (TecnoStock S.A.)
│       ├── dashboard.html           ← KPIs, Chart.js, top productos/proveedores
│       ├── brand_*.html
│       ├── productgroup_*.html
│       ├── supplier_*.html          ← Lista con foto, formulario con subida de imagen
│       ├── product_*.html           ← Lista con foto, formulario con preview
│       ├── customer_*.html          ← Lista con foto, formulario con preview en vivo
│       ├── invoice_*.html           ← Lista, formulario, detalle, confirmar emisión,
│       │                               anular, sustituir, PDF
│       ├── credit_note_form.html    ← Formulario de Nota de Crédito
│       ├── _pagination.html         ← Partial reutilizable de paginación
│       └── _export_buttons.html     ← Partial reutilizable de exportación
│
├── purchasing/                      ← App de Compras
│   ├── models.py                    ← Purchase, PurchaseDetail, SupplierCreditNote
│   ├── views.py                     ← list, create, confirm, cancel, detail, delete, pdf
│   ├── forms.py                     ← PurchaseForm, PurchaseDetailForm, FormSet
│   ├── urls.py                      ← Rutas del módulo de compras
│   ├── admin.py
│   ├── migrations/
│   └── templates/purchasing/
│       ├── purchase_list.html       ← Lista con filtros y exportación
│       ├── purchase_form.html       ← Formset con recálculo JS
│       ├── purchase_detail.html     ← Detalle: confirmar / anular / PDF
│       ├── purchase_confirm.html    ← Confirmación de emisión
│       ├── purchase_cancel.html     ← Confirmación de anulación
│       ├── purchase_confirm_delete.html
│       └── supplier_credit_note_form.html
│
├── inventory/                       ← App de Inventario (solo modelos y admin)
│   ├── models.py                    ← StockMovement (auditoría de movimientos)
│   ├── admin.py
│   └── migrations/
│
├── shared/                          ← Código reutilizable (no es una app Django)
│   ├── __init__.py
│   ├── mixins.py                    ← SearchListMixin, ExportMixin,
│   │                                   SearchExportMixin, StaffRequiredMixin
│   ├── money.py                     ← round_money() con ROUND_HALF_UP
│   ├── decorators.py                ← @audit_action
│   └── validators.py                ← validate_cedula_ec
│
└── templates/                       ← Templates globales
    └── registration/
        ├── login.html
        └── signup.html
```

---

## Modelos y Relaciones

### App `billing` (Ventas)

| Modelo          | Relaciones y notas                                                          |
|-----------------|-----------------------------------------------------------------------------|
| `Brand`         | —                                                                           |
| `ProductGroup`  | —                                                                           |
| `Supplier`      | Campo `photo` (ImageField)                                                  |
| `Product`       | FK → Brand, FK → ProductGroup, M2M → Supplier. Campos: `photo`, `tax_rate` |
| `Customer`      | Campo `photo` (ImageField)                                                  |
| `Invoice`       | FK → Customer. `estado`: Borrador(0) / Emitida(1) / Anulada(2)             |
| `InvoiceDetail` | FK → Invoice, FK → Product. Campo `discount_pct`                            |
| `CreditNote`    | FK → Invoice. Tipos: Devolución Total / Parcial                             |

### App `purchasing` (Compras)

| Modelo               | Relaciones y notas                                                 |
|----------------------|--------------------------------------------------------------------|
| `Purchase`           | FK → Supplier. `estado`: Borrador / Confirmada / Anulada           |
| `PurchaseDetail`     | FK → Purchase (CASCADE), FK → Product (PROTECT)                   |
| `SupplierCreditNote` | FK → Purchase. Nota de crédito emitida por el proveedor            |

### App `inventory` (Inventario)

| Modelo          | Relaciones y notas                                                              |
|-----------------|---------------------------------------------------------------------------------|
| `StockMovement` | FK → Product, FK optional → Invoice, FK optional → Purchase, FK optional → User |

> `Supplier` y `Product` son compartidos; `purchasing` e `inventory` los importan de `billing.models`.

---

## Funcionalidades del Sistema

### Módulo de Ventas

| Sección      | Operaciones                                                                        |
|--------------|------------------------------------------------------------------------------------|
| Marcas       | Listar, Crear, Editar, Eliminar, Ver detalle, Exportar PDF/Excel                  |
| Grupos       | Listar, Crear, Editar, Eliminar, Ver detalle, Exportar PDF/Excel                  |
| Proveedores  | Listar (con logo), Crear, Editar (subir logo), Eliminar, Ver detalle, Exportar    |
| Productos    | Listar (con foto), Crear, Editar (subir foto, balance dinámico), Eliminar, Ver detalle, Exportar |
| Clientes     | Listar (con foto), Crear, Editar (subir foto, preview en vivo), Eliminar, Ver detalle, Exportar |
| Facturas     | Listar, Crear borrador, Emitir, Ver detalle, Anular, Sustituir, Nota de Crédito, Descargar PDF, Exportar |

#### Ciclo de vida de facturas

```
Nueva Factura ──► Borrador ──► Emitir ──► Emitida ──► Anular ──► Anulada
                    │                        │
                  Editar                   Sustituir → nuevo Borrador
                  Eliminar                 Nota de Crédito
```

- **Borrador** — se puede editar y eliminar; el stock **no** se modifica.
- **Emitida** — el stock se descuenta automáticamente al emitir; solo se puede anular, crear nota de crédito o sustituir.
- **Anulada** — el stock se revierte automáticamente; registro histórico visible e inactivo.
- **Nota de Crédito** — documento contable vinculado a la factura original (devolución parcial o total).
- **Sustitución** — anula la factura original y crea un nuevo borrador con los mismos datos para corregir y volver a emitir.

### Módulo de Compras

| Sección            | Operaciones                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| Compras            | Listar, Crear borrador, Confirmar, Anular, Ver detalle, Descargar PDF, Exportar     |
| Nota de crédito    | Registrar nota de crédito del proveedor vinculada a la compra                       |

#### Ciclo de vida de compras

```
Nueva Compra ──► Borrador ──► Confirmar ──► Confirmada ──► Anular ──► Anulada
                   │
                 Eliminar
```

- **Borrador** — editable; stock no modificado.
- **Confirmada** — stock incrementado automáticamente con `F()` + `atomic()`; registra `StockMovement`.
- **Anulada** — stock revertido; registra `StockMovement`.

---

## Características Transversales

| Característica            | Descripción                                                                          |
|---------------------------|--------------------------------------------------------------------------------------|
| Autenticación             | Login / Logout / Registro con validación                                            |
| Control de permisos       | Eliminaciones protegidas con `StaffRequiredMixin` (solo Staff)                       |
| Auditoría de stock        | `StockMovement` registra cada entrada/salida con tipo, usuario, fecha y documento    |
| Búsqueda y filtros        | Buscador por múltiples campos + filtros por fecha, estado, rango de precios          |
| Paginación                | Paginación automática en todos los listados (10 registros por página)               |
| Exportación               | Botones PDF y Excel en todos los módulos de listado                                 |
| PDF de documentos         | Facturas y compras exportables a PDF con ReportLab (cabeceras a color, tablas)      |
| Fotos en listados         | Miniatura circular en las listas de productos, clientes y proveedores               |
| Modal de detalle          | Botón "Ver" abre modal con foto/avatar, datos del registro y botón Editar integrado |
| Modo oscuro / claro       | Toggle en la barra de navegación; preferencia guardada en `localStorage`             |
| Validación de cédula      | Validador `validate_cedula_ec` con algoritmo oficial del Registro Civil del Ecuador  |
| Landing page pública      | Página de inicio de TecnoStock S.A. sin requerir login                              |
| Dashboard con KPIs        | Ventas/compras/margen bruto, gráficos Chart.js, top 5 productos y proveedores       |

---

## Carpeta `shared/` — Código Reutilizable

La carpeta `shared/` contiene utilidades que pueden importarse desde cualquier app.

### `SearchListMixin`
Mixin declarativo que agrega búsqueda filtrada y paginación a cualquier `ListView`. Cada vista declara `search_fields` con una lista de dicts que describe los parámetros de búsqueda:

```python
search_fields = [
    {'param': 'q',         'fields': ['name__icontains', 'email__icontains']},
    {'param': 'is_active', 'field':  'is_active', 'type': 'bool'},
    {'param': 'price_min', 'field':  'unit_price__gte', 'type': 'number'},
    {'param': 'date_from', 'field':  'created_at__date__gte', 'type': 'date'},
]
```

### `ExportMixin`
Intercepta `?export=pdf` y `?export=excel` antes de paginar y genera el archivo con todos los registros filtrados. Cada vista declara `export_fields` y `export_filename`.

### `SearchExportMixin`
Combina `SearchListMixin` + `ExportMixin`. Es el mixin que se usa directamente en las vistas.

### `StaffRequiredMixin`
Protege las vistas de eliminación: solo usuarios con `is_staff = True` pueden acceder. Redirige con mensaje de error a usuarios sin permiso.

### `@audit_action`
Decorador que registra en el logger `audit` cada acción importante: usuario, acción, IP, método HTTP y timestamp.

### `validate_cedula_ec`
Valida que el campo `dni` sea matemáticamente correcto según el algoritmo del Registro Civil del Ecuador (dígito verificador, código de provincia, longitud).

---

## Ejecución del Proyecto

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd salesdjango
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Iniciar el servidor

```bash
python manage.py runserver
```

Abrir el navegador en `http://127.0.0.1:8000`

---

## Dependencias principales (`requirements.txt`)

```
Django==6.0.6
reportlab==4.5.1
openpyxl==3.1.5
pillow==12.2.0
django-extensions==4.1
```

> No se necesita instalar nada adicional; todas las dependencias ya están declaradas en `requirements.txt`.

---

## Uso de Inteligencia Artificial

Durante el desarrollo del proyecto se utilizó **Claude (Anthropic)** como herramienta de apoyo para:

- Revisar que el proyecto cumpliera los requisitos de la guía de la tarea
- Resolver dudas sobre relaciones entre modelos y el ORM de Django
- Orientación en la implementación de `inlineformset_factory` para facturas y compras con detalle
- Apoyo en la implementación de mixins reutilizables (`SearchExportMixin`)
- Implementación del ciclo de vida de facturas (Borrador / Emitida / Anulada)
- Uso de expresiones `F()` para actualizaciones atómicas de stock
- Diseño del módulo de Compras y la landing page pública
- Generación del `.gitignore`, `CAMBIOS.md` y este `README`

### Ejemplos de prompts utilizados

**Prompt 1**
```
cual sería la mejor forma de maximizar el rendimiento del progarma y minimizar el codigo, manteniendolo compacto y funcional.
```

**Prompt 2**
```
Implementa las funciones alternativas para el módulo de facturación:
botón Anular que revierte el stock, módulo de Notas de Crédito vinculado
a la factura original, y flujo de Sustitución que anula la factura vieja
y crea un borrador editable. Agrega un campo estado en la tabla facturas
(0=Borrador, 1=Emitida, 2=Anulada).
```

**Prompt 3**
```
¿Cómo aplico el StaffRequiredMixin en las vistas de eliminación
y cuál es el orden correcto de herencia en Django CBV?
```



> Si el proyecto te resulta útil, puedes darle una ⭐ al repositorio para apoyar el trabajo realizado.
