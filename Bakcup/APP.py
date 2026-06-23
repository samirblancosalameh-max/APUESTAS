from flask import Flask, render_template, request, redirect

app = Flask(__name__)

partidos = []
apuestas_por_partido = {}

@app.route("/")
def index():
    # Calcular resumen general
    total_apostadores = sum(len(apuestas) for apuestas in apuestas_por_partido.values())
    total_dinero = sum(sum(a["dinero"] for a in apuestas) for apuestas in apuestas_por_partido.values())
    return render_template("index.html",
                           partidos=partidos,
                           apuestas_por_partido=apuestas_por_partido,
                           total_apostadores=total_apostadores,
                           total_dinero=total_dinero)

@app.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    if request.method == "POST":
        equipo1 = request.form["equipo1"]
        equipo2 = request.form["equipo2"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        lugar = request.form["lugar"]
        partido = {
            "equipo1": equipo1,
            "equipo2": equipo2,
            "fecha": fecha,
            "hora": hora,
            "lugar": lugar
        }
        partidos.append(partido)
        apuestas_por_partido[len(partidos)-1] = []
        return redirect("/")
    return render_template("ingresar.html")

@app.route("/apostar/<int:partido_id>", methods=["GET", "POST"])
def apostar(partido_id):
    if request.method == "POST":
        nombre = request.form["nombre"]
        marcador1 = request.form["marcador1"]
        marcador2 = request.form["marcador2"]
        dinero = int(request.form["dinero"])
        apuesta = {
            "nombre": nombre,
            "marcador": f"{marcador1} - {marcador2}",
            "dinero": dinero
        }
        apuestas_por_partido[partido_id].append(apuesta)
        return redirect("/")
    return render_template("apostar.html", partido=partidos[partido_id])

@app.route("/borrar_partido/<int:partido_id>", methods=["POST"])
def borrar_partido(partido_id):
    clave = request.form.get("clave")
    if clave == "1102":
        if 0 <= partido_id < len(partidos):
            partidos.pop(partido_id)
            apuestas_por_partido.pop(partido_id, None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
