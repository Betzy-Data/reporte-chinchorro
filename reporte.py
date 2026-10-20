import streamlit as st
import pandas as pd
import glob

st.title("Reporte Artesanias La Guajira - VERSION FINAL")
st.warning("Si ves este letrero amarillo, el codigo nuevo SI se cargo")

archivo = glob.glob("*.xlsx")[0]
st.success(f"Archivo: {archivo}")

# Leemos sin titulo
df_raw = pd.read_excel(archivo, header=None)
df_raw = df_raw.dropna(how='all', axis=0)

st.write("Fila 0 original:", df_raw.iloc[0].tolist())

# Si la fila 0 tiene la palabra Fecha, usala como titulo
if "Fecha" in str(df_raw.iloc[0].tolist()):
    df_raw.columns = df_raw.iloc[0]
    df = df_raw[1:].reset_index(drop=True)
else:
    df = pd.read_excel(archivo)

df = df.dropna(how='all')
st.write("Columnas finales:", list(df.columns))
st.dataframe(df.head(10))

if 'Total' in df.columns:
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    st.metric("Ventas Totales", f"${df['Total'].sum():,.0f} COP")
    st.metric("Numero de ventas", len(df))
    if 'Producto' in df.columns:
        st.bar_chart(df.groupby('Producto')['Total'].sum())
