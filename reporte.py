import streamlit as st
import pandas as pd
import glob
import urllib.parse
import altair as alt
import pydeck as pdk

st.set_page_config(page_title="Tienda La Guajira | Dashboard", page_icon="🧶", layout="wide")

# CSS PROFESIONAL
st.markdown("""
<style>
.metric-card {background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:5px solid #FF5733;}
.wayuu-header {background: linear-gradient(90deg, #FFC300 0%, #C70039 50%, #581845 100%); padding:20px; border-radius:12px; color:white;}
</style>
""", unsafe_allow_html=True)

NUMERO_BETZY = "573003508492"

# HEADER PROFESIONAL
st.markdown('<div class="wayuu-header"><h1 style="margin:0; color:white;">🧶 Tienda La Guajira</h1><p style="margin:0; color:white; opacity:0.9;">Dashboard de Ventas - Artesanías Wayuu | Riohacha, La Guajira</p></div>', unsafe_allow_html=True)
st.write("")

# CARGAR EXCEL
archivo = glob.glob("*.xlsx")[0]
df_raw = pd.read_excel(archivo, header=None)
fila_header = 0
for i in range(20):
    texto = " ".join(str(x) for x in df_raw.iloc[i].tolist() if str(x) != 'nan')
    if "Fecha" in texto or "Producto" in texto:
        fila_header = i
        break
df_raw.columns = df_raw.iloc[fila_header]
df = df_raw.iloc[fila_header + 1:].reset_index(drop=True)
df = df.dropna(how="all")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

costos = {"Chinchorro":180000,"Mochila Wayuu":80000,"Manilla":15000,"Sombrero":45000,"Bolso":60000,"Chinchorros":180000,"Mochilas":80000,"Bolso cuero":120000,"Hamaca":90000,"Manilla artesanal":15000,"Sombrero Vueltiao":45000}
df["Costo"] = df["Producto"].map(costos).fillna(50000)
df["Ganancia"] = df["Total"] - df["Costo"]

# METRICAS PROFESIONALES
col1,col2,col3,col4 = st.columns(4)
col1.metric("💰 VENDIDO TOTAL", f"${df['Total'].sum():,.0f}", f"{len(df)} pedidos")
col2.metric("📦 COSTO ARTESANAS", f"${df['Costo'].sum():,.0f}")
col3.metric("✨ TU GANANCIA", f"${df['Ganancia'].sum():,.0f}", f"{(df['Ganancia'].sum()/df['Total'].sum()*100):.0f}% margen")
col4.metric("🎯 TICKET PROMEDIO", f"${df['Total'].mean():,.0f}")

st.divider()

# DOS COLUMNAS: GANANCIA MES + MAS VENDIDO
c_left, c_right = st.columns([2,1])
with c_left:
    st.subheader("📈 Tu ganancia por mes")
    df["Mes"] = df["Fecha"].dt.strftime("%Y-%m")
    ganancia_mes = df.groupby("Mes")["Ganancia"].sum().reset_index()
    chart_mes = alt.Chart(ganancia_mes).mark_bar(color="#FF5733", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x="Mes", y="Ganancia", tooltip=["Mes","Ganancia"]).properties(height=300)
    st.altair_chart(chart_mes, use_container_width=True)
    if not ganancia_mes.empty:
        mejor = ganancia_mes.loc[ganancia_mes["Ganancia"].idxmax()]
        st.info(f"🏆 Tu mejor mes fue **{mejor['Mes']}** con **${mejor['Ganancia']:,.0f}** de ganancia")

with c_right:
    top_producto = df["Producto"].mode()[0]
    st.subheader("🔥 Lo más vendido")
    st.success(f"**{top_producto}**\n\nEs lo que más se vende. ¡Pide más de esto a tus artesanas!")
    st.metric("Stock inicial", "68 unidades")
    st.metric("Objetivo", "50 unidades")

# INVENTARIO PROFESIONAL CON WHATSAPP
st.divider()
st.subheader("⚠️ Alerta de Inventario Inteligente")
stock_inicial = 68
stock_objetivo = 50
ventas_por_producto = df["Producto"].value_counts()
stock_actual = stock_inicial - ventas_por_producto

cols = st.columns(3)
for i, (prod, stock) in enumerate(stock_actual.items()):
    with cols[i % 3]:
        if stock < 10:
            st.error(f"**{prod}**\n\nTe quedan solo **{stock}** - ¡Pide ya!")
            msg = f"Hola, soy Betzy (3003508492) de Tienda La Guajira. Me quedan solo {stock} de {prod}. Necesito {stock_objetivo-stock} más para completar. ¿Me confirmas?"
            link = f"https://wa.me/{NUMERO_BETZY}?text={urllib.parse.quote(msg)}"
            st.link_button(f"📲 Pedir {prod}", link, use_container_width=True)
        elif stock < 20:
            st.warning(f"**{prod}**\n\nQuedan {stock} - Ve pidiendo")
        else:
            st.success(f"**{prod}**\n\nTe quedan {stock} - Vas bien")

