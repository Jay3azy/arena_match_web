# Arena-Match — Interfaz Web Flask
**ITIZ-2201 Base de Datos II — Fase 4**  
Grupo 04: Ontaneda Isaiah, Ortiz Jose, Ramos Kimberlly

---

## Requisitos Previos

- Python 3.10 o superior
- SQL Server (con la base de datos `ArenaMatch` ya creada con el script de la Fase 2)
- ODBC Driver 17 for SQL Server instalado

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la conexión (editar app.py)
#    Busca DB_CONFIG y ajusta el nombre del servidor:
DB_CONFIG = {
    'server': 'localhost\\SQLEXPRESS',  # o tu nombre de servidor
    'database': 'ArenaMatch',
    ...
}

# 4. Ejecutar la aplicación
python app.py
```

Abre tu navegador en: http://localhost:5000

---

## Estructura del Proyecto

```
arena_match/
├── app.py                  # Aplicación Flask principal
├── requirements.txt        # Dependencias Python
├── static/
│   ├── css/style.css       # Estilos (tema oscuro gaming)
│   └── js/main.js          # JavaScript
└── templates/
    ├── base.html           # Plantilla base con navbar
    ├── index.html          # Dashboard
    ├── error.html          # Página de error
    ├── usuarios/           # CRUD de usuarios
    ├── equipos/            # CRUD de equipos
    ├── torneos/            # Gestión de torneos
    ├── inscripciones/      # Inscripción de equipos
    ├── enfrentamientos/    # Partidos y resultados
    └── reportes/           # Reportes operativos
```

---

## Funcionalidades Implementadas

| Caso de Uso | Descripción |
|---|---|
| CU-01 | Registrar equipos y gestionar jugadores |
| CU-02 | Inscribir equipo en torneo (con validación mínimo 3 jugadores) |
| CU-03 | Gestionar torneo (crear, avanzar estado secuencial) |
| CU-05 | Registrar resultado de enfrentamiento |
| — | CRUD completo de Usuarios |
| — | Reportes: Equipos por torneo, Transacciones, Resultados |
