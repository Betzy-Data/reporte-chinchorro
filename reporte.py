import streamlit as st
import pandas as pd
import glob

st.title("Reporte artesanias La Guajira")

archivo = glob.glob("*.xlsx")[0]
st.success(f"Archivo cargado: {archivo}")

# Leemos sin titulos para buscar donde estan
df_raw = pd.read_excel(archivo, header=None)

# Buscar la fila que tiene "Producto" o "Total" o "Fecha"
fila_titulo = 0
for i in range(len(df_raw)):
    fila_texto = str(df_raw.iloc[i].tolist()).lower()
    if "producto" in fila_texto or "total" in fila_texto or "fecha" in fila_texto:
        fila_titulo = i
        break

st.write(f"Titulos encontrados en fila: {fila_titulo + 1}")

# Ahora leemos con esa fila como titulo
df = pd.read_excel(archivo, header=fila_titulo)
df = df.dropna(how='all') # quitar filas vacias

st.write("Columnas:", list(df.columns))
st.dataframe(df)

# Metricas
if 'Total' in df.columns:
    total = pd.to_numeric(df['Total'], errors='coerce').sum()
    st.metric("Ventas Totales", f"${total:,.0f} COP")
    st.metric("Numero de ventas", len(df))
    # Grafico por producto
    if 'Producto' in df.columns:
        st.bar_chart(df.groupby('Producto')['Total'].sum())
