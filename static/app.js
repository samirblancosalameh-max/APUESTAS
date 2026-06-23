// Apuestas App - localStorage management
const ApuestasApp = {
    PARTIDOS_KEY: 'apuestas_partidos',
    APUESTAS_KEY: 'apuestas_apuestas',

    init() {
        this.loadFromStorage();
        this.renderPage();
    },

    loadFromStorage() {
        const partidosJSON = localStorage.getItem(this.PARTIDOS_KEY);
        const apuestasJSON = localStorage.getItem(this.APUESTAS_KEY);
        
        window.partidos = partidosJSON ? JSON.parse(partidosJSON) : [];
        window.apuestas_por_partido = apuestasJSON ? JSON.parse(apuestasJSON) : {};
    },

    saveToStorage() {
        localStorage.setItem(this.PARTIDOS_KEY, JSON.stringify(window.partidos));
        localStorage.setItem(this.APUESTAS_KEY, JSON.stringify(window.apuestas_por_partido));
    },

    agregarPartido(equipo1, equipo2, fecha, hora, lugar) {
        const partido = { equipo1, equipo2, fecha, hora, lugar };
        window.partidos.push(partido);
        const id = window.partidos.length - 1;
        window.apuestas_por_partido[id] = [];
        this.saveToStorage();
        return id;
    },

    eliminarPartido(partido_id) {
        if (partido_id < 0 || partido_id >= window.partidos.length) return false;
        
        window.partidos.splice(partido_id, 1);
        
        // Reorganizar apuestas
        const nuevasApuestas = {};
        for (let old_id in window.apuestas_por_partido) {
            old_id = parseInt(old_id);
            if (old_id < partido_id) {
                nuevasApuestas[old_id] = window.apuestas_por_partido[old_id];
            } else if (old_id > partido_id) {
                nuevasApuestas[old_id - 1] = window.apuestas_por_partido[old_id];
            }
        }
        window.apuestas_por_partido = nuevasApuestas;
        this.saveToStorage();
        return true;
    },

    agregarApuesta(partido_id, nombre, dinero, marcador) {
        if (!(partido_id in window.apuestas_por_partido)) return false;
        
        window.apuestas_por_partido[partido_id].push({
            nombre,
            dinero: parseInt(dinero),
            marcador
        });
        this.saveToStorage();
        return true;
    },

    eliminarApuesta(partido_id, apuesta_id) {
        if (!(partido_id in window.apuestas_por_partido) || 
            apuesta_id < 0 || 
            apuesta_id >= window.apuestas_por_partido[partido_id].length) {
            return false;
        }
        
        window.apuestas_por_partido[partido_id].splice(apuesta_id, 1);
        this.saveToStorage();
        return true;
    },

    editarApuesta(partido_id, apuesta_id, nombre, dinero, marcador) {
        if (!(partido_id in window.apuestas_por_partido) || 
            apuesta_id < 0 || 
            apuesta_id >= window.apuestas_por_partido[partido_id].length) {
            return false;
        }
        
        window.apuestas_por_partido[partido_id][apuesta_id] = {
            nombre,
            dinero: parseInt(dinero),
            marcador
        };
        this.saveToStorage();
        return true;
    },

    renderPage() {
        // This will be overridden by specific page logic
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ApuestasApp.init();
});
