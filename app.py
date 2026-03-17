import streamlit as st
import random
import time

class ConfiguracionJuego:
    _instancia = None
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConfiguracionJuego, cls).__new__(cls)
            cls._instancia.dificultad = "Normal"
            cls._instancia.volumen_musica = 80
            cls._instancia.idioma = "Español"
            cls._instancia.pantalla_completa = True
        return cls._instancia

class EventoJuego:
    def __init__(self):
        self.observadores = []
    def registrar(self, obs):
        self.observadores.append(obs)
    def notificar(self, evento):
        for obs in self.observadores:
            obs.actualizar(evento)

class RegistroJuego:
    def actualizar(self, evento):
        st.session_state.log.insert(0, evento)

def generar_mazo_maestro(clase):
    mazo = []
    config = {
        "Mago": {"iconos": ["🔥", "❄️", "⚡", "🔮", "☄️"], "prefix": ["Nova", "Rayo", "Sello"], "suffix": ["Arcano", "Gélido", "Ígneo"]},
        "Guerrero": {"iconos": ["🗡️", "🪓", "🛡️", "⚔️", "💥"], "prefix": ["Corte", "Golpe", "Escudo"], "suffix": ["Brutal", "Puro", "Pesado"]},
        "Arquero": {"iconos": ["🏹", "🎯", "🍃", "🦅", "💣"], "prefix": ["Flecha", "Velo", "Disparo"], "suffix": ["Veloz", "Letal", "Tóxico"]}
    }
    c = config[clase]
    for i in range(40):
        nombre = f"{random.choice(c['prefix'])} {random.choice(c['suffix'])} {i+1}"
        icono = random.choice(c['iconos'])
        tipo = random.choice(["ataque", "defensa", "curacion"])
        
        if tipo == "ataque":
            fx = {"dmg": random.randint(18, 35), "def": 0, "heal": 0, "anim": "ataque"}
        elif tipo == "defensa":
            fx = {"dmg": 0, "def": random.randint(20, 40), "heal": 0, "anim": "cura"}
        else:
            fx = {"dmg": 0, "def": 0, "heal": random.randint(15, 25), "anim": "cura"}
            
        mazo.append({"nombre": nombre, "icono": icono, "fx": fx})
    return mazo

class Personaje:
    def __init__(self, nombre, clase, emoji):
        self.nombre = nombre
        self.clase = clase
        self.emoji = emoji
        self.vida = 100
        self.armadura = 0
        self.mazo_total = generar_mazo_maestro(clase)
        self.mano = random.sample(self.mazo_total, 3)

    def recibir_danio(self, cantidad):
        if self.armadura > 0:
            absorbido = min(self.armadura, cantidad)
            self.armadura -= absorbido
            cantidad -= absorbido
            return "break-armor" if cantidad <= 0 else "shake-red"
        self.vida = max(0, self.vida - cantidad)
        return "shake-red"

    def jugar_turno(self, carta, objetivo):
        fx = carta["fx"]
        # Aplicar efectos
        if fx["dmg"] > 0: objetivo.recibir_danio(fx["dmg"])
        if fx["def"] > 0: self.armadura += fx["def"]
        if fx["heal"] > 0: self.vida = min(100, self.vida + fx["heal"])
        
        # Lógica de Gasto y Robo
        self.mano.remove(carta)
        self.mano.append(random.choice(self.mazo_total))
        return f"{self.icono_clase()} {self.nombre} usó {carta['nombre']} {carta['icono']}"

    def icono_clase(self): return self.emoji

st.set_page_config(layout="wide", page_title="Battle Arena PRO")

