from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import *
from shared.mixins import StaffRequiredMixin, SearchExportMixin
from shared.decorators import audit_action
from .forms import SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet
from decimal import Decimal


# === REGISTRO ===
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('billing:brand_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# === BRAND (FBV) ===
@login_required
def home(request):
    """Vista principal del sistema. Muestra resumen general."""
    context = {
        'total_brands': Brand.objects.count(),
        'total_products': Product.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_invoices': Invoice.objects.count(),
        'recent_invoices': Invoice.objects.all()[:5],  # Últimas 5
        'low_stock': Product.objects.filter(stock__lte=5, is_active=True),
    }
    return render(request, 'billing/home.html', context)



@login_required
@audit_action('CREATE_BRAND')
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca Creada!')
            return redirect('billing:brand_list')
    else: form = BrandForm()
    return render(request, 'billing/brand_form.html', {'form':form, 'title':'Crear Marca'})

@login_required
@audit_action('UPDATE_BRAND')  
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca Actualizada!')
            return redirect('billing:brand_list')
    else: form = BrandForm(instance=brand)
    return render(request, 'billing/brand_form.html', {'form':form, 'title':'Edit Brand'})

@login_required
@audit_action('DELETE_BRAND')  
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'BMarca eliminada!')
        return redirect('billing:brand_list')
    return render(request, 'billing/brand_confirm_delete.html', {'object': brand})



@login_required
def invoice_create(request):
    """Crea factura con sus líneas de detalle."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Guardar factura (sin commit para asignar totales)
            invoice = form.save(commit=False)
            invoice.save()

            # Asignar la factura al formset y guardar detalles
            formset.instance = invoice
            details = formset.save()

            # Calcular totales
            subtotal = sum(d.subtotal for d in invoice.details.all())
            invoice.subtotal = subtotal
            invoice.tax = subtotal * Decimal('0.15')  # IVA 15%
            invoice.total = invoice.subtotal + invoice.tax
            invoice.save()

            messages.success(request, f'Invoice #{invoice.id} created! Total: ${invoice.total}')
            return redirect('billing:invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceDetailFormSet()

    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice',
    })


@login_required
def invoice_detail(request, pk):
    """Muestra el detalle completo de una factura."""
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer')
                       .prefetch_related('details__product'),
        pk=pk
    )
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_delete(request, pk):
    """Elimina una factura y todos sus detalles (CASCADE)."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice_id = invoice.id
        invoice.delete()
        messages.success(request, f'Invoice #{invoice_id} deleted!')
        return redirect('billing:invoice_list')
    return render(request, 'billing/invoice_confirm_delete.html', {'object': invoice})

# === BRAND (CBV list) ===
class BrandListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = Brand
    template_name = 'billing/brand_list.html'
    context_object_name = 'items'
    export_filename = 'marcas'
    export_fields = [
        ('Name', 'name'), ('Description', 'description'), ('Active', 'is_active'),
    ]
    search_fields = [
        {'param': 'q', 'fields': ['name__icontains', 'description__icontains']},
        {'param': 'is_active', 'field': 'is_active', 'type': 'bool'},
    ]

# === PRODUCTGROUP (CBV) ===
class ProductGroupListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = ProductGroup
    template_name = 'billing/productgroup_list.html'
    context_object_name = 'items'
    export_filename = 'grupos'
    export_fields = [('Name', 'name'), ('Active', 'is_active')]
    search_fields = [
        {'param': 'q', 'field': 'name__icontains'},
        {'param': 'is_active', 'field': 'is_active', 'type': 'bool'},
    ]
class ProductGroupCreateView(LoginRequiredMixin, CreateView):
    model = ProductGroup; fields = ['name','is_active']; template_name = 'billing/productgroup_form.html'; success_url = reverse_lazy('billing:productgroup_list')
class ProductGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductGroup; fields = ['name','is_active']; template_name = 'billing/productgroup_form.html'; success_url = reverse_lazy('billing:productgroup_list')
class ProductGroupDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProductGroup; template_name = 'billing/productgroup_confirm_delete.html'; success_url = reverse_lazy('billing:productgroup_list')
    staff_redirect_url = '/groups/'  

