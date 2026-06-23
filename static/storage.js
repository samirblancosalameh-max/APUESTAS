// Almacenamiento local - maneja todo en el navegador
const StorageManager = {
    PARTIDOS_KEY: 'apuestas_partidos',
    APUESTAS_KEY: 'apuestas_data',

    // Cargar partidos desde localStorage
    getPartidos() {
        const data = localStorage.getItem(this.PARTIDOS_KEY);
        return data ? JSON.parse(data) : [];
    },

    // Guardar partidos a localStorage
    setPartidos(partidos) {
        localStorage.setItem(this.PARTIDOS_KEY, JSON.stringify(partidos));
    },

    // Cargar apuestas desde localStorage
    getApuestas() {
        const data = localStorage.getItem(this.APUESTAS_KEY);
        return data ? JSON.parse(data) : {};
    },

    // Guardar apuestas a localStorage
    setApuestas(apuestas) {
        localStorage.setItem(this.APUESTAS_KEY, JSON.stringify(apuestas));
    },

    // Agregar un nuevo partido
    agregarPartido(equipo1, equipo2, fecha, hora, lugar) {
        const partidos = this.getPartidos();
        partidos.push({ equipo1, equipo2, fecha, hora, lugar });
        this.setPartidos(partidos);
        const apuestas = this.getApuestas();
        apuestas[partidos.length - 1] = [];
        this.setApuestas(apuestas);
        return partidos.length - 1;
    },

    // Eliminar un partido
    eliminarPartido(id) {
        const partidos = this.getPartidos();
        if (id < 0 || id >= partidos.length) return false;
        
        partidos.splice(id, 1);
        this.setPartidos(partidos);
        
        const apuestas = this.getApuestas();
        const nuevasApuestas = {};
        
        for (let oldId in apuestas) {
            oldId = parseInt(oldId);
            if (oldId < id) {
                nuevasApuestas[oldId] = apuestas[oldId];
            } else if (oldId > id) {
                nuevasApuestas[oldId - 1] = apuestas[oldId];
            }
        }
        
        this.setApuestas(nuevasApuestas);
        return true;
    },

    // Agregar apuesta
    agregarApuesta(partidoId, nombre, dinero, marcador) {
        const apuestas = this.getApuestas();
        if (!(partidoId in apuestas)) {
            apuestas[partidoId] = [];
        }
        apuestas[partidoId].push({ nombre, dinero: parseInt(dinero), marcador });
        this.setApuestas(apuestas);
    },

    // Eliminar apuesta
    eliminarApuesta(partidoId, apuestaId) {
        const apuestas = this.getApuestas();
        if (!(partidoId in apuestas) || apuestaId < 0 || apuestaId >= apuestas[partidoId].length) {
            return false;
        }
        apuestas[partidoId].splice(apuestaId, 1);
        this.setApuestas(apuestas);
        return true;
    },

    // Editar apuesta
    editarApuesta(partidoId, apuestaId, nombre, dinero, marcador) {
        const apuestas = this.getApuestas();
        if (!(partidoId in apuestas) || apuestaId < 0 || apuestaId >= apuestas[partidoId].length) {
            return false;
        }
        apuestas[partidoId][apuestaId] = { nombre, dinero: parseInt(dinero), marcador };
        this.setApuestas(apuestas);
        return true;
    }
};
