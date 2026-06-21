from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.db.models import F
from .models import *
from shared.mixins import StaffRequiredMixin, SearchExportMixin
from shared.decorators import audit_action
from .forms import SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet, CreditNoteForm
from .ProductForm import ProductForm
from .CustomerForm import CustomerForm
from decimal import Decimal


# === REGISTRO ===
class SignUpView(CreateView):
    form_class    = SignUpForm
    template_name = 'registration/signup.html'
    success_url   = reverse_lazy('billing:dashboard')
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# === HOME (página pública) ===
def home(request):
    if request.user.is_authenticated:
        return redirect('billing:dashboard')
    return render(request, 'billing/home.html')

# === DASHBOARD (selector de módulos) ===
@login_required
def dashboard(request):
    context = {
        'total_products':  Product.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_invoices':  Invoice.objects.count(),
        'low_stock':       Product.objects.filter(stock__lte=5, is_active=True).count(),
    }
    return render(request, 'billing/dashboard.html', context)


# ── BRANDS ──────────────────────────────────────────────────────────────
@login_required
@audit_action('CREATE_BRAND')
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca creada correctamente.')
            return redirect('billing:brand_list')
    else:
        form = BrandForm()
    return render(request, 'billing/brand_form.html', {'form': form, 'title': 'Crear Marca'})