# === SUPPLIER (CBV) ===
class SupplierListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = Supplier
    template_name = 'billing/supplier_list.html'
    context_object_name = 'items'
    export_filename = 'proveedores'
    export_fields = [
        ('Name', 'name'), ('Contact', 'contact_name'),
        ('Email', 'email'), ('Phone', 'phone'), ('Active', 'is_active'),
    ]
    search_fields = [
        {'param': 'q', 'fields': ['name__icontains', 'contact_name__icontains', 'email__icontains']},
        {'param': 'phone', 'field': 'phone__icontains'},
        {'param': 'is_active', 'field': 'is_active', 'type': 'bool'},
    ]
class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier; fields = ['name','contact_name','email','phone','address','is_active']; template_name = 'billing/supplier_form.html'; success_url = reverse_lazy('billing:supplier_list')
class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier; fields = ['name','contact_name','email','phone','address','is_active']; template_name = 'billing/supplier_form.html'; success_url = reverse_lazy('billing:supplier_list')
class SupplierDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Supplier; template_name = 'billing/supplier_confirm_delete.html'; success_url = reverse_lazy('billing:supplier_list')
    staff_redirect_url = '/suppliers/'

# === PRODUCT (CBV) ===
class ProductListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = Product
    queryset = Product.objects.select_related('brand', 'group').prefetch_related('suppliers')
    template_name = 'billing/product_list.html'
    context_object_name = 'items'
    export_filename = 'productos'
    export_fields = [
        ('Name',        'name'),
        ('Description', 'description'),
        ('Brand',       'brand__name'),
        ('Group',       'group__name'),
        ('Price',       'unit_price'),
        ('Stock',       'stock'),
        ('Active',      'is_active'),
    ]
    search_fields = [
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
    model = Product; fields = ['name','description','brand','group','suppliers','unit_price','stock','is_active']; template_name = 'billing/product_form.html'; success_url = reverse_lazy('billing:product_list')
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product; fields = ['name','description','brand','group','suppliers','unit_price','stock','is_active']; template_name = 'billing/product_form.html'; success_url = reverse_lazy('billing:product_list')
class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product; template_name = 'billing/product_confirm_delete.html'; success_url = reverse_lazy('billing:product_list')
    staff_redirect_url = '/products/'

# === CUSTOMER (CBV) ===
class CustomerListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = Customer
    template_name = 'billing/customer_list.html'
    context_object_name = 'items'
    export_filename = 'clientes'
    export_fields = [
        ('DNI', 'dni'), ('Last Name', 'last_name'), ('First Name', 'first_name'),
        ('Email', 'email'), ('Phone', 'phone'), ('Active', 'is_active'),
    ]
    search_fields = [
        {'param': 'q', 'fields': ['first_name__icontains', 'last_name__icontains', 'dni__icontains', 'email__icontains']},
        {'param': 'phone',     'field': 'phone__icontains'},
        {'param': 'is_active', 'field': 'is_active', 'type': 'bool'},
    ]
class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer; fields = ['dni','first_name','last_name','email','phone','address','is_active']; template_name = 'billing/customer_form.html'; success_url = reverse_lazy('billing:customer_list')
class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer; fields = ['dni','first_name','last_name','email','phone','address','is_active']; template_name = 'billing/customer_form.html'; success_url = reverse_lazy('billing:customer_list')
class CustomerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Customer; template_name = 'billing/customer_confirm_delete.html'; success_url = reverse_lazy('billing:customer_list')
    staff_redirect_url = '/customers/'



# === INVOICE (CBV list) ===
class InvoiceListView(LoginRequiredMixin, SearchExportMixin, ListView):
    model = Invoice
    queryset = Invoice.objects.select_related('customer')
    template_name = 'billing/invoice_list.html'
    context_object_name = 'items'
    export_filename = 'facturas'
    export_fields = [
        ('#',        'id'),
        ('Customer', lambda inv: str(inv.customer)),
        ('Date',     lambda inv: inv.invoice_date.strftime('%d/%m/%Y')),
        ('Subtotal', 'subtotal'),
        ('Tax',      'tax'),
        ('Total',    'total'),
    ]
    search_fields = [
        {'param': 'q', 'fields': [
            'customer__first_name__icontains',
            'customer__last_name__icontains',
            'customer__dni__icontains',
        ]},
        {'param': 'date_from', 'field': 'invoice_date__date__gte', 'type': 'date'},
        {'param': 'date_to',   'field': 'invoice_date__date__lte', 'type': 'date'},
        {'param': 'total_min', 'field': 'total__gte', 'type': 'number'},
        {'param': 'total_max', 'field': 'total__lte', 'type': 'number'},
    ]
