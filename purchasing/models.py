from decimal import Decimal
from django.db import models
from billing.models import Supplier, Product
from shared.money import round_money


class Purchase(models.Model):
    BORRADOR   = 0
    CONFIRMADA = 1
    ANULADA    = 2
    ESTADO_CHOICES = [
        (BORRADOR,   'Borrador'),
        (CONFIRMADA, 'Confirmada'),
        (ANULADA,    'Anulada'),
    ]

    supplier        = models.ForeignKey(
                          Supplier, on_delete=models.PROTECT,
                          related_name='purchases', verbose_name='Proveedor')
    document_number = models.CharField(max_length=20, verbose_name='N° Documento')
    purchase_date   = models.DateField(auto_now_add=True, verbose_name='Fecha')
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')
    tax             = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='IVA')
    total           = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
    estado          = models.PositiveSmallIntegerField(
                          choices=ESTADO_CHOICES, default=BORRADOR, verbose_name='Estado')
    is_active       = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name        = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-purchase_date', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['document_number', 'supplier'],
                name='unique_purchase_per_supplier'
            )
        ]

    def __str__(self):
        return f'Compra #{self.id} – {self.supplier.name}'

    @property
    def can_confirm(self):    return self.estado == self.BORRADOR
    @property
    def can_edit(self):       return self.estado == self.BORRADOR
    @property
    def can_delete(self):     return self.estado == self.BORRADOR
    @property
    def can_cancel(self):     return self.estado == self.CONFIRMADA
    @property
    def can_credit_note(self):return self.estado == self.CONFIRMADA

    @property
    def estado_badge_class(self):
        return {
            self.BORRADOR:   'bg-secondary',
            self.CONFIRMADA: 'bg-success',
            self.ANULADA:    'bg-danger',
        }.get(self.estado, 'bg-secondary')


class PurchaseDetail(models.Model):
    purchase   = models.ForeignKey(
                     Purchase, on_delete=models.CASCADE,
                     related_name='details', verbose_name='Compra')
    product    = models.ForeignKey(
                     Product, on_delete=models.PROTECT,
                     related_name='purchase_details', verbose_name='Producto')
    quantity   = models.PositiveIntegerField(verbose_name='Cantidad')
    unit_cost  = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Costo Unitario')
    subtotal   = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='IVA')

    class Meta:
        verbose_name        = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.subtotal   = round_money(self.unit_cost * Decimal(self.quantity))
        self.tax_amount = round_money(self.subtotal * self.product.tax_rate)
        super().save(*args, **kwargs)


class SupplierCreditNote(models.Model):
    TIPO_TOTAL   = 'total'
    TIPO_PARCIAL = 'parcial'
    TIPO_CHOICES = [
        (TIPO_TOTAL,   'Devolución Total'),
        (TIPO_PARCIAL, 'Devolución Parcial'),
    ]

    purchase  = models.ForeignKey(
                    Purchase, on_delete=models.PROTECT,
                    related_name='credit_notes', verbose_name='Compra')
    date      = models.DateField(auto_now_add=True, verbose_name='Fecha')
    tipo      = models.CharField(
                    max_length=10, choices=TIPO_CHOICES,
                    default=TIPO_TOTAL, verbose_name='Tipo')
    amount    = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    reason    = models.CharField(max_length=300, verbose_name='Motivo')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Nota de Crédito a Proveedor'
        verbose_name_plural = 'Notas de Crédito a Proveedores'
        ordering = ['-date', '-id']

    def __str__(self):
        return f'NC-P{self.id} → Compra #{self.purchase_id}'
