"""Vista de despliegue de CitaSalud Arequipa (Python Diagrams).
Requiere: pip install diagrams  y Graphviz instalado en el sistema.
Ejecutar: python despliegue.py  -> genera img/despliegue.png
"""
import os
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Client
from diagrams.onprem.network import Nginx, Internet
from diagrams.programming.framework import Django, React
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.queue import Celery
from diagrams.onprem.monitoring import Grafana
from diagrams.generic.device import Mobile

base = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(base, "img"), exist_ok=True)
graph_attr = {"fontsize": "20", "bgcolor": "white", "pad": "0.3"}

with Diagram("CitaSalud Arequipa - Vista de despliegue",
             filename=os.path.join(base, "img", "despliegue"), show=False,
             direction="LR", graph_attr=graph_attr, outformat="png"):
    with Cluster("Usuarios"):
        pacientes = Mobile("Pacientes\n(PWA en celular)")
        personal = Client("Admisión y médicos\n(navegador en PC)")
    with Cluster("Servidor en la nube (un solo VPS)"):
        proxy = Nginx("Nginx\n(HTTPS + PWA estática)")
        front = React("Frontend PWA\n(archivos estáticos)")
        with Cluster("Monolito modular"):
            app = Django("Django API\n(5 módulos)")
            worker = Celery("Worker y programador\nde recordatorios")
        cola = Redis("Redis\n(cola de tareas)")
        db = PostgreSQL("PostgreSQL\n(cupos y citas)")
        mon = Grafana("Monitoreo\n(herramienta por definir)")
    wa = Internet("WhatsApp Business API\n(servicio externo)")

    [pacientes, personal] >> Edge(label="HTTPS") >> proxy
    proxy >> Edge(label="sirve", style="dotted") >> front
    proxy >> Edge(label="/api") >> app
    app >> Edge(label="reserva (transacción)") >> db
    app >> Edge(label="encola recordatorio") >> cola >> worker
    worker >> Edge(label="envía", style="dashed") >> wa
    app >> Edge(style="dotted") >> mon
