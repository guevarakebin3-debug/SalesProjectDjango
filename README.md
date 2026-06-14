# 🛒 Sistema de Ventas y Facturación - Django

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Django-6.x-darkgreen?style=for-the-badge&logo=django">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap">
  <img src="https://img.shields.io/badge/SQLite-Base_de_Datos-lightblue?style=for-the-badge&logo=sqlite">
  <img src="https://img.shields.io/badge/Estado-En_Desarrollo-orange?style=for-the-badge">
</p>

---

# 📖 Descripción

Proyecto académico desarrollado para la asignatura de **Programación Orientada a Objetos con Python**, utilizando el framework **Django** y el entorno de desarrollo **Visual Studio Code**.

Es un sistema web de **ventas y facturación** que permite gestionar marcas, grupos de productos, proveedores, productos, clientes y facturas, con autenticación de usuarios, control de permisos y auditoría de acciones.

---

# 🎯 Objetivos del Proyecto

✅ Aplicar el patrón MVT (Modelo - Vista - Template) de Django  
✅ Implementar relaciones entre modelos (ForeignKey, OneToOne, ManyToMany)  
✅ Gestionar autenticación y permisos de usuarios  
✅ Aplicar vistas basadas en funciones (FBV) y en clases (CBV)  
✅ Reutilizar código mediante mixins, decoradores y validadores  
✅ Implementar formularios con formsets para facturas con detalle  
✅ Organizar proyectos Django de forma profesional  

---

# 🛠️ Tecnologías Utilizadas

| Tecnología         | Uso                                        |
| ------------------ | ------------------------------------------ |
| Python 3           | Lenguaje principal                         |
| Django 6           | Framework web (MVT)                        |
| Bootstrap 5.3      | Estilos y componentes de interfaz          |
| SQLite             | Base de datos de desarrollo                |
| Visual Studio Code | Entorno de desarrollo                      |
| Git                | Control de versiones                       |
| GitHub             | Repositorio remoto                         |

---

# 📂 Estructura del Proyecto

```text
salesdjango/
│
├── manage.py                    ← Punto de entrada Django
├── requirements.txt             ← Dependencias del proyecto
├── .gitignore
│
├── config/                      ← Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── billing/                     ← App principal
│   ├── models.py                ← Brand, ProductGroup, Supplier, Product,
│   │                               Customer, CustomerProfile, Invoice, InvoiceDetail
│   ├── views.py                 ← FBV (Brand, Invoice) + CBV (resto de modelos)
│   ├── forms.py                 ← SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet
│   ├── urls.py                  ← Rutas de la app
│   ├── admin.py                 ← Registro de modelos con inlines
│   └── templates/billing/       ← Templates de la app
│       ├── base.html
│       ├── home.html
│       ├── brand_*.html
│       ├── productgroup_*.html
│       ├── supplier_*.html
│       ├── product_*.html
│       ├── customer_*.html
│       └── invoice_*.html
│
├── shared/                      ← Código reutilizable (NO es una app Django)
│   ├── __init__.py
│   ├── mixins.py                ← StaffRequiredMixin
│   ├── decorators.py            ← @audit_action
│   └── validators.py            ← validate_cedula_ec
│
└── templates/                   ← Templates globales
    └── registration/
        ├── login.html
        └── signup.html
```

---

# 🗃️ Modelos y Relaciones

| Modelo            | Relaciones                                        |
| ----------------- | ------------------------------------------------- |
| `Brand`           | —                                                 |
| `ProductGroup`    | —                                                 |
| `Supplier`        | —                                                 |
| `Product`         | ForeignKey → Brand, ProductGroup / ManyToMany → Supplier |
| `Customer`        | —                                                 |
| `CustomerProfile` | OneToOne → Customer                               |
| `Invoice`         | ForeignKey → Customer                             |
| `InvoiceDetail`   | ForeignKey → Invoice, Product                     |

