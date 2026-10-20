
import streamlit as st
import pandas as pd
import glob

st.title("Reporte Artesanias La Guajira - FINAL FINAL")
st.success("Codigo nuevo cargado!")

archivo = glob.glob("*.xlsx")[0]
df_raw = pd.read_excel(archivo, header=None)

# Buscar donde esta Fecha o Producto, saltando vacios
fila_header = 0
for i in range(20):
    fila_lista = df_raw.iloc[i].tolist()
    # convertir todo a texto y quitar nulos
    texto = " ".join([str(x) for x in fila_lista if str(x) != 'nan'])
    if "Fecha" in texto or "Producto" in texto:
        fila_header = i
        break

st.write(f"Encabezado encontrado en fila: {fila_header + 1}")

df_raw.columns = df_raw.iloc[fila_header]
df = df_raw.iloc[fila_header + 1:].reset_index(drop=True)
df = df.dropna(how='all')

st.write("Columnas finales:", list(df.columns))
st.dataframe(df)

if 'Total' in df.columns:
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    st.metric("Ventas Totales", f"${df['Total'].sum():,.0f} COP")
    st.metric("Numero de ventas", len(df))
    if 'Producto' in df.columns:
        st.bar_chart(df.groupby('Producto')['Total'].sum())
