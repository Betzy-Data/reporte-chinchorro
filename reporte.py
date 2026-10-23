import streamlit as st
import pandas as pd
import glob
from datetime import date
import urllib.parse

st.set_page_config(page_title="Artesanias La Guajira", layout="wide")
st.title("Tienda La Guajira - Que se vendio hoy?")
st.write("Registra tus ventas desde el celular")

# TU NUMERO YA PUESTO
NUMERO_ARTESANA = "573003508492"  # Betzy 3003508492

archivos = glob.glob("*.xlsx")
archivo = archivos[0]
df_raw = pd.read_excel(archivo, header=None)

fila_header = 0
for i in range(20):
    texto = " ".join(str(x) for x in df_raw.iloc[i].tolist() if str(x) != 'nan')
    if "Fecha" in texto or "Producto" in texto:
        fila_header = i
        break

df_raw.columns = df_raw.iloc[fila_header]
df = df_raw.iloc[fila_header+1:].reset_index(drop=True)
df = df.dropna(how="all")

df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce")
df["Producto"] = df["Producto"].astype(str).str.strip()

costos_artesana = {
    "Chinchorro": 180000, "Mochila Wayuu": 80000,
    "Manilla": 15000, "Sombrero": 45000,
    "Bolso": 60000, "Chinchorros": 180000, "Mochilas": 80000
}
precios_venta = {
    "Chinchorro": 280000, "Mochila Wayuu": 180000,
    "Manilla": 35000, "Sombrero": 85000, "Bolso": 120000,
    "Chinchorros": 280000, "Mochilas": 180000
}

df["Costo"] = df["Producto"].map(costos_artesana).fillna(0) * df["Cantidad"].fillna(1)
df["Ganancia"] = df["Total"] - df["Costo"]

# FORMULARIO DESDE CELULAR
st.divider()
st.subheader("➕ Registrar venta desde el celular")
with st.form("form_venta"):
    colA, colB = st.columns(2)
    with colA:
        fecha_nueva = st.date_input("Fecha", value=date.today())
        producto_nuevo = st.selectbox("Producto", list(costos_artesana.keys()))
    with colB:
        cantidad_nueva = st.number_input("Cantidad", min_value=1, value=1, step=1)
        precio_unit = st.number_input("Precio c/u", value=precios_venta.get(producto_nuevo, 180000), step=1000)
    
    total_nuevo = cantidad_nueva * precio_unit
    st.info(f"Total: ${total_nuevo:,.0f} COP")
    guardar = st.form_submit_button("💾 Guardar venta", use_container_width=True)

    if guardar:
        nueva_fila = {"Fecha": fecha_nueva, "Producto": producto_nuevo, "Cantidad": cantidad_nueva, "Total": total_nuevo}
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        df[["Fecha","Producto","Cantidad","Total"]].to_excel(archivo, index=False)
        st.success(f"¡Guardado! {cantidad_nueva} x {producto_nuevo}")
        st.rerun()

# METRICAS
total_vendido = df["Total"].sum()
total_ganancia = df["Ganancia"].sum()
col1, col2 = st.columns(2)
col1.metric("💰 TU GANANCIA", f"${total_ganancia:,.0f}")
col2.metric("🛒 VENDIDO", f"${total_vendido:,.0f}")

# ALERTA + WHATSAPP CON TU NUMERO
st.divider()
st.subheader("⚠️ Alerta de Inventario")
stock_inicial = 50
ventas_por_prod = df.groupby("Producto")["Cantidad"].sum()

for prod in costos_artesana.keys():
    stock = stock_inicial - ventas_por_prod.get(prod, 0)
    a_pedir = stock_inicial - stock
    
    if stock < 10:
        st.error(f"🔴 Quedan solo {stock} de {prod} - ¡Pide ya!")
        mensaje = f"Hola! Soy Betzy. Quedan solo {stock} de {prod}. Necesito {a_pedir} mas. Mi num: 3003508492"
        link = f"https://wa.me/{NUMERO_ARTESANA}?text={urllib.parse.quote(mensaje)}"
        st.link_button(f"📲 Pedir {prod} por WhatsApp (a mi mismo para probar)", link, use_container_width=True)
    elif stock < 20:
        st.warning(f"🟡 Quedan {stock} de {prod}")
    else:
        st.success(f"🟢 Te quedan {stock} de {prod} - Vas bien")
