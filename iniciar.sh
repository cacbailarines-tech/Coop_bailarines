#!/bin/bash
echo "================================================"
echo "  Cooperativa Bailarines - Sistema v3           "
echo "================================================"
pip install -r requirements.txt --quiet
python manage.py migrate --verbosity=0
python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import PerfilUsuario
if not User.objects.filter(username='admin').exists():
    u=User.objects.create_superuser('admin','admin@bailarines.coop','admin123',first_name='Administrador',last_name='Sistema')
    PerfilUsuario.objects.create(usuario=u,rol='admin')
    print('Usuario admin creado: admin / admin123')
else:
    print('Usuario admin: OK')
"
echo ""
echo "  Sistema listo en: http://localhost:8000"
echo "  Portal socios:    http://localhost:8000/portal/"
echo "================================================"
python manage.py runserver 0.0.0.0:8000
