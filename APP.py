from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = "apuestas_mundial_secret_key_2026_xyz"

# Datos en memoria (se pierden si Vercel reinicia, pero funciona sin errores de write)
partidos = []
apuestas_por_partido = {}

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

        partidos.append({"equipo1": equipo1, "equipo2": equipo2, "fecha": fecha, "hora": hora, "lugar": lugar})
        apuestas_por_partido[len(partidos)-1] = []
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
        flash(f"Apuesta de {nombre} registrada exitosamente!", "success")
        return redirect(url_for("index"))
    return render_template("apostar.html", partido=partidos[partido_id], partido_id=partido_id)

@app.route("/borrar_partido/<int:partido_id>", methods=["POST"])
def borrar_partido(partido_id):
    global partidos, apuestas_por_partido
    try:
        if 0 <= partido_id < len(partidos):
            equipo1 = partidos[partido_id]["equipo1"]
            equipo2 = partidos[partido_id]["equipo2"]
            
            partidos.pop(partido_id)
            
            # Reorganizar índices de apuestas
            if partido_id in apuestas_por_partido:
                del apuestas_por_partido[partido_id]
            
            apuestas_renumeradas = {}
            for old_id, apuestas in sorted(apuestas_por_partido.items()):
                if old_id < partido_id:
                    apuestas_renumeradas[old_id] = apuestas
                elif old_id > partido_id:
                    apuestas_renumeradas[old_id - 1] = apuestas
            
            # Actualizar el diccionario global correctamente
            apuestas_por_partido.clear()
            apuestas_por_partido.update(apuestas_renumeradas)
            
            flash(f"Partido {equipo1} vs {equipo2} eliminado.", "success")
        else:
            flash("El partido no existe.", "error")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "error")
        app.logger.error(f"Error en borrar_partido: {str(e)}")
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
        flash("Apuesta modificada exitosamente.", "success")
        return redirect(url_for("index"))

    return render_template("editar_apuesta.html", partido=partidos[partido_id], apuesta=apuesta,
                           partido_id=partido_id, apuesta_id=apuesta_id)

@app.route("/borrar_apuesta/<int:partido_id>/<int:apuesta_id>", methods=["POST"])
def borrar_apuesta(partido_id, apuesta_id):
    try:
        if partido_id not in apuestas_por_partido or apuesta_id < 0 or apuesta_id >= len(apuestas_por_partido[partido_id]):
            flash("La apuesta no existe.", "error")
            return redirect(url_for("index"))

        apuestas_por_partido[partido_id].pop(apuesta_id)
        flash("Apuesta eliminada.", "success")
    except Exception as e:
        flash(f"Error al eliminar apuesta: {str(e)}", "error")
        app.logger.error(f"Error en borrar_apuesta: {str(e)}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