st.markdown("""
<style>
    /* Animaciones de Movimiento */
    @keyframes jump-right { 0% { transform: translateX(0); } 50% { transform: translateX(100px) scale(1.2); } 100% { transform: translateX(0); } }
    @keyframes jump-left { 0% { transform: translateX(0); } 50% { transform: translateX(-100px) scale(1.2); } 100% { transform: translateX(0); } }
    
    /* Animaciones de Recibir Daño */
    @keyframes shake-red { 0%, 100% { transform: translateX(0); background: rgba(255,0,0,0); } 25% { transform: translateX(-10px); background: rgba(255,0,0,0.4); } 75% { transform: translateX(10px); } }
    @keyframes break-blue { 0% { transform: scale(1); } 50% { transform: scale(1.1); box-shadow: 0 0 30px #0af; } 100% { transform: scale(1); } }

    .anim-ataque-jugador { animation: jump-left 0.5s ease-in-out; }
    .anim-ataque-enemigo { animation: jump-right 0.5s ease-in-out; }
    .anim-shake-red { animation: shake-red 0.4s ease-in-out; border: 3px solid red !important; }
    .anim-break-armor { animation: break-blue 0.4s ease-in-out; border: 3px solid #0af !important; }

    .pj-card {
        background: #1e1e1e; border: 2px solid #444; border-radius: 20px;
        padding: 20px; text-align: center; transition: 0.3s;
    }
    .stat-bar { font-weight: bold; font-size: 20px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- ESTADO GLOBAL ---
if 'pantalla' not in st.session_state: st.session_state.pantalla = 'titulo'
if 'log' not in st.session_state: st.session_state.log = []
if 'victorias' not in st.session_state: st.session_state.victorias = 0
if 'anim_jugador' not in st.session_state: st.session_state.anim_jugador = ""
if 'anim_enemigo' not in st.session_state: st.session_state.anim_enemigo = ""
if 'icono_central' not in st.session_state: st.session_state.icono_central = "VS"

if 'motor_eventos' not in st.session_state:
    st.session_state.motor_eventos = EventoJuego()
    st.session_state.motor_eventos.registrar(RegistroJuego())

if st.session_state.pantalla == 'titulo':
    st.markdown("<h1 style='text-align:center; font-size: 80px; margin-top: 50px;'>⚔️ BATTLE ARENA</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🎮 NUEVA PARTIDA", use_container_width=True): 
            st.session_state.pantalla = 'seleccion'
            st.rerun()
        if st.button("⚙️ CONFIGURACIÓN", use_container_width=True): 
            st.session_state.pantalla = 'config'
            st.rerun()
        if st.button("❌ SALIR AL ESCRITORIO", use_container_width=True): st.stop()

elif st.session_state.pantalla == 'config':
    st.title("⚙️ AJUSTES DEL SISTEMA")
    conf = ConfiguracionJuego()
    with st.container(border=True):
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Video")
            st.selectbox("Resolución", ["1920x1080", "1280x720"], index=0)
            st.toggle("Sincronización Vertical", True)
        with col_b:
            st.subheader("Audio")
            conf.volumen_musica = st.slider("Música", 0, 100, conf.volumen_musica)
            st.slider("Efectos (SFX)", 0, 100, 100)
    if st.button("APLICAR CAMBIOS"): 
        st.session_state.pantalla = 'titulo'
        st.rerun()

elif st.session_state.pantalla == 'seleccion':
    st.title("Elige tu Héroe")
    c1, c2, c3 = st.columns(3)
    clases = [("Mago", "🧙‍♂️"), ("Guerrero", "🛡️"), ("Arquero", "🧝")]
    for i, (tipo, ico) in enumerate(clases):
        with [c1, c2, c3][i]:
            st.markdown(f"<h1 style='text-align:center;'>{ico}</h1>", unsafe_allow_html=True)
            if st.button(f"Clase: {tipo}", use_container_width=True):
                st.session_state.jugador = Personaje("Héroe", tipo, ico)
                st.session_state.enemigo = Personaje("Enemigo", "Guerrero", "👹")
                st.session_state.pantalla = 'batalla'
                st.rerun()

elif st.session_state.pantalla == 'batalla':
    j, e = st.session_state.jugador, st.session_state.enemigo

    if e.vida <= 0:
        st.success(f"¡HAS VENCIDO! Victoria #{st.session_state.victorias + 1}")
        if st.button("➡️ PRÓXIMO COMBATE"):
            st.session_state.victorias += 1
            j.vida = min(100, j.vida + 30) 
            st.session_state.enemigo = Personaje(f"Rival {st.session_state.victorias+1}", random.choice(["Mago", "Guerrero", "Arquero"]), random.choice(["💀", "🐉", "🧛", "👿"]))
            st.rerun()
        st.stop()
    
    if j.vida <= 0:
        st.error(f"HAS SIDO DERROTADO. Récord: {st.session_state.victorias} victorias.")
        if st.button("VOLVER AL MENÚ"): 
            st.session_state.pantalla = 'titulo'
            st.rerun()
        st.stop()

    col_e, col_c, col_j = st.columns([1, 0.8, 1])

    with col_e:
        st.markdown(f"""<div class='pj-card {st.session_state.anim_enemigo}'>
            <h2>{e.emoji} {e.nombre}</h2>
            <div class='stat-bar' style='color:#ff4b4b;'>❤️ HP: {e.vida}</div>
            <div class='stat-box' style='color:#0af;'>🛡️ DEF: {e.armadura}</div>
        </div>""", unsafe_allow_html=True)

    with col_c:
        st.markdown(f"<h1 style='text-align:center; font-size: 100px;'>{st.session_state.icono_central}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>Racha: {st.session_state.victorias}</h3>", unsafe_allow_html=True)

    with col_j:
        st.markdown(f"""<div class='pj-card {st.session_state.anim_jugador}'>
            <h2>{j.emoji} {j.nombre}</h2>
            <div class='stat-bar' style='color:#ff4b4b;'>❤️ HP: {j.vida}</div>
            <div class='stat-box' style='color:#0af;'>🛡️ DEF: {j.armadura}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    st.subheader("🃏 Tus Cartas")
    cols_mano = st.columns(3)
    for idx, carta in enumerate(j.mano):
        with cols_mano[idx]:
            if st.button(f"{carta['icono']} {carta['nombre']}\n\n(Dmg:{carta['fx']['dmg']} | Def:{carta['fx']['def']})", key=f"c_{idx}", use_container_width=True):
                res_e = e.recibir_danio(carta['fx']['dmg'])
                msg_j = j.jugar_turno(carta, e)
                st.session_state.motor_eventos.notificar(msg_j)
                
                st.session_state.anim_jugador = "anim-ataque-jugador"
                st.session_state.anim_enemigo = f"anim-{res_e}"
                st.session_state.icono_central = carta['icono']
                
                time.sleep(0.5)
                carta_ia = random.choice(e.mano)
                res_j = j.recibir_danio(carta_ia['fx']['dmg'])
                msg_e = e.jugar_turno(carta_ia, j)
                st.session_state.motor_eventos.notificar(msg_e)
                
                st.session_state.anim_enemigo = "anim-ataque-enemigo"
                st.session_state.anim_jugador = f"anim-{res_j}"
                
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_rendir, _ = st.columns([1, 0.4, 1])
    with col_rendir:
        if st.button("🏳️ Rendirse", use_container_width=True, help="Abandonar el combate actual"):
            st.session_state.motor_eventos.notificar(f"🚩 {j.nombre} se ha retirado del combate.")
            j.vida = 0 
            st.rerun()

    st.session_state.anim_jugador = ""
    st.session_state.anim_enemigo = ""

    with st.expander("📜 Registro de Combate", expanded=True):
        for line in st.session_state.log[:5]:
            st.write(line)