---

# 🔐 Carpeta `shared/` — Código Reutilizable

La carpeta `shared/` contiene utilidades que pueden importarse en cualquier parte del proyecto sin pertenecer a una app específica.

| Archivo           | Contiene             | Se aplica en                              |
| ----------------- | -------------------- | ----------------------------------------- |
| `mixins.py`       | `StaffRequiredMixin` | DeleteView de todos los modelos (CBV)     |
| `decorators.py`   | `@audit_action`      | FBV de Brand (list, create, update, delete) |
| `validators.py`   | `validate_cedula_ec` | Campo `dni` del modelo `Customer`         |

### StaffRequiredMixin
Protege las vistas de eliminación: solo usuarios con `is_staff = True` pueden borrar registros. Si un usuario sin permiso intenta acceder, es redirigido con un mensaje de error.

### @audit_action
Registra en consola (y en el logger `audit`) cada acción que realiza un usuario: quién, qué, cuándo, desde qué IP y con qué método HTTP.

### validate_cedula_ec
Valida que el DNI/RUC ingresado sea matemáticamente correcto según el algoritmo oficial del Registro Civil del Ecuador (módulo 10, verificación de provincia y dígito verificador).

---

# ▶️ Ejecución del Proyecto

## Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd salesdjango
```

## Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Aplicar migraciones

```bash
python manage.py migrate
```

## Crear superusuario

```bash
python manage.py createsuperuser
```

## Iniciar el servidor

```bash
python manage.py runserver
```

Luego abre el navegador en `http://127.0.0.1:8000`

---

# 📋 Funcionalidades del Sistema

| Módulo          | Operaciones disponibles              |
| --------------- | ------------------------------------ |
| Marcas (Brand)  | Listar, Crear, Editar, Eliminar      |
| Grupos          | Listar, Crear, Editar, Eliminar      |
| Proveedores     | Listar, Crear, Editar, Eliminar      |
| Productos       | Listar, Crear, Editar, Eliminar      |
| Clientes        | Listar, Crear, Editar, Eliminar      |
| Facturas        | Listar, Crear con detalle, Ver, Eliminar |
| Usuarios        | Registro, Login, Logout              |

> Las operaciones de **Eliminar** están protegidas: solo usuarios Staff pueden ejecutarlas.

---

# 🤖 Uso de Inteligencia Artificial

Durante el desarrollo del proyecto se utilizó **Claude (Anthropic)** como apoyo para:

- Revisar y verificar que el proyecto cumpliera con los requisitos de la guía
- Resolver dudas sobre relaciones entre modelos y el ORM de Django
- Orientación en la implementación de formsets para el módulo de facturas
- Apoyar en la generación del `.gitignore` y este `README`

---

# 💬 Ejemplos de Prompts Utilizados

## 🧠 Prompt 1

```text
Revisa por favor la guía y el proyecto para ver si todo está tal como
debo hacerlo según la guía.
```

## 🧠 Prompt 2

```text
¿Cómo aplico el StaffRequiredMixin en las vistas de eliminación
y cuál es el orden correcto de herencia?
```

## 🧠 Prompt 3

```text
¿Cómo funciona inlineformset_factory para crear una factura
con sus líneas de detalle en un solo formulario?
```

---

# 👥 Equipo de Desarrollo

| Nombre                     | Rol              |
| -------------------------- | ---------------- |
| Vera Paredes Daniel        | Profesor         |
| Delgado Zambrano Alexy     | 4to semestre     |
| Gines Moncada Brithany     | 4to semestre     |
| López Herrera Ashley       | 4to semestre     |
| Martínez López Byron       | 4to semestre     |
| Moreira Intriago Diego     | 4to semestre     |
| Quizhpi Landi Andy         | 4to semestre     |

---

# ⭐ Recomendación

Si el proyecto te resulta útil, puedes darle una ⭐ al repositorio para apoyar el trabajo realizado.