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

| Tecnología      | Uso                                             |
|-----------------|-------------------------------------------------|
| Python 3        | Lenguaje principal                              |
| Django 6        | Framework web (MVT)                             |
| Bootstrap 5.3   | Estilos, componentes UI y modo claro/oscuro     |
| SQLite          | Base de datos de desarrollo                     |
| ReportLab       | Exportación a PDF                               |
| OpenPyXL        | Exportación a Excel                             |
| Visual Studio Code | Entorno de desarrollo                        |
| Git / GitHub    | Control de versiones                            |

---

## Estructura del Proyecto

```text
salesdjango/
│
├── manage.py                        ← Punto de entrada Django
├── requirements.txt                 ← Dependencias del proyecto
├── CAMBIOS.md                       ← Historial detallado de cambios
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
│   │                                   Customer, CustomerProfile,
│   │                                   Invoice, InvoiceDetail, CreditNote
│   ├── views.py                     ← FBV (Invoice, Brand) + CBV (resto)
│   ├── forms.py                     ← SignUpForm, BrandForm, InvoiceForm,
│   │                                   InvoiceDetailFormSet, CreditNoteForm
│   ├── ProductForm.py               ← Formulario avanzado de Producto
│   ├── CustomerForm.py              ← Formulario avanzado de Cliente
│   ├── urls.py                      ← Rutas de la app de ventas
│   ├── admin.py                     ← Registro con inlines y filtros
│   ├── migrations/
│   └── templates/billing/
│       ├── base.html                ← Layout base con navbar, modal y modo oscuro
│       ├── home.html                ← Landing page pública (TecnoStock S.A.)
│       ├── dashboard.html           ← Selector de módulos post-login
│       ├── brand_*.html
│       ├── productgroup_*.html
│       ├── supplier_*.html
│       ├── product_*.html
│       ├── customer_*.html
│       ├── invoice_*.html           ← Lista, formulario, detalle, confirmar,
│       │                               anular, sustituir, confirmar emisión
│       ├── credit_note_form.html    ← Formulario de Nota de Crédito
│       ├── _pagination.html         ← Partial reutilizable de paginación
│       └── _export_buttons.html     ← Partial reutilizable de exportación
│
├── purchasing/                      ← App de Compras (módulo secundario)
│   ├── models.py                    ← Purchase, PurchaseDetail
│   ├── views.py                     ← FBV: list, create, detail, delete
│   ├── forms.py                     ← PurchaseForm, PurchaseDetailForm,
│   │                                   PurchaseDetailFormSet
│   ├── urls.py                      ← Rutas del módulo de compras
│   ├── admin.py
│   ├── migrations/
│   └── templates/purchasing/
│       ├── purchase_list.html
│       ├── purchase_form.html
│       ├── purchase_detail.html
│       └── purchase_confirm_delete.html
│
├── shared/                          ← Código reutilizable (no es una app Django)
│   ├── __init__.py
│   ├── mixins.py                    ← SearchListMixin, ExportMixin,
│   │                                   SearchExportMixin, StaffRequiredMixin
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

| Modelo            | Relaciones                                                  |
|-------------------|-------------------------------------------------------------|
| `Brand`           | —                                                           |
| `ProductGroup`    | —                                                           |
| `Supplier`        | —                                                           |
| `Product`         | FK → Brand, FK → ProductGroup, M2M → Supplier              |
| `Customer`        | —                                                           |
| `CustomerProfile` | OneToOne → Customer                                         |
| `Invoice`         | FK → Customer. Estados: Borrador(0) / Emitida(1) / Anulada(2) |
| `InvoiceDetail`   | FK → Invoice, FK → Product                                  |
| `CreditNote`      | FK → Invoice (tipos: Devolución Total / Parcial)           |

### App `purchasing` (Compras)

| Modelo           | Relaciones                        |
|------------------|-----------------------------------|
| `Purchase`       | FK → Supplier (de billing)        |
| `PurchaseDetail` | FK → Purchase, FK → Product (de billing) |

> Los modelos `Supplier` y `Product` son compartidos entre ambas apps; `purchasing` los importa de `billing.models`.

---

## Funcionalidades del Sistema

### Módulo de Ventas

| Sección      | Operaciones                                                         |
|--------------|---------------------------------------------------------------------|
| Marcas       | Listar, Crear, Editar, Eliminar, Ver detalle, Exportar PDF/Excel    |
| Grupos       | Listar, Crear, Editar, Eliminar, Ver detalle, Exportar PDF/Excel    |
| Proveedores  | Listar, Crear, Editar, Eliminar, Ver detalle, Exportar PDF/Excel    |
| Productos    | Listar, Crear, Editar, Eliminar, Ver detalle, Foto, Exportar PDF/Excel |
| Clientes     | Listar, Crear, Editar, Eliminar, Ver detalle, Exportar PDF/Excel    |
| Facturas     | Listar, Crear borrador, Emitir, Ver detalle, Anular, Sustituir, Nota de Crédito, Exportar |

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

| Sección  | Operaciones                                                   |
|----------|---------------------------------------------------------------|
| Compras  | Listar, Crear, Ver detalle, Eliminar, Exportar PDF/Excel      |

Al registrar una compra, el stock de cada producto se incrementa automáticamente usando expresiones `F()` del ORM de Django para evitar condiciones de carrera.

---

## Características Transversales

| Característica            | Descripción                                                          |
|---------------------------|----------------------------------------------------------------------|
| Autenticación             | Login / Logout / Registro con validación                            |
| Control de permisos       | Eliminaciones protegidas con `StaffRequiredMixin` (solo Staff)       |
| Auditoría                 | Decorador `@audit_action` registra acciones críticas con IP y timestamp |
| Búsqueda y filtros        | Buscador por múltiples campos + filtros por fecha, estado, rango de precios |
| Paginación                | Paginación automática en todos los listados (10 registros por página) |
| Exportación               | Botones PDF y Excel en todos los módulos de listado                 |
| Modal de detalle          | Botón "Ver" abre modal con datos del registro; botón "Editar" integrado |
| Modo oscuro / claro       | Toggle en la barra de navegación; preferencia guardada en `localStorage` |
| Validación de cédula      | Validador `validate_cedula_ec` con algoritmo oficial del Registro Civil del Ecuador |
| Landing page pública      | Página de inicio con información de TecnoStock S.A. sin requerir login |
| Dashboard post-login      | Selector visual de módulos (Ventas o Compras) con estadísticas rápidas |

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
asgiref==3.11.1
django-extensions==4.1
reportlab==4.5.1
openpyxl==3.1.5
pillow==12.2.0
sqlparse==0.5.5
```

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

---

## Equipo de Desarrollo

| Nombre                     | Rol              |
|----------------------------|------------------|
| Vera Paredes Daniel        | Profesor         |
| Delgado Zambrano Alexy     | 4to semestre     |
| Gines Moncada Brithany     | 4to semestre     |
| López Herrera Ashley       | 4to semestre     |
| Martínez López Byron       | 4to semestre     |
| Moreira Intriago Diego     | 4to semestre     |
| Quizhpi Landi Andy         | 4to semestre     |

---

> Si el proyecto te resulta útil, puedes darle una ⭐ al repositorio para apoyar el trabajo realizado.
