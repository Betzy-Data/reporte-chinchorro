
import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="Artesanias La Guajira", layout="wide")
st.title("🧶Tienda La Guajira - Que se vendio hoy?")
st.write("Sube tu Excel de ventas y te digo que pedir y cuanto ganaste")
archivo = glob.glob("*.xlsx")[0]
df_raw = pd.read_excel(archivo, header=None)

fila_header = 0
for i in range(20):
    texto = " ".join([str(x) for x in df_raw.iloc[i].tolist() if str(x) != 'nan'])
    if "Fecha" in texto or "Producto" in texto:
        fila_header = i
        break

df_raw.columns = df_raw.iloc[fila_header]
df = df_raw.iloc[fila_header + 1:].reset_index(drop=True)
df = df.dropna(how='all')

# Limpiar tipos
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
df['Fecha'] = df['Fecha'].dt.strftime('%d/%m/%Y')

df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')

# Producto estrella
top_producto = df['Producto'].mode()[0]
st.success(f"Lo que mas se vende es: {top_producto} - Pide mas de esto!")

# Filtros
st.sidebar.header("Filtros")
producto_filtro = st.sidebar.multiselect("Producto", df['Producto'].unique(), default=df['Producto'].unique())
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
fechas_validas = df['Fecha'].dropna()
if not fechas_validas.empty:
    rango_fechas = st.sidebar.date_input("Rango de fechas", [fechas_validas.min().date(), fechas_validas.max().date()])
else:
    rango_fechas = []
df['Fecha'] = df['Fecha'].dt.date
df_f = df[df['Producto'].isin(producto_filtro)]
if len(rango_fechas) == 2:
    df_f = df_f[(df_f['Fecha'] >= rango_fechas[0]) & (df_f['Fecha'] <= rango_fechas[1])]                                                        
# Metricas
c1, c2, c3 = st.columns(3)
c1.metric("Ventas Totales", f"${df_f['Total'].sum():,.0f} COP")
c2.metric("Total Pedidos", len(df_f))
c3.metric("Ticket Promedio", f"${df_f['Total'].mean():,.0f} COP")

# Tablas y graficos
st.subheader("Detalle de ventas")
st.dataframe(df_f, use_container_width=True)

# Grafico con colores Wayuu
import altair as alt
st.subheader("Ventas con colores Wayuu")

ventas_producto = df_f.groupby('Producto')['Total'].sum().reset_index()

grafico = alt.Chart(ventas_producto).mark_bar().encode(
    x='Producto',
    y='Total',
    color=alt.Color('Producto', scale=alt.Scale(range=['#FFC300', '#C70039', '#581845', '#FF5733', '#DAF7A6'])),
    tooltip=['Producto', 'Total']
).properties(height=400)

st.altair_chart(grafico, use_container_width=True)

# CLASE 5 - MAPA LA GUAJIRA
st.subheader("🗺️ De dónde nos compran")

# Coordenadas de La Guajira
ciudades_coords = {
    "Riohacha": [11.544, -72.907],
    "Maicao": [11.379, -72.241],
    "Manaure": [11.779, -72.445],
    "Uribia": [11.714, -72.266],
    "Albania": [11.161, -72.583],
    "Fonseca": [10.888, -72.854]
}

# Agrupamos tus ventas por ciudad
mapa_data = df.groupby("Ciudad").size().reset_index(name="Pedidos")
mapa_data["lat"] = mapa_data["Ciudad"].map(lambda x: ciudades_coords.get(x, [11.5, -72.9])[0])
mapa_data["lon"] = mapa_data["Ciudad"].map(lambda x: ciudades_coords.get(x, [11.5, -72.9])[1])

st.map(mapa_data, latitude="lat", longitude="lon", size="Pedidos", color="#FF5722")
st.caption("Mientras más grande el punto, más pedidos de esa ciudad")
