from django.contrib import admin

# Panel de Administracion de Django para la app de tests de clientes

# Register your models here.

# Importo mis modelos de la app de tests para clientes
from .models import SesionDelTest, RespuestaDelUsuario, PreguntaGuardadaPorElUsuario

# Esto me permite usar la biblioteca de Import Export de django
from import_export.admin import ImportExportModelAdmin

# Registro mis modelos de la app de tests para clientes
admin.site.register(SesionDelTest, ImportExportModelAdmin)
admin.site.register(RespuestaDelUsuario)
admin.site.register(PreguntaGuardadaPorElUsuario)


