from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from decimal import Decimal
from .models import Purchase, PurchaseDetail
from .forms import PurchaseForm, PurchaseDetailFormSet
from billing.models import Supplier, Product


@login_required
def purchase_list(request):
    qs = Purchase.objects.select_related('supplier').all()

    q = request.GET.get('q', '').strip()
    supplier_id = request.GET.get('supplier', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if q:
        qs = (
            Purchase.objects.select_related('supplier')
            .filter(document_number__icontains=q) |
            Purchase.objects.select_related('supplier')
            .filter(supplier__name__icontains=q)
        )
    if supplier_id:
        qs = qs.filter(supplier_id=supplier_id)
    if date_from:
        qs = qs.filter(purchase_date__gte=date_from)
    if date_to:
        qs = qs.filter(purchase_date__lte=date_to)

    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, 'purchasing/purchase_list.html', {
        'items': qs,
        'suppliers': suppliers,
        'search_params': {
            'q': q,
            'supplier': supplier_id,
            'date_from': date_from,
            'date_to': date_to,
        },
    })


@login_required
def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = PurchaseDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            purchase = form.save(commit=False)
            purchase.save()

            formset.instance = purchase
            formset.save()

            subtotal = sum(d.subtotal for d in purchase.details.all())
            purchase.subtotal = subtotal
            purchase.tax = subtotal * Decimal('0.15')
            purchase.total = purchase.subtotal + purchase.tax
            purchase.save()

            for detail in purchase.details.all():
                Product.objects.filter(pk=detail.product_id).update(
                    stock=F('stock') + detail.quantity
                )

            messages.success(request, f'Compra #{purchase.id} registrada. Total: ${purchase.total}')
            return redirect('purchasing:purchase_list')
    else:
        form = PurchaseForm()
        formset = PurchaseDetailFormSet()

    return render(request, 'purchasing/purchase_form.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(
        Purchase.objects.select_related('supplier')
                        .prefetch_related('details__product'),
        pk=pk
    )
    return render(request, 'purchasing/purchase_detail.html', {'purchase': purchase})


@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        purchase_id = purchase.id
        purchase.delete()
        messages.success(request, f'Compra #{purchase_id} eliminada.')
        return redirect('purchasing:purchase_list')
    return render(request, 'purchasing/purchase_confirm_delete.html', {'object': purchase})
