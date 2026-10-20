
import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="Artesanias La Guajira", layout="wide")
st.title("🧶 Reporte Artesanias La Guajira")

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
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')

# Filtros
st.sidebar.header("Filtros")
producto_filtro = st.sidebar.multiselect("Producto", df['Producto'].unique(), default=df['Producto'].unique())
df_f = df[df['Producto'].isin(producto_filtro)]

# Metricas
c1, c2, c3 = st.columns(3)
c1.metric("Ventas Totales", f"${df_f['Total'].sum():,.0f} COP")
c2.metric("Total Pedidos", len(df_f))
c3.metric("Ticket Promedio", f"${df_f['Total'].mean():,.0f} COP")

# Tablas y graficos
st.subheader("Detalle de ventas")
st.dataframe(df_f, use_container_width=True)

st.subheader("Ventas por producto")
st.bar_chart(df_f.groupby('Producto')['Total'].sum())

st.subheader("Ventas por ciudad")
st.bar_chart(df_f.groupby('Ciudad')['Total'].sum())
