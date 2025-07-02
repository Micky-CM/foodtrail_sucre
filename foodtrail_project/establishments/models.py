from django.db import models
from django.utils.text import slugify

class EstablishmentType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return self.name

class MealType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return self.name

class Establishment(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre del Establecimiento")
    description = models.TextField(verbose_name="Descripción")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    zone = models.CharField(max_length=100, blank=True, verbose_name="Zona")
    street = models.CharField(max_length=255, verbose_name="Calle")
    number = models.CharField(max_length=20, blank=True, verbose_name="Número")
    latitude = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name="Latitud")
    longitude = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True, verbose_name="Longitud")
    establishment_types = models.ManyToManyField(EstablishmentType, verbose_name="Tipos de Establecimiento")
    meal_types = models.ManyToManyField(MealType, blank=True, verbose_name="Horarios de Comida")
    def __str__(self): return self.name

class Image(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="images", verbose_name="Establecimiento")
    image = models.ImageField(upload_to='establishments/', verbose_name="Imagen")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Leyenda")
    def __str__(self): return f"Imagen de {self.establishment.name}"