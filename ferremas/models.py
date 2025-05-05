from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12)
    phone = models.CharField(max_length=15)
    
    def save(self, *args, **kwargs):
        # Remover puntos pero mantener el guion en el RUT
        self.rut = self.rut.replace('.', '')
        
        # Formato para número de teléfono
        if not self.phone.startswith('+56'):
            self.phone = f'+56{self.phone.lstrip("+")}'
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"