# ADR-004: Usar Django (API REST) y React (PWA) como stack tecnológico

- Estado: Aceptado
- Fecha: 2026-09-30
- Decisores: [AJUSTAR: nombres de los 3 integrantes]

## Contexto
El MVP debe salir en 1 mes (R-01) con 3 developers que dominan Python/Django, PostgreSQL, MySQL, Node.js, React, Vue.js, Java y C/C++ (R-02), con un solo servidor de bajo costo (R-03). El monolito modular (ADR-001) necesita módulos separados; la reserva usa transacciones en PostgreSQL (ADR-002) y los recordatorios una cola Celery + Redis (ADR-003). El personal de admisión debe administrar cupos (RF-06), los roles deben restringir el acceso a datos de salud (RF-07, QA-03) y el rendimiento en el pico de 7:00 a. m. es crítico (QA-01).

## Alternativas consideradas
1. **Django + Django REST Framework (backend) y React (PWA, frontend).**
2. **Node.js (backend) y React (PWA).** Hay dominio de ambos, pero la cola de tareas, la autenticación por roles y el panel de administración habría que armarlos o integrarlos por separado.
3. **Java (backend) y Vue.js (frontend).** Es viable para el equipo, pero con más configuración inicial y menos velocidad para un MVP de 1 mes.

## Decisión
Usaremos Django con Django REST Framework para el backend, organizando cada módulo del monolito (Disponibilidad y cupos, Reservas, Agenda médica, Notificaciones, Identidad y acceso) como una app de Django. Usaremos React para la PWA. Nginx servirá los archivos estáticos y reenviará las peticiones `/api` al servidor de aplicaciones WSGI de Django. Django se conectará a PostgreSQL (ADR-002) y a Celery con Redis (ADR-003).

## Consecuencias
- Positivas: el equipo ya domina el stack, lo que protege el plazo (R-01, R-02); Celery se integra de forma natural con Python (ADR-003); Django trae autenticación, permisos por rol (RF-07, QA-03) y un panel de administración que cubre buena parte de RF-06 sin desarrollo propio; las apps de Django dan una separación de módulos coherente con el ADR-001.
- Negativas / riesgos: Python rinde menos por petición que Node.js o Java, por lo que el pico de QA-01 debe validarse con pruebas de carga y caché donde haga falta; mantener backend y frontend separados exige coordinar dos proyectos y contratos de API; la PWA con React requiere cuidar el rendimiento en celulares de gama baja.
