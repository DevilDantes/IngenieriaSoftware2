import streamlit as st

# ==========================================
# PATRONES DE DISEÑO (Lógica Intacta)
# ==========================================
class ConfiguracionJuego: # Singleton [cite: 73, 74]
    _instancia = None
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConfiguracionJuego, cls).__new__(cls)
            cls._instancia.dificultad = "Normal"
        return cls._instancia

class EstrategiaAtaque: # Strategy 
    def ejecutar_ataque(self) -> tuple: pass

class AtaqueEspada(EstrategiaAtaque):
    def ejecutar_ataque(self): return ("Ataque Físico", 15, "🗡️ Dajo con espada!")

class AtaqueMagico(EstrategiaAtaque):
    def ejecutar_ataque(self): return ("Ataque Mágico", 20, "🔮 ¡Hechizo lanzado!")

class AtaqueDistancia(EstrategiaAtaque):
    def ejecutar_ataque(self): return ("Ataque a Distancia", 10, "🏹 ¡Flecha certera!")

class Personaje:
    def __init__(self, nombre, estrategia: EstrategiaAtaque, emoji: str):
        self.nombre = nombre
        self.estrategia = estrategia
        self.vida = 100
        self.emoji = emoji

    def atacar(self):
        tipo, daño, mensaje = self.estrategia.ejecutar_ataque()
        return f"{self.nombre} usó {tipo} causando {daño} de daño. {mensaje}"

class FabricaPersonaje: # Factory Method [cite: 168, 169]
    @staticmethod
    def crear_personaje(tipo: str, nombre: str):
        if tipo == "Guerrero": return Personaje(nombre, AtaqueEspada(), "🛡️")
        elif tipo == "Mago": return Personaje(nombre, AtaqueMagico(), "🧙‍♂️")
        elif tipo == "Arquero": return Personaje(nombre, AtaqueDistancia(), "🧝‍♂️")

class EventoJuego: # Observer [cite: 102, 103]
    def __init__(self): self._observadores = []
    def registrar_observador(self, observador): self._observadores.append(observador)
    def notificar(self, evento: str):
        for obs in self._observadores: obs.actualizar(evento)

class RegistroJuego:
    def actualizar(self, evento: str): st.session_state.historial.insert(0, evento)

# ==========================================
# INTERFAZ GRÁFICA MEJORADA (El "Diseño Guapo")
# ==========================================
st.set_page_config(page_title="Battle Arena TCG", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS para crear el estilo de "Cartas"
st.markdown("""
<style>
    .carta-container {
        background-color: #1e1e1e;
        border: 2px solid #FFD700;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(255, 215, 0, 0.2);
        transition: 0.3s;
    }
    .carta-container:hover {
        box-shadow: 0 12px 20px rgba(255, 215, 0, 0.5);
        transform: translateY(-5px);
    }
    .carta-titulo { color: #FFD700; font-size: 24px; font-weight: bold; margin-bottom: 0;}
    .carta-emoji { font-size: 80px; margin: 10px 0; }
    .log-batalla { background-color: #0e1117; padding: 15px; border-left: 4px solid #FF4B4B; border-radius: 5px; margin-bottom: 10px; font-family: monospace;}
</style>
""", unsafe_allow_html=True)

# Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'motor' not in st.session_state:
    st.session_state.motor = EventoJuego()
    st.session_state.motor.registrar_observador(RegistroJuego())

config = ConfiguracionJuego()

# BARRA LATERAL (Creación y Configuración)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3592/3592882.png", width=100) # Un logo genérico de espadas
    st.title("Forja tu Héroe")
    tipo_pj = st.selectbox("Clase:", ["Guerrero", "Mago", "Arquero"])
    nombre_pj = st.text_input("Nombre:", "Arthas")
    
    st.divider()
    st.write("⚙️ Configuración Global")
    config.dificultad = st.select_slider("Dificultad", options=["Fácil", "Normal", "Pesadilla"])

jugador = FabricaPersonaje.crear_personaje(tipo_pj, nombre_pj)

# ÁREA PRINCIPAL
st.title("⚔️ BATTLE ARENA: El Duelo")
st.write("---")

# Layout de la Arena en 3 Columnas
col_jugador, col_vs, col_registro = st.columns([1, 0.2, 1.5])

# COLUMNA 1: Carta del Jugador
with col_jugador:
    st.markdown(f"""
    <div class="carta-container">
        <div class="carta-titulo">{jugador.nombre}</div>
        <div style="color: gray; font-size: 14px;">Clase: {tipo_pj}</div>
        <div class="carta-emoji">{jugador.emoji}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Espacio
    st.progress(jugador.vida / 100, text=f"❤️ Vida: {jugador.vida}/100")
    
    # Botones de Acción (Estrategias)
    st.write("### Jugar Carta de Acción:")
    b1, b2, b3 = st.columns(3)
    if b1.button("🗡️ Tajo", use_container_width=True):
        jugador.estrategia = AtaqueEspada()
        st.session_state.motor.notificar(jugador.atacar())
    if b2.button("🔮 Fuego", use_container_width=True):
        jugador.estrategia = AtaqueMagico()
        st.session_state.motor.notificar(jugador.atacar())
    if b3.button("🏹 Disparo", use_container_width=True):
        jugador.estrategia = AtaqueDistancia()
        st.session_state.motor.notificar(jugador.atacar())

# COLUMNA 2: Separador VS
with col_vs:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-top: 50px;'>VS</h1>", unsafe_allow_html=True)

# COLUMNA 3: Historial de Batalla Animado
with col_registro:
    st.subheader("📜 Registro de Batalla")
    if not st.session_state.historial:
        st.info("La arena está en silencio... ¡Ataca para comenzar!")
    else:
        # Mostrar solo los últimos 5 eventos para no saturar la pantalla
        for accion in st.session_state.historial[:5]:
            st.markdown(f"<div class='log-batalla'> {accion} </div>", unsafe_allow_html=True)
