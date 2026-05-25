"""
Arena-Match - Aplicación Web Flask (Versión Final Supabase / PostgreSQL)
ITIZ-2201 Base de Datos II - Fase 4
Grupo 04: Ontaneda Isaiah, Ortiz Jose, Ramos Kimberlly
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'arenamatch_secret_2026'

# Configuración de la cadena de conexión nativa de Supabase
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:basegrupo42026@db.synohlxxdftnfipokkmu.supabase.co:5432/postgres'
)

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def query_db(sql, params=None, fetch='all'):
    conn = get_connection()
    # Usamos RealDictCursor para mantener la estructura de diccionarios llave-valor
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(sql, params or [])
    if fetch == 'one':
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(row) if row else None
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]

def execute_db(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or [])
    conn.commit()
    cursor.close()
    conn.close()


# =============================================
# DASHBOARD
# =============================================

@app.route('/')
def index():
    try:
        # PostgreSQL retorna los alias COUNT(*) estrictamente en minúsculas. 
        # Forzamos las llaves en mayúsculas/minúsculas según tus HTMLs originales.
        stats = {
            'jugadores': query_db("SELECT COUNT(*) AS n FROM Jugadores", fetch='one')['n'],
            'equipos':   query_db("SELECT COUNT(*) AS n FROM Equipos",   fetch='one')['n'],
            'torneos':   query_db("SELECT COUNT(*) AS n FROM Torneos",   fetch='one')['n'],
            'partidas':  query_db("SELECT COUNT(*) AS n FROM Partidas",  fetch='one')['n'],
        }
        
        # Agregamos alias con comillas dobles para que el diccionario respete las mayúsculas en el HTML
        torneos_activos = query_db("""
            SELECT t.NombreTorneo AS "NombreTorneo", t.Estado AS "Estado", v.NombreJuego AS "NombreJuego"
            FROM Torneos t
            JOIN Videojuegos v ON t.ID_Videojuego = v.ID_Videojuego
            ORDER BY t.ID_Torneo DESC
            LIMIT 5
        """)
        return render_template('index.html', stats=stats, torneos=torneos_activos)
    except Exception as e:
        return render_template('error.html', error=str(e))


# =============================================
# JUGADORES
# =============================================

@app.route('/jugadores')
def jugadores():
    # Mapeamos explícitamente las columnas para asegurar compatibilidad exacta con tus vistas HTML antiguas
    data = query_db("""
        SELECT ID_Jugador AS "ID_Jugador", Nombre AS "Nombre", Apellido AS "Apellido", 
               Nickname AS "Nickname", Correo AS "Correo", RolPlataforma AS "RolPlataforma" 
        FROM Jugadores ORDER BY ID_Jugador
    """)
    return render_template('usuarios/lista.html', jugadores=data)

@app.route('/jugadores/nuevo', methods=['GET', 'POST'])
def jugador_nuevo():
    if request.method == 'POST':
        try:
            execute_db("""
                INSERT INTO Jugadores (Nombre, Apellido, Nickname, Correo, RolPlataforma)
                VALUES (%s, %s, %s, %s, %s)
            """, [request.form['nombre'], request.form['apellido'],
                  request.form['nickname'], request.form['correo'], request.form['rol']])
            flash('Jugador registrado exitosamente.', 'success')
            return redirect(url_for('jugadores'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('usuarios/form.html', roles=['Capitán', 'Miembro'], jugador=None)

@app.route('/jugadores/editar/<int:id>', methods=['GET', 'POST'])
def jugador_editar(id):
    if request.method == 'POST':
        try:
            execute_db("""
                UPDATE Jugadores SET Nombre=%s, Apellido=%s, Nickname=%s, Correo=%s, RolPlataforma=%s
                WHERE ID_Jugador=%s
            """, [request.form['nombre'], request.form['apellido'],
                  request.form['nickname'], request.form['correo'], request.form['rol'], id])
            flash('Jugador actualizado.', 'success')
            return redirect(url_for('jugadores'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            
    jugador = query_db("""
        SELECT ID_Jugador AS "ID_Jugador", Nombre AS "Nombre", Apellido AS "Apellido", 
               Nickname AS "Nickname", Correo AS "Correo", RolPlataforma AS "RolPlataforma" 
        FROM Jugadores WHERE ID_Jugador=%s
    """, [id], fetch='one')
    return render_template('usuarios/form.html', roles=['Capitán', 'Miembro'], jugador=jugador)

@app.route('/jugadores/eliminar/<int:id>', methods=['POST'])
def jugador_eliminar(id):
    try:
        execute_db("DELETE FROM Jugadores WHERE ID_Jugador=%s", [id])
        flash('Jugador eliminado.', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'danger')
    return redirect(url_for('jugadores'))


# =============================================
# EQUIPOS
# =============================================

@app.route('/equipos')
def equipos():
    data = query_db("""
        SELECT e.ID_Equipo AS "ID_Equipo", e.NombreEquipo AS "NombreEquipo", 
               v.NombreJuego AS "NombreJuego", e.FechaCreacion AS "FechaCreacion",
               j.Nombre || ' ' || j.Apellido AS "Capitan",
               COUNT(me.ID_Jugador) AS "NumJugadores"
        FROM Equipos e
        JOIN Videojuegos v       ON e.ID_Videojuego = v.ID_Videojuego
        JOIN Jugadores j         ON e.ID_Capitan    = j.ID_Jugador
        LEFT JOIN Miembros_Equipo me ON e.ID_Equipo = me.ID_Equipo AND me.Activo = TRUE
        GROUP BY e.ID_Equipo, e.NombreEquipo, v.NombreJuego, e.FechaCreacion, j.Nombre, j.Apellido
        ORDER BY e.ID_Equipo
    """)
    return render_template('equipos/lista.html', equipos=data)

@app.route('/equipos/nuevo', methods=['GET', 'POST'])
def equipo_nuevo():
    if request.method == 'POST':
        try:
            execute_db("""
                INSERT INTO Equipos (NombreEquipo, FechaCreacion, ID_Capitan, ID_Videojuego)
                VALUES (%s, %s, %s, %s)
            """, [request.form['nombre'], date.today().isoformat(),
                  int(request.form['capitan_id']), int(request.form['videojuego_id'])])
            flash('Equipo creado exitosamente.', 'success')
            return redirect(url_for('equipos'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            
    videojuegos = query_db('SELECT ID_Videojuego AS "ID_Videojuego", NombreJuego AS "NombreJuego" FROM Videojuegos ORDER BY NombreJuego')
    capitanes   = query_db('SELECT ID_Jugador AS "ID_Jugador", Nombre || \' \' || Apellido AS "NombreCompleto" FROM Jugadores WHERE RolPlataforma = \'Capitán\' ORDER BY Nombre')
    return render_template('equipos/form.html', equipo=None, videojuegos=videojuegos, capitanes=capitanes)

@app.route('/equipos/<int:id>')
def equipo_detalle(id):
    equipo = query_db("""
        SELECT e.ID_Equipo AS "ID_Equipo", e.NombreEquipo AS "NombreEquipo", e.FechaCreacion AS "FechaCreacion",
               v.NombreJuego AS "NombreJuego", j.Nombre || ' ' || j.Apellido AS "NombreCapitan"
        FROM Equipos e
        JOIN Videojuegos v ON e.ID_Videojuego = v.ID_Videojuego
        JOIN Jugadores j   ON e.ID_Capitan    = j.ID_Jugador
        WHERE e.ID_Equipo = %s
    """, [id], fetch='one')
    
    miembros = query_db("""
        SELECT j.ID_Jugador AS "ID_Jugador", j.Nombre AS "Nombre", j.Apellido AS "Apellido", 
               j.Nickname AS "Nickname", j.RolPlataforma AS "RolPlataforma", 
               me.FechaIngreso AS "FechaIngreso", me.Activo AS "Activo"
        FROM Miembros_Equipo me
        JOIN Jugadores j ON me.ID_Jugador = j.ID_Jugador
        WHERE me.ID_Equipo = %s ORDER BY me.FechaIngreso
    """, [id])
    return render_template('equipos/detalle.html', equipo=equipo, jugadores=miembros)

@app.route('/equipos/editar/<int:id>', methods=['GET', 'POST'])
def equipo_editar(id):
    if request.method == 'POST':
        try:
            execute_db("""
                UPDATE Equipos SET NombreEquipo=%s, ID_Capitan=%s, ID_Videojuego=%s
                WHERE ID_Equipo=%s
            """, [request.form['nombre'], int(request.form['capitan_id']),
                  int(request.form['videojuego_id']), id])
            flash('Equipo actualizado.', 'success')
            return redirect(url_for('equipos'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            
    equipo      = query_db('SELECT ID_Equipo AS "ID_Equipo", NombreEquipo AS "NombreEquipo", ID_Capitan AS "ID_Capitan", ID_Videojuego AS "ID_Videojuego" FROM Equipos WHERE ID_Equipo=%s', [id], fetch='one')
    videojuegos = query_db('SELECT ID_Videojuego AS "ID_Videojuego", NombreJuego AS "NombreJuego" FROM Videojuegos ORDER BY NombreJuego')
    capitanes   = query_db('SELECT ID_Jugador AS "ID_Jugador", Nombre || \' \' || Apellido AS "NombreCompleto" FROM Jugadores WHERE RolPlataforma = \'Capitán\' ORDER BY Nombre')
    return render_template('equipos/form.html', equipo=equipo, videojuegos=videojuegos, capitanes=capitanes)


# =============================================
# TORNEOS
# =============================================

@app.route('/torneos')
def torneos():
    data = query_db("""
        SELECT t.ID_Torneo AS "ID_Torneo", t.NombreTorneo AS "NombreTorneo", 
               v.NombreJuego AS "NombreJuego", t.FechaInicio AS "FechaInicio", 
               t.FechaFin AS "FechaFin", t.Estado AS "Estado"
        FROM Torneos t
        JOIN Videojuegos v ON t.ID_Videojuego = v.ID_Videojuego
        ORDER BY t.ID_Torneo DESC
    """)
    return render_template('torneos/lista.html', torneos=data)

@app.route('/torneos/nuevo', methods=['GET', 'POST'])
def torneo_nuevo():
    if request.method == 'POST':
        try:
            execute_db("""
                INSERT INTO Torneos (NombreTorneo, FechaInicio, FechaFin, Estado, ID_Videojuego)
                VALUES (%s, %s, %s, 'Planificación', %s)
            """, [request.form['nombre'], request.form['fecha_inicio'],
                  request.form['fecha_fin'], int(request.form['videojuego_id'])])
            flash('Torneo creado exitosamente.', 'success')
            return redirect(url_for('torneos'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    videojuegos = query_db('SELECT ID_Videojuego AS "ID_Videojuego", NombreJuego AS "NombreJuego" FROM Videojuegos ORDER BY NombreJuego')
    return render_template('torneos/form.html', torneo=None, videojuegos=videojuegos)

@app.route('/torneos/<int:id>')
def torneo_detalle(id):
    torneo = query_db("""
        SELECT t.ID_Torneo AS "ID_Torneo", t.NombreTorneo AS "NombreTorneo", 
               t.FechaInicio AS "FechaInicio", t.FechaFin AS "FechaFin", 
               t.Estado AS "Estado", v.NombreJuego AS "NombreJuego" 
        FROM Torneos t
        JOIN Videojuegos v ON t.ID_Videojuego = v.ID_Videojuego
        WHERE t.ID_Torneo = %s
    """, [id], fetch='one')
    
    partidas = query_db("""
        SELECT p.ID_Partida AS "ID_Partida", p.FechaHora AS "FechaHora", p.Resultado_Final AS "Resultado_Final",
               a.Nombre || ' ' || a.Apellido AS "Arbitro"
        FROM Partidas p
        JOIN Arbitros a ON p.ID_Arbitro = a.ID_Arbitro
        WHERE p.ID_Torneo = %s ORDER BY p.FechaHora
    """, [id])
    return render_template('torneos/detalle.html', torneo=torneo, partidas=partidas)

@app.route('/torneos/estado/<int:id>', methods=['POST'])
def torneo_cambiar_estado(id):
    estados = ['Planificación', 'Inscripciones Abiertas', 'En Curso', 'Finalizado']

    # Buscamos usando el alias correcto en mayúsculas
    torneo = query_db('SELECT Estado AS "Estado" FROM Torneos WHERE ID_Torneo=%s', [id], fetch='one')
    if torneo:
        try:
            idx = estados.index(torneo['Estado'])
            if idx < len(estados) - 1:
                execute_db("UPDATE Torneos SET Estado=%s WHERE ID_Torneo=%s", [estados[idx + 1], id])
                flash(f'Estado cambiado a: {estados[idx + 1]}', 'success')
            else:
                flash('El torneo ya está finalizado.', 'warning')
        except ValueError:
            flash('Estado desconocido.', 'danger')
    return redirect(url_for('torneo_detalle', id=id))


# =============================================
# PARTIDAS
# =============================================

@app.route('/partidas')
def partidas():
    data = query_db("""
        SELECT p.ID_Partida AS "ID_Partida", p.FechaHora AS "FechaHora", p.Resultado_Final AS "Resultado_Final",
               t.NombreTorneo AS "NombreTorneo", a.Nombre || ' ' || a.Apellido AS "Arbitro"
        FROM Partidas p
        JOIN Torneos t  ON p.ID_Torneo  = t.ID_Torneo
        JOIN Arbitros a ON p.ID_Arbitro = a.ID_Arbitro
        ORDER BY p.FechaHora DESC
    """)
    return render_template('enfrentamientos/lista.html', partidas=data)

@app.route('/partidas/resultado/<int:id>', methods=['GET', 'POST'])
def registrar_resultado(id):
    if request.method == 'POST':
        execute_db("UPDATE Partidas SET Resultado_Final=%s WHERE ID_Partida=%s",
                   [request.form['resultado'], id])
        flash('Resultado registrado.', 'success')
        return redirect(url_for('partidas'))
        
    partida = query_db("""
        SELECT p.ID_Partida AS "ID_Partida", p.FechaHora AS "FechaHora", p.Resultado_Final AS "Resultado_Final", 
               t.NombreTorneo AS "NombreTorneo", a.Nombre || ' ' || a.Apellido AS "Arbitro"
        FROM Partidas p
        JOIN Torneos t  ON p.ID_Torneo  = t.ID_Torneo
        JOIN Arbitros a ON p.ID_Arbitro = a.ID_Arbitro
        WHERE p.ID_Partida = %s
    """, [id], fetch='one')
    return render_template('enfrentamientos/resultado.html', enf=partida)


# =============================================
# REPORTES
# =============================================

@app.route('/reportes')
def reportes():
    return render_template('reportes/index.html')

@app.route('/reportes/equipos_torneo')
def reporte_equipos_torneo():
    data = query_db("""
        SELECT t.NombreTorneo AS "NombreTorneo", v.NombreJuego AS "NombreJuego", 
               COUNT(DISTINCT p.ID_Partida) AS "TotalPartidas"
        FROM Torneos t
        JOIN Videojuegos v ON t.ID_Videojuego = v.ID_Videojuego
        LEFT JOIN Partidas p ON t.ID_Torneo = p.ID_Torneo
        GROUP BY t.ID_Torneo, t.NombreTorneo, v.NombreJuego
        ORDER BY t.NombreTorneo
    """)
    return render_template('reportes/equipos_torneo.html', data=data)

@app.route('/reportes/partidas')
def reporte_partidas():
    data = query_db("""
        SELECT t.NombreTorneo AS "NombreTorneo", p.FechaHora AS "FechaHora",
               COALESCE(p.Resultado_Final, 'Pendiente') AS "Resultado",
               a.Nombre || ' ' || a.Apellido AS "Arbitro"
        FROM Partidas p
        JOIN Torneos t  ON p.ID_Torneo  = t.ID_Torneo
        JOIN Arbitros a ON p.ID_Arbitro = a.ID_Arbitro
        ORDER BY p.FechaHora DESC
    """)
    return render_template('reportes/resultados.html', data=data)

@app.route('/reportes/sanciones_activas')
def reporte_sanciones_activas():
    data = query_db("""
        SELECT j.Nickname AS "Nickname", j.Nombre || ' ' || j.Apellido AS "NombreCompleto",
               s.Motivo AS "Motivo", s.FechaInicio AS "FechaInicio", s.FechaFin AS "FechaFin"
        FROM Sanciones s
        JOIN Jugadores j ON s.ID_Jugador = j.ID_Jugador
        WHERE s.Activa = TRUE ORDER BY s.FechaFin
    """)
    return render_template('reportes/transacciones.html', sanciones=data)


if __name__ == '__main__':
    # Agregamos lectura dinámica de puertos requerida para entornos como Vercel/Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


    #final del código o eso espero 