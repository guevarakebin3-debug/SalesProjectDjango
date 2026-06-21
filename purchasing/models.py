from django.db import models
from billing.models import Supplier, Product


class Purchase(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT,
        related_name='purchases', verbose_name='Proveedor'
    )
    document_number = models.CharField(max_length=20, verbose_name='N° Documento')
    purchase_date = models.DateField(auto_now_add=True, verbose_name='Fecha')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='IVA')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Compra'
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


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE,
        related_name='details', verbose_name='Compra'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT,
        related_name='purchase_details', verbose_name='Producto'
    )
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Costo Unitario')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_cost * self.quantity
        super().save(*args, **kwargs)
