import streamlit as st
import pandas as pd
import glob

st.title("Reporte Artesanias La Guajira")

archivo = glob.glob("*.xlsx")[0]
st.success(f"Archivo cargado: {archivo}")

# Leemos todo sin encabezado
df_temp = pd.read_excel(archivo, header=None)
df_temp = df_temp.dropna(how='all')

# La primera fila que tiene "Fecha" es el titulo
# La ponemos como columnas
df_temp.columns = df_temp.iloc[0]
df = df_temp[1:].reset_index(drop=True)

# Limpiar
df = df.dropna(how='all')
st.write("Columnas encontradas:")
st.write(list(df.columns))
st.dataframe(df)

# Ahora si calcula totales
if 'Total' in df.columns:
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    c1, c2 = st.columns(2)
    c1.metric("Ventas Totales", f"${df['Total'].sum():,.0f} COP")
    c2.metric("Ventas", f"{len(df)}")

    if 'Producto' in df.columns:
        st.subheader("Ventas por Producto")
        st.bar_chart(df.groupby('Producto')['Total'].sum())