st.subheader("📋 Qué debes pedir hoy")
pedidos = []
for prod, stock in stock_actual.items():
    if stock < stock_objetivo:
        pedir = stock_objetivo - stock
        pedidos.append({"Producto": prod, "Te quedan": stock, "Pide": pedir, "Prioridad": "🔴 Urgente" if stock < 10 else "🟡 Pronto"})

if pedidos:
    df_pedidos = pd.DataFrame(pedidos)
    st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
    c1,c2 = st.columns(2)
    c1.download_button("📥 Descargar pedido (CSV)", df_pedidos.to_csv(index=False), "pedidos_artesana.csv", "text/csv", use_container_width=True)
    todos_msg = "\n".join([f"- {p['Pide']} de {p['Producto']}" for p in pedidos])
    msg_all = f"Hola artesana, soy Betzy 3003508492. Necesito este pedido:\n{todos_msg}"
    c2.link_button("📲 Enviar TODO el pedido por WhatsApp", f"https://wa.me/{NUMERO_BETZY}?text={urllib.parse.quote(msg_all)}", use_container_width=True)
else:
    st.balloons()
    st.success("¡Estás full de inventario! No necesitas pedir hoy.")

# FILTROS CON FECHAS
st.divider()
st.sidebar.header("🔍 Filtros Profesionales")
producto_filtro = st.sidebar.multiselect("Filtrar por Producto", df["Producto"].unique(), default=df["Producto"].unique())
fechas_validas = df["Fecha"].dropna()
if not fechas_validas.empty:
    rango_fechas = st.sidebar.date_input("📅 Rango de fechas", [fechas_validas.min().date(), fechas_validas.max().date()])
    if len(rango_fechas) == 2:
        df_f = df[(df["Fecha"] >= pd.to_datetime(rango_fechas[0])) & (df["Fecha"] <= pd.to_datetime(rango_fechas[1]))]
        df_f = df_f[df_f["Producto"].isin(producto_filtro)]
    else:
        df_f = df[df["Producto"].isin(producto_filtro)]
else:
    df_f = df[df["Producto"].isin(producto_filtro)]

c1,c2,c3 = st.columns(3)
c1.metric("Ventas Filtradas", f"${df_f['Total'].sum():,.0f} COP")
c2.metric("Pedidos Filtrados", len(df_f))
c3.metric("Ticket Promedio", f"${df_f['Total'].mean():,.0f} COP")

with st.expander("📄 Ver detalle de ventas completo", expanded=False):
    st.dataframe(df_f, use_container_width=True)

# GRAFICO COLORES WAYUU PROFESIONAL
st.subheader("🎨 Ventas con colores Wayuu")
ventas_producto = df_f.groupby("Producto")["Total"].sum().reset_index()
grafico = alt.Chart(ventas_producto).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
    x=alt.X("Producto", sort="-y"), y="Total",
    color=alt.Color("Producto", scale=alt.Scale(range=["#FFC300","#C70039","#581845","#FF5733","#DAF7A6","#F4D03F"]), legend=None),
    tooltip=["Producto","Total"]
).properties(height=400)
st.altair_chart(grafico, use_container_width=True)

# MAPA PROFESIONAL
st.subheader("🗺️ De dónde nos compran - La Guajira")
st.caption("Mapa interactivo | Toca los puntos naranjas para ver pedidos")

if "Ciudad" in df_f.columns:
    mapa_data = df_f.groupby("Ciudad").size().reset_index(name="Pedidos")
else:
    mapa_data = pd.DataFrame([{"Ciudad":"Riohacha","Pedidos":35},{"Ciudad":"Uribia","Pedidos":25},{"Ciudad":"Maicao","Pedidos":20},{"Ciudad":"Manaure","Pedidos":12}])

def get_lon(c): return {"Riohacha":-72.9072,"Uribia":-72.268,"Maicao":-72.241,"Manaure":-72.445}.get(c,-72.9072)
def get_lat(c): return {"Riohacha":11.5444,"Uribia":11.714,"Maicao":11.379,"Manaure":11.779}.get(c,11.5444)

mapa_data["lon"] = mapa_data["Ciudad"].apply(get_lon)
mapa_data["lat"] = mapa_data["Ciudad"].apply(get_lat)
mapa_data["size"] = mapa_data["Pedidos"] * 2500

layer = pdk.Layer("ScatterplotLayer", mapa_data, get_position="[lon, lat]", get_color="[255, 87, 34, 220]", get_radius="size", pickable=True, stroked=True, get_line_color="[255,255,255]", line_width_min_pixels=2)
view = pdk.ViewState(latitude=11.55, longitude=-72.55, zoom=8, pitch=20)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"html":"<b>{Ciudad}</b><br/>{Pedidos} pedidos", "style":{"backgroundColor":"#FF5733","color":"white"}}, map_style="dark"))

st.success("✨ Dashboard profesional listo - Tienda La Guajira | Contacto WhatsApp: 3003508492")
