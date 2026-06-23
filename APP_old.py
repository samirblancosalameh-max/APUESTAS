from flask import Flask, render_template, request, redirect, flash, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "apuestas_mundial_secret_key_2026_xyz"

# Configurar MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/apuestas_mundial")
client = MongoClient(MONGODB_URI)
db = client.get_default_database()
partidos_collection = db.partidos
apuestas_collection = db.apuestas

def obtener_partidos():
    """Obtiene todos los partidos de MongoDB"""
    return list(partidos_collection.find())

def obtener_apuestas_por_partido(partido_id):
    """Obtiene todas las apuestas de un partido"""
    try:
        return list(apuestas_collection.find({"partido_id": ObjectId(partido_id)}))
    except:
        return []

def obtener_apuesta(partido_id, apuesta_id):
    """Obtiene una apuesta específica"""
    try:
        return apuestas_collection.find_one({
            "_id": ObjectId(apuesta_id),
            "partido_id": ObjectId(partido_id)
        })
    except:
        return None

@app.route("/")
def index():
    partidos = obtener_partidos()
    
    # Crear estructura apuestas_por_partido para compatibilidad con template
    apuestas_por_partido = {}
    for i, partido in enumerate(partidos):
        apuestas_por_partido[i] = obtener_apuestas_por_partido(str(partido["_id"]))
    
    total_apostadores = sum(len(apuestas) for apuestas in apuestas_por_partido.values())
    total_dinero = sum(
        sum(a.get("dinero", 0) for a in apuestas)
        for apuestas in apuestas_por_partido.values()
    )
    
    return render_template(
        "index.html",
        partidos=partidos,
        apuestas_por_partido=apuestas_por_partido,
        total_apostadores=total_apostadores,
        total_dinero=total_dinero
    )

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

        partido = {
            "equipo1": equipo1,
            "equipo2": equipo2,
            "fecha": fecha,
            "hora": hora,
            "lugar": lugar
        }
        partidos_collection.insert_one(partido)
        flash(f"Partido {equipo1} vs {equipo2} registrado con exito.", "success")
        return redirect(url_for("index"))
    
    return render_template("ingresar.html")

@app.route("/apostar/<int:partido_id>", methods=["GET", "POST"])
def apostar(partido_id):
    partidos = obtener_partidos()
    
    if partido_id < 0 or partido_id >= len(partidos):
        flash("El partido seleccionado no existe.", "error")
        return redirect(url_for("index"))

    partido = partidos[partido_id]
    partido_obj_id = str(partido["_id"])

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

        apuesta = {
            "partido_id": ObjectId(partido_obj_id),
            "nombre": nombre,
            "dinero": dinero,
            "marcador": marcador
        }
        apuestas_collection.insert_one(apuesta)
        flash(f"Apuesta de {nombre} registrada exitosamente!", "success")
        return redirect(url_for("index"))
    
    return render_template("apostar.html", partido=partido, partido_id=partido_id)

@app.route("/borrar_partido/<int:partido_id>", methods=["POST"])
def borrar_partido(partido_id):
    try:
        partidos = obtener_partidos()
        
        if partido_id < 0 or partido_id >= len(partidos):
            flash("El partido no existe.", "error")
            return redirect(url_for("index"))
        
        partido = partidos[partido_id]
        equipo1 = partido["equipo1"]
        equipo2 = partido["equipo2"]
        partido_obj_id = ObjectId(partido["_id"])
        
        # Eliminar el partido
        partidos_collection.delete_one({"_id": partido_obj_id})
        
        # Eliminar todas las apuestas del partido
        apuestas_collection.delete_many({"partido_id": partido_obj_id})
        
        flash(f"Partido {equipo1} vs {equipo2} eliminado.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "error")
        app.logger.error(f"Error en borrar_partido: {str(e)}")
    
    return redirect(url_for("index"))

@app.route("/editar_apuesta/<int:partido_id>/<apuesta_id>", methods=["GET", "POST"])
def editar_apuesta(partido_id, apuesta_id):
    partidos = obtener_partidos()
    
    if partido_id < 0 or partido_id >= len(partidos):
        flash("El partido no existe.", "error")
        return redirect(url_for("index"))
    
    partido = partidos[partido_id]
    partido_obj_id = ObjectId(partido["_id"])
    
    try:
        apuesta_obj_id = ObjectId(apuesta_id)
        apuesta = apuestas_collection.find_one({
            "_id": apuesta_obj_id,
            "partido_id": partido_obj_id
        })
    except:
        apuesta = None
    
    if not apuesta:
        flash("La apuesta no existe.", "error")
        return redirect(url_for("index"))

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

        apuestas_collection.update_one(
            {"_id": apuesta_obj_id},
            {
                "$set": {
                    "nombre": nombre,
                    "dinero": dinero,
                    "marcador": marcador
                }
            }
        )
        flash("Apuesta modificada exitosamente.", "success")
        return redirect(url_for("index"))

    return render_template(
        "editar_apuesta.html",
        partido=partido,
        apuesta=apuesta,
        partido_id=partido_id,
        apuesta_id=apuesta_id
    )

@app.route("/borrar_apuesta/<int:partido_id>/<apuesta_id>", methods=["POST"])
def borrar_apuesta(partido_id, apuesta_id):
    try:
        partidos = obtener_partidos()
        
        if partido_id < 0 or partido_id >= len(partidos):
            flash("El partido no existe.", "error")
            return redirect(url_for("index"))
        
        partido = partidos[partido_id]
        partido_obj_id = ObjectId(partido["_id"])
        apuesta_obj_id = ObjectId(apuesta_id)
        
        apuesta = apuestas_collection.find_one({
            "_id": apuesta_obj_id,
            "partido_id": partido_obj_id
        })
        
        if not apuesta:
            flash("La apuesta no existe.", "error")
            return redirect(url_for("index"))
        
        apuestas_collection.delete_one({"_id": apuesta_obj_id})
        flash("Apuesta eliminada.", "success")
    except Exception as e:
        flash(f"Error al eliminar apuesta: {str(e)}", "error")
        app.logger.error(f"Error en borrar_apuesta: {str(e)}")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
