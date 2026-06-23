from flask import Flask, render_template, request, redirect, flash, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "apuestas_mundial_secret_key_2026_xyz"

DATA_FILE = "datos.json"

partidos = []
apuestas_por_partido = {}

def cargar_datos():
    global partidos, apuestas_por_partido
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                partidos = datos.get("partidos", [])
                apuestas_por_partido = {int(k): v for k, v in datos.get("apuestas_por_partido", {}).items()}
                
                # Asegurar que todos los partidos tengan los campos necesarios
                for p in partidos:
                    if "marcador_final" not in p:
                        p["marcador_final"] = None
                    if "finalizado" not in p:
                        p["finalizado"] = False
    except:
        partidos = []
        apuestas_por_partido = {}

def guardar_datos():
    try:
        datos = {
            "partidos": partidos,
            "apuestas_por_partido": {str(k): v for k, v in apuestas_por_partido.items()}
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        # Silenciosamente ignorar si no se puede guardar (Vercel read-only filesystem)
        pass

@app.route("/")
def index():
    total_apostadores = sum(len(apuestas_por_partido.get(i, [])) for i in range(len(partidos)))
    total_dinero = sum(sum(a.get("dinero", 0) for a in apuestas_por_partido.get(i, [])) for i in range(len(partidos)))
    return render_template("index.html", partidos=partidos, apuestas_por_partido=apuestas_por_partido,
                           total_apostadores=total_apostadores, total_dinero=total_dinero)

@app.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    if request.method == "POST":
        equipo1 = request.form["equipo1"].strip()
        equipo2 = request.form["equipo2"].strip()
        fecha = request.form["fecha"].strip()
        hora = request.form["hora"].strip()
        lugar = request.form["lugar"].strip()

        if not equipo1 or not equipo2 or not fecha or not hora or not lugar:
            flash("Todos los campos del partido son requeridos.", "error")
            return redirect(url_for("ingresar"))

        partidos.append({
            "equipo1": equipo1, 
            "equipo2": equipo2, 
            "fecha": fecha, 
            "hora": hora, 
            "lugar": lugar,
            "marcador_final": None,
            "finalizado": False
        })
        apuestas_por_partido[len(partidos)-1] = []
        guardar_datos()
        flash(f"Partido {equipo1} vs {equipo2} registrado con exito.", "success")
        return redirect(url_for("index"))
    return render_template("ingresar.html")

@app.route("/apostar/<int:partido_id>", methods=["GET", "POST"])
def apostar(partido_id):
    if partido_id < 0 or partido_id >= len(partidos):
        flash("El partido seleccionado no existe.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        try:
            dinero = int(request.form["dinero"])
        except ValueError:
            dinero = 0
        marcador = request.form["marcador"].strip()

        if not nombre or dinero <= 0 or not marcador:
            flash("Por favor completa todos los campos. El dinero debe ser mayor a 0.", "error")
            return redirect(url_for("apostar", partido_id=partido_id))

        apuesta = {"nombre": nombre, "dinero": dinero, "marcador": marcador}
        if partido_id not in apuestas_por_partido:
            apuestas_por_partido[partido_id] = []
        apuestas_por_partido[partido_id].append(apuesta)
        guardar_datos()
        flash(f"Apuesta de {nombre} registrada exitosamente!", "success")
        return redirect(url_for("index"))
    return render_template("apostar.html", partido=partidos[partido_id], partido_id=partido_id)

@app.route("/borrar_partido/<int:partido_id>", methods=["POST"])
def borrar_partido(partido_id):
    global partidos, apuestas_por_partido
    if 0 <= partido_id < len(partidos):
        equipo1 = partidos[partido_id]["equipo1"]
        equipo2 = partidos[partido_id]["equipo2"]
        partidos.pop(partido_id)
        
        # Eliminar apuestas del partido eliminado
        if partido_id in apuestas_por_partido:
            del apuestas_por_partido[partido_id]
        
        # Reorganizar índices
        apuestas_renumeradas = {}
        for old_id, apuestas in sorted(apuestas_por_partido.items()):
            if old_id < partido_id:
                apuestas_renumeradas[old_id] = apuestas
            elif old_id > partido_id:
                apuestas_renumeradas[old_id - 1] = apuestas
        
        apuestas_por_partido.clear()
        apuestas_por_partido.update(apuestas_renumeradas)
        
        guardar_datos()
        flash(f"Partido {equipo1} vs {equipo2} eliminado.", "success")
    else:
        flash("El partido no existe.", "error")
    return redirect(url_for("index"))

@app.route("/editar_apuesta/<int:partido_id>/<int:apuesta_id>", methods=["GET", "POST"])
def editar_apuesta(partido_id, apuesta_id):
    if partido_id not in apuestas_por_partido or apuesta_id < 0 or apuesta_id >= len(apuestas_por_partido[partido_id]):
        flash("La apuesta no existe.", "error")
        return redirect(url_for("index"))

    apuesta = apuestas_por_partido[partido_id][apuesta_id]

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        try:
            dinero = int(request.form["dinero"])
        except ValueError:
            dinero = 0
        marcador = request.form["marcador"].strip()

        if not nombre or dinero <= 0 or not marcador:
            flash("Por favor ingresa datos validos.", "error")
            return redirect(url_for("editar_apuesta", partido_id=partido_id, apuesta_id=apuesta_id))

        apuesta["nombre"] = nombre
        apuesta["dinero"] = dinero
        apuesta["marcador"] = marcador
        guardar_datos()
        flash("Apuesta modificada exitosamente.", "success")
        return redirect(url_for("index"))

    return render_template("editar_apuesta.html", partido=partidos[partido_id], apuesta=apuesta,
                           partido_id=partido_id, apuesta_id=apuesta_id)

@app.route("/borrar_apuesta/<int:partido_id>/<int:apuesta_id>", methods=["POST"])
def borrar_apuesta(partido_id, apuesta_id):
    if partido_id not in apuestas_por_partido or apuesta_id < 0 or apuesta_id >= len(apuestas_por_partido[partido_id]):
        flash("La apuesta no existe.", "error")
        return redirect(url_for("index"))

    apuestas_por_partido[partido_id].pop(apuesta_id)
    guardar_datos()
    flash("Apuesta eliminada.", "success")
    return redirect(url_for("index"))

def compare_scores(expected, actual):
    """
    Compara dos marcadores en formato 'X-Y'
    Retorna True si son iguales, False si no
    """
    try:
        expected = expected.strip().lower()
        actual = actual.strip().lower()
        return expected == actual
    except:
        return False

@app.route("/marcar_resultado/<int:partido_id>", methods=["POST"])
def marcar_resultado(partido_id):
    """
    Marca el resultado final de un partido y evalúa quién ganó
    """
    if partido_id < 0 or partido_id >= len(partidos):
        flash("El partido no existe.", "error")
        return redirect(url_for("index"))
    
    marcador_final = request.form.get("marcador_final", "").strip()
    
    if not marcador_final:
        flash("Por favor ingresa un marcador final (formato: X-Y).", "error")
        return redirect(url_for("index"))
    
    # Marcar partido como finalizado
    partidos[partido_id]["marcador_final"] = marcador_final
    partidos[partido_id]["finalizado"] = True
    
    # Evaluar apuestas
    if partido_id in apuestas_por_partido:
        for apuesta in apuestas_por_partido[partido_id]:
            # Comparar marcador de la apuesta con el marcador final
            if compare_scores(apuesta["marcador"], marcador_final):
                apuesta["resultado"] = "ganador"
            else:
                apuesta["resultado"] = "perdedor"
    
    guardar_datos()
    flash(f"Resultado marcado: {partidos[partido_id]['equipo1']} vs {partidos[partido_id]['equipo2']} = {marcador_final}", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    cargar_datos()
    app.run(debug=True)

