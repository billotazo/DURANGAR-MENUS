import streamlit as st
import pandas as pd
import random
from io import BytesIO
import datetime

# ─── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Generador de Menús — NETO DURANGAR S.A.S.",
    page_icon="🍽️",
    layout="wide"
)

# ─── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .titulo-principal {
        background: linear-gradient(90deg, #1F3864, #2E75B6);
        color: white; padding: 20px; border-radius: 10px;
        text-align: center; margin-bottom: 20px;
    }
    .card-dia {
        background: #f8f9fa; border-left: 5px solid #2E75B6;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .servicio-header {
        font-weight: bold; color: #1F3864; font-size: 16px;
    }
    .prep-item { color: #333; margin: 4px 0; padding-left: 15px; }
    .badge-des  { background:#E2EFDA; color:#375623; padding:3px 10px; border-radius:12px; font-size:13px; }
    .badge-alm  { background:#DEEAF1; color:#1F3864; padding:3px 10px; border-radius:12px; font-size:13px; }
    .badge-cena { background:#FCE4D6; color:#C55A11; padding:3px 10px; border-radius:12px; font-size:13px; }
    .metric-box {
        background: white; border: 1px solid #e0e0e0;
        border-radius: 8px; padding: 15px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ─── TÍTULO ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="titulo-principal">
    <h2 style="margin:0">🍽️ Generador de Menús Aleatorios</h2>
    <p style="margin:5px 0 0 0; opacity:0.9">NETO DURANGAR S.A.S. | Frontera Energy | Minuta Contractual</p>
</div>
""", unsafe_allow_html=True)

# ─── CARGAR DATOS ─────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    # Desayuno
    df_des = pd.read_excel("Desayuno_Final_02.xlsx", header=0)
    df_des.columns = ['_','COMIDA','DESCRIPCION','PREPARACION',
                      'INGREDIENTE','g_persona','num_personas',
                      'total_dia','total_mes']
    df_des = df_des.iloc[1:].dropna(subset=['PREPARACION','INGREDIENTE'])
    df_des['g_persona'] = pd.to_numeric(df_des['g_persona'], errors='coerce')
    df_des['COMIDA'] = 'Desayuno'

    # Almuerzo/Cena
    df_alm = pd.read_excel("Alm-Cena_02.xlsx", header=0)
    df_alm.columns = ['_','DESCRIPCION','PREPARACION','INGREDIENTE',
                      'g_persona','num_personas','total_dia','total_mes']
    df_alm = df_alm.iloc[1:].dropna(subset=['PREPARACION','INGREDIENTE'])
    df_alm['g_persona'] = pd.to_numeric(df_alm['g_persona'], errors='coerce')

    return df_des, df_alm

df_des, df_alm = cargar_datos()

# ─── PARÁMETROS EN SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/restaurant.png", width=80)
    st.markdown("### ⚙️ Parámetros")

    num_semanas = st.slider("Semanas del ciclo", 1, 4, 4)
    num_personas = st.number_input("Personas por servicio", 100, 1000, 690, step=10)
    margen = st.slider("Margen de seguridad (%)", 0, 20, 10)

    st.markdown("---")
    st.markdown("### 📋 Restricciones Minuta")
    incluir_especiales = st.checkbox("Incluir especiales semanales", value=True)
    rotar_jugos = st.checkbox("Rotar jugos (sin repetir)", value=True)

    st.markdown("---")
    st.markdown("### ℹ️ Base de datos")
    st.info(f"**Desayuno:** {df_des['PREPARACION'].nunique()} preparaciones")
    st.info(f"**Almuerzo/Cena:** {df_alm['PREPARACION'].nunique()} preparaciones")

# ─── FUNCIÓN GENERADORA ───────────────────────────────────────────────────────
dias = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']

CATS_DESAYUNO = [
    'Jugos', 'Bebida Caliente ', 'Lácteos', 'Fruta',
    'Cereales', 'Queso', 'Huevos ', 'Proteina 1',
    'Proteina 2', 'Caldo', 'Arroz Cocido', 'Pan Varios'
]
CATS_ALMUERZO = [
    'Jugos', 'Frutas de Mano', 'Sopa, Crema o Consomé',
    'Proteico 1 - Carne Roja', 'Proteico 2 - Carne Blanca',
    'Verduras Cocidas', 'Arroz', 'Energético',
    'Barra de Ensalada', 'Leguminosa', 'Postre'
]

def elegir_prep(df, descripcion, excluir=None):
    """Elige una preparacion aleatoria de una categoria."""
    opciones = df[df['DESCRIPCION'] == descripcion]['PREPARACION'].unique().tolist()
    if excluir:
        opciones = [x for x in opciones if x not in excluir]
    if not opciones:
        opciones = df[df['DESCRIPCION'] == descripcion]['PREPARACION'].unique().tolist()
    return random.choice(opciones) if opciones else "N/A"

def generar_menu_completo(semanas, personas, rotar):
    """Genera el menú completo para N semanas."""
    menu = {}
    jugos_usados_des = []
    jugos_usados_alm = []

    for s in range(1, semanas + 1):
        menu[f'Semana {s}'] = {}
        for dia in dias:
            menu[f'Semana {s}'][dia] = {}

            # ── DESAYUNO ──
            jugo_d = elegir_prep(df_des, 'Jugos',
                                  jugos_usados_des if rotar else None)
            if rotar:
                jugos_usados_des.append(jugo_d)
                if len(jugos_usados_des) > 10:
                    jugos_usados_des.pop(0)

            menu[f'Semana {s}'][dia]['Desayuno'] = {
                'Jugos':          jugo_d,
                'Bebida Caliente':elegir_prep(df_des, 'Bebida Caliente '),
                'Lácteo':         elegir_prep(df_des, 'Lácteos'),
                'Fruta':          elegir_prep(df_des, 'Fruta'),
                'Cereal':         elegir_prep(df_des, 'Cereales'),
                'Queso':          elegir_prep(df_des, 'Queso'),
                'Huevo':          elegir_prep(df_des, 'Huevos '),
                'Proteína 1':     elegir_prep(df_des, 'Proteina 1'),
                'Proteína 2':     elegir_prep(df_des, 'Proteina 2'),
                'Caldo':          elegir_prep(df_des, 'Caldo'),
                'Arroz':          elegir_prep(df_des, 'Arroz Cocido'),
                'Pan':            elegir_prep(df_des, 'Pan Varios'),
            }

            # ── ALMUERZO ──
            jugo_a = elegir_prep(df_alm, 'Jugos',
                                  jugos_usados_alm if rotar else None)
            if rotar:
                jugos_usados_alm.append(jugo_a)
                if len(jugos_usados_alm) > 10:
                    jugos_usados_alm.pop(0)

            # Especial 1x semana: viernes = pescado/marisco
            if dia == 'Viernes' and incluir_especiales:
                prot1 = elegir_prep(df_alm, 'Especial - 1x Semana (Pescados y Mariscos)')
                prot2 = elegir_prep(df_alm, 'Proteico 2 - Carne Blanca')
            else:
                prot1 = elegir_prep(df_alm, 'Proteico 1 - Carne Roja')
                prot2 = elegir_prep(df_alm, 'Proteico 2 - Carne Blanca')

            menu[f'Semana {s}'][dia]['Almuerzo'] = {
                'Jugo':           jugo_a,
                'Fruta de mano':  elegir_prep(df_alm, 'Frutas de Mano'),
                'Sopa/Crema':     elegir_prep(df_alm, 'Sopa, Crema o Consomé'),
                'Proteína 1':     prot1,
                'Proteína 2':     prot2,
                'Verduras':       elegir_prep(df_alm, 'Verduras Cocidas'),
                'Arroz':          elegir_prep(df_alm, 'Arroz'),
                'Energético':     elegir_prep(df_alm, 'Energético'),
                'Ensalada':       elegir_prep(df_alm, 'Barra de Ensalada'),
                'Leguminosa':     elegir_prep(df_alm, 'Leguminosa'),
                'Postre':         elegir_prep(df_alm, 'Postre'),
            }

            # ── CENA (misma estructura que almuerzo pero diferentes preparaciones) ──
            menu[f'Semana {s}'][dia]['Cena'] = {
                'Jugo':           elegir_prep(df_alm, 'Jugos',
                                              [jugo_a] if rotar else None),
                'Fruta de mano':  elegir_prep(df_alm, 'Frutas de Mano'),
                'Sopa/Crema':     elegir_prep(df_alm, 'Sopa, Crema o Consomé'),
                'Proteína 1':     elegir_prep(df_alm, 'Proteico 1 - Carne Roja'),
                'Proteína 2':     elegir_prep(df_alm, 'Proteico 2 - Carne Blanca'),
                'Verduras':       elegir_prep(df_alm, 'Verduras Cocidas'),
                'Arroz':          elegir_prep(df_alm, 'Arroz'),
                'Energético':     elegir_prep(df_alm, 'Energético'),
                'Ensalada':       elegir_prep(df_alm, 'Barra de Ensalada'),
                'Leguminosa':     elegir_prep(df_alm, 'Leguminosa'),
                'Postre':         elegir_prep(df_alm, 'Postre'),
            }

    return menu

# ─── FUNCIÓN EXPORTAR EXCEL ───────────────────────────────────────────────────
def exportar_excel(menu, personas, margen_pct):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for semana, dias_menu in menu.items():
            filas = []
            for dia, servicios in dias_menu.items():
                for servicio, preps in servicios.items():
                    for componente, preparacion in preps.items():
                        # Obtener ingredientes
                        if servicio == 'Desayuno':
                            ing = df_des[df_des['PREPARACION'] == preparacion][
                                ['INGREDIENTE','g_persona']].drop_duplicates()
                        else:
                            ing = df_alm[df_alm['PREPARACION'] == preparacion][
                                ['INGREDIENTE','g_persona']].drop_duplicates()

                        if len(ing) == 0:
                            filas.append({
                                'DIA': dia, 'SERVICIO': servicio,
                                'COMPONENTE': componente,
                                'PREPARACION': preparacion,
                                'INGREDIENTE': '',
                                'g/persona': 0,
                                '# PERSONAS': personas,
                                'TOTAL Kg (base)': 0,
                                f'TOTAL Kg (+{margen_pct}%)': 0
                            })
                        else:
                            for _, row in ing.iterrows():
                                g = float(row['g_persona']) if pd.notna(row['g_persona']) else 0
                                total_base = round(g * personas / 1000, 3)
                                total_margen = round(total_base * (1 + margen_pct/100), 3)
                                filas.append({
                                    'DIA': dia, 'SERVICIO': servicio,
                                    'COMPONENTE': componente,
                                    'PREPARACION': preparacion,
                                    'INGREDIENTE': row['INGREDIENTE'],
                                    'g/persona': g,
                                    '# PERSONAS': personas,
                                    'TOTAL Kg (base)': total_base,
                                    f'TOTAL Kg (+{margen_pct}%)': total_margen
                                })

            df_out = pd.DataFrame(filas)
            nombre_hoja = semana.replace(' ', '_')[:31]
            df_out.to_excel(writer, sheet_name=nombre_hoja, index=False)

    output.seek(0)
    return output

# ─── INTERFAZ PRINCIPAL ───────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1,2,1])
with col2:
    generar = st.button(
        "🎲 GENERAR MENÚ ALEATORIO",
        type="primary",
        use_container_width=True
    )

if generar or 'menu_generado' in st.session_state:

    if generar:
        with st.spinner("Generando menú..."):
            st.session_state['menu_generado'] = generar_menu_completo(
                num_semanas, num_personas, rotar_jugos)
            st.session_state['params'] = {
                'personas': num_personas,
                'margen': margen,
                'semanas': num_semanas
            }

    menu = st.session_state['menu_generado']
    params = st.session_state['params']

    # ── Métricas resumen ──
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Semanas", params['semanas'])
    with c2:
        st.metric("Personas/servicio", params['personas'])
    with c3:
        st.metric("Días generados", params['semanas'] * 7)
    with c4:
        st.metric("Servicios totales", params['semanas'] * 7 * 3)

    st.markdown("---")

    # ── Ver menú por semana ──
    semanas_lista = list(menu.keys())
    semana_sel = st.selectbox("Ver semana:", semanas_lista)

    # ── Mostrar el menú ──
    dias_menu = menu[semana_sel]

    for dia, servicios in dias_menu.items():
        with st.expander(f"📅 {dia}", expanded=(dia == 'Lunes')):
            col_d, col_a, col_c = st.columns(3)

            with col_d:
                st.markdown('<span class="badge-des">🌅 Desayuno</span>',
                            unsafe_allow_html=True)
                for comp, prep in servicios['Desayuno'].items():
                    st.markdown(f"**{comp}:** {prep}")

            with col_a:
                st.markdown('<span class="badge-alm">☀️ Almuerzo</span>',
                            unsafe_allow_html=True)
                for comp, prep in servicios['Almuerzo'].items():
                    st.markdown(f"**{comp}:** {prep}")

            with col_c:
                st.markdown('<span class="badge-cena">🌙 Cena</span>',
                            unsafe_allow_html=True)
                for comp, prep in servicios['Cena'].items():
                    st.markdown(f"**{comp}:** {prep}")

    # ── Botones de descarga ──
    st.markdown("---")
    st.markdown("### 📥 Descargar resultados")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        excel_data = exportar_excel(
            menu, params['personas'], params['margen'])
        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📊 Descargar Excel completo",
            data=excel_data,
            file_name=f"Menu_NETO_DURANGAR_{fecha}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_e2:
        # Resumen en texto plano
        resumen = []
        for sem, dias_s in menu.items():
            resumen.append(f"\n{'='*50}")
            resumen.append(f"  {sem.upper()}")
            resumen.append(f"{'='*50}")
            for dia, servicios in dias_s.items():
                resumen.append(f"\n{dia}:")
                for servicio, preps in servicios.items():
                    resumen.append(f"  {servicio}:")
                    for comp, prep in preps.items():
                        resumen.append(f"    - {comp}: {prep}")

        texto = '\n'.join(resumen)
        st.download_button(
            label="📄 Descargar resumen texto",
            data=texto.encode('utf-8'),
            file_name=f"Menu_Resumen_{fecha}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_e3:
        if st.button("🔄 Regenerar menú",
                     use_container_width=True):
            st.session_state['menu_generado'] = generar_menu_completo(
                num_semanas, num_personas, rotar_jugos)
            st.rerun()

else:
    # Pantalla de bienvenida
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🎲 Aleatorio**\nCada clic genera un menú diferente respetando la Minuta Contractual")
    with col2:
        st.info("**📋 Completo**\nDesayuno, Almuerzo y Cena para todas las semanas del ciclo")
    with col3:
        st.info("**📥 Exportable**\nDescarga el menú en Excel con ingredientes y cantidades")

    st.markdown("""
    <div style='text-align:center; padding:40px; color:#888'>
        <h3>Configura los parámetros en el panel izquierdo</h3>
        <p>y haz clic en <strong>GENERAR MENÚ ALEATORIO</strong></p>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888; font-size:12px'>"
    "NETO DURANGAR S.A.S. | Sistema MRP — Específico 2 | "
    f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>",
    unsafe_allow_html=True
)
