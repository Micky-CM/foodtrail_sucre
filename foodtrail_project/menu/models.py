from django.db import models
from establishments.models import Establishment

class MenuItemType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    def __str__(self): return self.name

class MenuItem(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="menu_items", verbose_name="Establecimiento")
    name = models.CharField(max_length=255, verbose_name="Nombre del Plato")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Precio (Bs.)")
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True, verbose_name="Imagen del Plato")
    menu_item_types = models.ManyToManyField(MenuItemType, blank=True, verbose_name="Tipos de Plato")
    def __str__(self): return f"{self.name} - {self.establishment.name}"