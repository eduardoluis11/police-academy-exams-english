from django.contrib import admin

# Panel de Administracion de Django para la app de tests de clientes

# Register your models here.

# Importo mis modelos de la app de tests para clientes
from .models import SesionDelTest, RespuestaDelUsuario, PreguntaGuardadaPorElUsuario

# Registro mis modelos de la app de tests para clientes
admin.site.register(SesionDelTest)
admin.site.register(RespuestaDelUsuario)
admin.site.register(PreguntaGuardadaPorElUsuario)


