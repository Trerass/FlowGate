# FlowGate

FlowGate es una aplicacion web desarrollada con Django para visualizar el estado de los parqueaderos universitarios, consultar congestion en los accesos y gestionar funciones basicas de usuario como perfil, historial y pagos.

## Funcionalidades

- Visualizacion del estado de parqueaderos y filas por entrada.
- Indicador de congestion general.
- Soporte basico para dos idiomas.
- Inicio de sesion y registro de usuarios.
- Perfil del usuario y vehiculo.
- Historial de ingresos al parqueadero.
- Simulacion de pagos.

## Estructura del Proyecto

```text
flowgate/
- settings.py
- urls.py

parqueadero/
- models.py
- admin.py
- urls.py
- services/
- views/
- templates/parqueadero/
- static/parqueadero/css/
- migrations/
- tests/
```

## Requisitos

- Python 3.12 o superior
- Django 5.2.11

## Ejecucion Local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Notas

- El proyecto usa SQLite para simplificar la entrega.
- La logica de vistas fue separada por responsabilidad y se movio la logica auxiliar a servicios para facilitar mantenimiento.
- Los estilos fueron centralizados en archivos estaticos para evitar duplicacion entre templates.
