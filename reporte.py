import streamlit as st
import pandas as pd
import glob
import urllib.parse
from datetime import date

st.set_page_config(page_title="Tienda La Guajira", layout="wide", page_icon="🧶")

# NUMERO DE BETZY - YA CONFIGURADO
NUMERO_BETZY = "573003508492"

st.title("🧶 Tienda La Guajira - Que se vendio hoy?")
st.markdown("Sube tu Excel de ventas y te digo que pedir y cuanto ganaste")

# --- LEER TU EXCEL ORIGINAL ---
archivos = glob.glob("*.xlsx")
if not archivos:
    st.error("Súbeme tu Excel a GitHub")
    st.stop()

df_raw = pd.read_excel(archivos[0], header=None)

# Buscar donde empieza tu tabla
fila = 0
for i in range(25):
    txt = " ".join([str(x) for x in df_raw.iloc[i].tolist()])
    if "Fecha" in txt or "Producto" in txt:
        fila = i
        break

df_raw.columns = df_raw.iloc[fila]
df = df_raw.iloc[fila+1:].copy()
df = df.dropna(how="all")
df.columns = [str(c).strip() for c in df.columns]
df = df[~df["Fecha"].astype(str).str.contains("Fecha", na=False)]

# Convertir numeros
for c in ["Total", "Cantidad"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
if "Cantidad" not in df.columns:
    df["Cantidad"] = 1
df["Producto"] = df["Producto"].astype(str)

# Costos Wayuu
costos = {"Chinchorro":120000, "Chinchorros":120000, "Mochila Wayuu":80000, "Mochila":80000, "Manilla artesanal":15000, "Manilla":15000, "Hamaca":60000, "Bolso cuero":90000, "Bolso":60000, "Sombrero Vueltiao":45000}
df["Costo"] = df["Producto"].map(costos).fillna(70000) * df["Cantidad"].fillna(1)
df["Ganancia"] = df["Total"] - df["Costo"]

# --- TUS 3 CAJITAS DE SIEMPRE ---
vendido = df["Total"].sum()
a_artesanas = df["Costo"].sum()
tu_ganancia = df["Ganancia"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 VENDIDO", f"${vendido:,.0f}")
col2.metric("🧶 A ARTESANAS", f"${a_artesanas:,.0f}")
col3.metric("✨ TU GANANCIA", f"${tu_ganancia:,.0f}", delta=f"{len(df)} pedidos")

# Lo que mas se vende
mas_vendido = df["Producto"].mode()[0]
st.success(f"✅ Lo que mas se vende es: **{mas_vendido}** - ¡Pide mas de esto!")

# --- VENTAS TOTALES, PEDIDOS, TICKET ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Ventas Totales**")
    st.header(f"${vendido:,.0f} COP")
with c2:
    st.markdown("**Total Pedidos**")
    st.header(f"{len(df)}")
with c3:
    st.markdown("**Ticket Promedio**")
    st.header(f"${vendido/len(df):,.0f} COP" if len(df)>0 else "$0")

# --- DETALLE DE VENTAS ---
st.subheader("📋 Detalle de ventas")
st.dataframe(df[["Fecha","Factura","Producto","Cantidad","Total"]].tail(30) if "Factura" in df.columns else df.tail(30), use_container_width=True)

# --- TU GANANCIA POR MES (tu grafico original) ---
st.subheader("📈 Tu ganancia por mes")
df["Mes"] = df["Fecha"].dt.strftime("%Y-%m")
ganancia_mes = df.groupby("Mes")["Ganancia"].sum()
st.bar_chart(ganancia_mes, color="#E91E63")
if not ganancia_mes.empty:
    mejor_mes = ganancia_mes.idxmax()
    st.caption(f"Tu mejor mes fue {mejor_mes} con ${ganancia_mes.max():,.0f}")

# --- VENTAS CON COLORES WAYUU + MAPA ---
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🎨 Ventas con colores Wayuu")
    ventas_prod = df.groupby("Producto")["Total"].sum()
    st.bar_chart(ventas_prod, color="#FF5722")

with col_b:
    st.subheader("🗺️ Mapa: Riohacha, Uribia, Maicao")
    # Mapa simple de La Guajira
    mapa_data = pd.DataFrame({
        "lat": [11.5444, 11.714, 11.3777],
        "lon": [-72.9072, -72.266, -72.238],
        "lugar": ["Riohacha", "Uribia", "Maicao"],
        "ventas": [len(df)*0.5, len(df)*0.3, len(df)*0.2]
    })
    st.map(mapa_data, size="ventas", color="#E91E63")

# --- ALERTA INVENTARIO + WHATSAPP NUEVO (lo unico nuevo) ---
st.divider()
st.subheader("🚨 Alerta de Inventario")
stock_inicial = 50
ventas_por_prod = df.groupby("Producto")["Cantidad"].sum()

for prod in ["Chinchorro","Mochila Wayuu","Manilla artesanal","Hamaca","Bolso cuero","Sombrero Vueltiao","Chinchorros","Mochila","Manilla"]:
    if prod not in ventas_por_prod.index:
        continue
    quedan = stock_inicial - ventas_por_prod[prod]
    if quedan < 0:
        quedan = 0
    
    if quedan < 10:
        st.error(f"🔴 {prod}: te quedan {quedan:.0f} - ¡Pide YA!")
        texto = f"Hola! Soy Betzy de Tienda La Guajira 3003508492. Me quedan solo {quedan:.0f} de {prod}. Necesito mas por favor. Mi ganancia va en ${tu_ganancia:,.0f}"
        link = f"https://wa.me/{NUMERO_BETZY}?text={urllib.parse.quote(texto)}"
        st.link_button(f"📲 Pedir {prod} por WhatsApp a mi misma (probar)", link, use_container_width=True)
    elif quedan < 20:
        st.warning(f"🟡 {prod}: te quedan {quedan:.0f}")
    else:
        st.success(f"🟢 {prod}: te quedan {quedan:.0f} - Vas bien")

st.divider()
st.caption(f"WhatsApp configurado: +57 {NUMERO_BETZY} | Hecho con ❤️ en Riohacha")