@login_required
@audit_action('UPDATE_BRAND')
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada correctamente.')
            return redirect('billing:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'billing/brand_form.html', {'form': form, 'title': 'Editar Marca'})

@login_required
@audit_action('DELETE_BRAND')
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Marca eliminada.')
        return redirect('billing:brand_list')
    return render(request, 'billing/brand_confirm_delete.html', {'object': brand})


# ── INVOICES ─────────────────────────────────────────────────────────────

def _recalc_invoice(invoice):
    """Recalcula subtotal/tax/total a partir de las líneas de detalle."""
    subtotal         = sum(d.subtotal for d in invoice.details.all())
    invoice.subtotal = subtotal
    invoice.tax      = subtotal * Decimal('0.15')
    invoice.total    = invoice.subtotal + invoice.tax
    invoice.save()


@login_required
def invoice_create(request):
    """Crea un borrador de factura con sus líneas de detalle (sin afectar stock)."""
    if request.method == 'POST':
        form    = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice          = form.save(commit=False)
            invoice.estado   = Invoice.BORRADOR
            invoice.save()
            formset.instance = invoice
            formset.save()
            _recalc_invoice(invoice)
            messages.info(request,
                f'Borrador #{invoice.id} guardado. Revísalo y pulsa "Emitir" para confirmar.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form    = InvoiceForm()
        formset = InvoiceDetailFormSet()

    return render(request, 'billing/invoice_form.html', {
        'form': form, 'formset': formset,
        'title': 'Nueva Factura',
    })


@login_required
def invoice_update(request, pk):
    """Edita un borrador de factura (solo en estado BORRADOR)."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if not invoice.can_edit:
        messages.error(request, 'Solo se puede editar una factura en estado Borrador.')
        return redirect('billing:invoice_detail', pk=pk)

    if request.method == 'POST':
        form    = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceDetailFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            _recalc_invoice(invoice)
            messages.success(request, f'Borrador #{invoice.id} actualizado.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form    = InvoiceForm(instance=invoice)
        formset = InvoiceDetailFormSet(instance=invoice)

    return render(request, 'billing/invoice_form.html', {
        'form': form, 'formset': formset,
        'invoice': invoice,
        'title': f'Editar Borrador #{invoice.id}',
    })


@login_required
def invoice_confirm(request, pk):
    """Emite un borrador: cambia estado a EMITIDA y descuenta stock de cada producto."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if not invoice.can_confirm:
        messages.error(request, 'Solo se puede emitir una factura en estado Borrador.')
        return redirect('billing:invoice_detail', pk=pk)

    if request.method == 'POST':
        for detail in invoice.details.all():
            Product.objects.filter(pk=detail.product_id).update(
                stock=F('stock') - detail.quantity
            )
        invoice.estado = Invoice.EMITIDA
        invoice.save()
        messages.success(request, f'Factura #{invoice.id} emitida. Stock actualizado.')
        return redirect('billing:invoice_detail', pk=invoice.pk)

    return render(request, 'billing/invoice_confirm_emit.html', {'invoice': invoice})


@login_required
def invoice_cancel(request, pk):
    """Anula una factura emitida: revierte el stock y la marca como Anulada/Inactiva."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if not invoice.can_cancel:
        messages.error(request, 'Solo se puede anular una factura en estado Emitida.')
        return redirect('billing:invoice_detail', pk=pk)

    if request.method == 'POST':
        for detail in invoice.details.all():
            Product.objects.filter(pk=detail.product_id).update(
                stock=F('stock') + detail.quantity
            )
        invoice.estado    = Invoice.ANULADA
        invoice.is_active = False
        invoice.save()
        messages.success(request,
            f'Factura #{invoice.id} anulada. Stock revertido automáticamente.')
        return redirect('billing:invoice_list')

    return render(request, 'billing/invoice_cancel.html', {'invoice': invoice})


@login_required
def invoice_substitute(request, pk):
    """Anula la factura original y crea un nuevo borrador con los mismos datos."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if not invoice.can_substitute:
        messages.error(request, 'Solo se puede sustituir una factura emitida.')
        return redirect('billing:invoice_detail', pk=pk)

    if request.method == 'POST':
        # 1. Anular la factura original y revertir stock
        for detail in invoice.details.all():
            Product.objects.filter(pk=detail.product_id).update(
                stock=F('stock') + detail.quantity
            )
        invoice.estado    = Invoice.ANULADA
        invoice.is_active = False
        invoice.save()

        # 2. Crear nuevo borrador con los mismos datos
        new_invoice = Invoice.objects.create(
            customer=invoice.customer,
            estado=Invoice.BORRADOR,
        )
        for detail in invoice.details.all():
            InvoiceDetail.objects.create(
                invoice    = new_invoice,
                product    = detail.product,
                quantity   = detail.quantity,
                unit_price = detail.unit_price,
            )
        _recalc_invoice(new_invoice)

        messages.success(request,
            f'Factura #{invoice.id} anulada. Nuevo borrador #{new_invoice.id} creado. '
            f'Corrija los datos y emita la factura de reemplazo.')
        return redirect('billing:invoice_update', pk=new_invoice.pk)

    return render(request, 'billing/invoice_substitute.html', {'invoice': invoice})


@login_required
def credit_note_create(request, pk):
    """Crea una Nota de Crédito vinculada a una factura emitida."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if not invoice.can_credit_note:
        messages.error(request, 'Solo se pueden crear notas de crédito sobre facturas emitidas.')
        return redirect('billing:invoice_detail', pk=pk)

    if request.method == 'POST':
        form = CreditNoteForm(request.POST)
        if form.is_valid():
            note         = form.save(commit=False)
            note.invoice = invoice
            note.save()
            messages.success(request,
                f'Nota de Crédito NC-{note.id} registrada sobre Factura #{invoice.id}.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = CreditNoteForm(initial={
            'amount': invoice.total,
            'tipo':   CreditNote.TIPO_TOTAL,
        })

    return render(request, 'billing/credit_note_form.html', {
        'form': form, 'invoice': invoice,
    })


@login_required
def invoice_detail(request, pk):
    """Muestra el detalle completo de una factura."""
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer')
                       .prefetch_related('details__product', 'credit_notes'),
        pk=pk
    )
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_delete(request, pk):
    """Elimina un borrador de factura (solo en estado BORRADOR)."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if not invoice.can_delete:
        messages.error(request,
            'Solo se puede eliminar una factura en estado Borrador. '
            'Para las emitidas, usa "Anular".')
        return redirect('billing:invoice_detail', pk=pk)
    if request.method == 'POST':
        invoice_id = invoice.id
        invoice.delete()
        messages.success(request, f'Borrador #{invoice_id} eliminado.')
        return redirect('billing:invoice_list')
    return render(request, 'billing/invoice_confirm_delete.html', {'object': invoice})


# ── BRAND (CBV list) ─────────────────────────────────────────────────────
class BrandListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model           = Brand
    template_name   = 'billing/brand_list.html'
    context_object_name = 'items'
    export_filename = 'marcas'
    export_fields   = [
        ('Nombre', 'name'), ('Descripción', 'description'), ('Activo', 'is_active'),
    ]
    search_fields   = [
        {'param': 'q',         'fields': ['name__icontains', 'description__icontains']},
        {'param': 'is_active', 'field':  'is_active', 'type': 'bool'},
    ]


# ── PRODUCTGROUP (CBV) ──────────────────────────────────────────────────
class ProductGroupListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model           = ProductGroup
    template_name   = 'billing/productgroup_list.html'
    context_object_name = 'items'
    export_filename = 'grupos'
    export_fields   = [('Nombre', 'name'), ('Activo', 'is_active')]
    search_fields   = [
        {'param': 'q',         'field': 'name__icontains'},
        {'param': 'is_active', 'field': 'is_active', 'type': 'bool'},
    ]

class ProductGroupCreateView(LoginRequiredMixin, CreateView):
    model         = ProductGroup
    fields        = ['name', 'is_active']
    template_name = 'billing/productgroup_form.html'
    success_url   = reverse_lazy('billing:productgroup_list')

class ProductGroupUpdateView(LoginRequiredMixin, UpdateView):
    model         = ProductGroup
    fields        = ['name', 'is_active']
    template_name = 'billing/productgroup_form.html'
    success_url   = reverse_lazy('billing:productgroup_list')

class ProductGroupDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model             = ProductGroup
    template_name     = 'billing/productgroup_confirm_delete.html'
    success_url       = reverse_lazy('billing:productgroup_list')
    staff_redirect_url = '/groups/'


# ── SUPPLIER (CBV) ──────────────────────────────────────────────────────
class SupplierListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model           = Supplier
    template_name   = 'billing/supplier_list.html'
    context_object_name = 'items'
    export_filename = 'proveedores'
    export_fields   = [
        ('Nombre', 'name'), ('Contacto', 'contact_name'),
        ('Email', 'email'), ('Teléfono', 'phone'), ('Activo', 'is_active'),
    ]
    search_fields   = [
        {'param': 'q',         'fields': ['name__icontains', 'contact_name__icontains', 'email__icontains']},
        {'param': 'phone',     'field':  'phone__icontains'},
        {'param': 'is_active', 'field':  'is_active', 'type': 'bool'},
    ]

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model         = Supplier
    fields        = ['name', 'contact_name', 'email', 'phone', 'address', 'is_active']
    template_name = 'billing/supplier_form.html'
    success_url   = reverse_lazy('billing:supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model         = Supplier
    fields        = ['name', 'contact_name', 'email', 'phone', 'address', 'is_active']
    template_name = 'billing/supplier_form.html'
    success_url   = reverse_lazy('billing:supplier_list')

class SupplierDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model              = Supplier
    template_name      = 'billing/supplier_confirm_delete.html'
    success_url        = reverse_lazy('billing:supplier_list')
    staff_redirect_url = '/suppliers/'


# ── PRODUCT (CBV) ───────────────────────────────────────────────────────
class ProductListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model           = Product
    queryset        = Product.objects.select_related('brand', 'group').prefetch_related('suppliers')
    template_name   = 'billing/product_list.html'
    context_object_name = 'items'
    export_filename = 'productos'
    export_fields   = [
        ('Nombre',      'name'),
        ('Descripción', 'description'),
        ('Marca',       'brand__name'),
        ('Grupo',       'group__name'),
        ('Precio',      'unit_price'),
        ('Stock',       'stock'),
        ('Balance',     lambda p: p.unit_price * p.stock),
        ('Activo',      'is_active'),
    ]
    search_fields   = [
        {'param': 'q',         'fields': ['name__icontains', 'description__icontains']},
        {'param': 'brand',     'field':  'brand__name__icontains'},
        {'param': 'group',     'field':  'group__name__icontains'},
        {'param': 'supplier',  'field':  'suppliers__name__icontains'},
        {'param': 'price_min', 'field':  'unit_price__gte', 'type': 'number'},
        {'param': 'price_max', 'field':  'unit_price__lte', 'type': 'number'},
        {'param': 'stock_min', 'field':  'stock__gte',      'type': 'number'},
        {'param': 'stock_max', 'field':  'stock__lte',      'type': 'number'},
        {'param': 'is_active', 'field':  'is_active',       'type': 'bool'},
    ]

class ProductCreateView(LoginRequiredMixin, CreateView):
    model         = Product
    form_class    = ProductForm
    template_name = 'billing/product_form.html'
    success_url   = reverse_lazy('billing:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model         = Product
    form_class    = ProductForm
    template_name = 'billing/product_form.html'
    success_url   = reverse_lazy('billing:product_list')

class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model              = Product
    template_name      = 'billing/product_confirm_delete.html'
    success_url        = reverse_lazy('billing:product_list')
    staff_redirect_url = '/products/'


# ── CUSTOMER (CBV) ──────────────────────────────────────────────────────
class CustomerListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model           = Customer
    template_name   = 'billing/customer_list.html'
    context_object_name = 'items'
    export_filename = 'clientes'
    export_fields   = [
        ('DNI', 'dni'), ('Apellidos', 'last_name'), ('Nombres', 'first_name'),
        ('Email', 'email'), ('Teléfono', 'phone'), ('Activo', 'is_active'),
    ]
    search_fields   = [
        {'param': 'q',         'fields': ['first_name__icontains', 'last_name__icontains',
                                          'dni__icontains', 'email__icontains']},
        {'param': 'phone',     'field':  'phone__icontains'},
        {'param': 'is_active', 'field':  'is_active', 'type': 'bool'},
    ]

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model         = Customer
    form_class    = CustomerForm
    template_name = 'billing/customer_form.html'
    success_url   = reverse_lazy('billing:customer_list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model         = Customer
    form_class    = CustomerForm
    template_name = 'billing/customer_form.html'
    success_url   = reverse_lazy('billing:customer_list')

class CustomerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model              = Customer
    template_name      = 'billing/customer_confirm_delete.html'
    success_url        = reverse_lazy('billing:customer_list')
    staff_redirect_url = '/customers/'


# ── INVOICE (CBV list) ──────────────────────────────────────────────────
class InvoiceListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model           = Invoice
    queryset        = Invoice.objects.select_related('customer')
    template_name   = 'billing/invoice_list.html'
    context_object_name = 'items'
    export_filename = 'facturas'
    export_fields   = [
        ('#',       'id'),
        ('Cliente', lambda inv: str(inv.customer)),
        ('Fecha',   lambda inv: inv.invoice_date.strftime('%d/%m/%Y')),
        ('Estado',  lambda inv: inv.get_estado_display()),
        ('Subtotal','subtotal'),
        ('IVA',     'tax'),
        ('Total',   'total'),
    ]
    search_fields   = [
        {'param': 'q', 'fields': [
            'customer__first_name__icontains',
            'customer__last_name__icontains',
            'customer__dni__icontains',
        ]},
        {'param': 'estado',    'field': 'estado',              'type': 'number'},
        {'param': 'date_from', 'field': 'invoice_date__date__gte', 'type': 'date'},
        {'param': 'date_to',   'field': 'invoice_date__date__lte', 'type': 'date'},
        {'param': 'total_min', 'field': 'total__gte',          'type': 'number'},
        {'param': 'total_max', 'field': 'total__lte',          'type': 'number'},
    ]
