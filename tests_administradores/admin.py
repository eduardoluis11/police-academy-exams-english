from django.contrib import admin

""" Panel de Administración de Django. Aquí podré ver y gestionar mis modelos de la app de tests para administradores
desde el panel de admin de Django.

Como puse una relación de muchos a muchos entre el modelo de PreguntaDelTest y el modelo de Test, se creará 
automáticamente una tabla intermedia que relacionará ambos modelos. Quiero renderizar esta tabla intermedia en el panel
de admin de Django para poder ver las relaciones entre las preguntas y los tests.
"""

# Register your models here.

# Esto importa mis modelos de la app de tests para administradores
from .models import PreguntaDelTest, Test

# Esto me muestra mis modelos en el panel de admin de Django
admin.site.register(PreguntaDelTest)
admin.site.register(Test)
# admin.site.register(TestPreguntaRelation)

