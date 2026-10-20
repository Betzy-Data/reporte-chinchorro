import streamlit as st
import pandas as pd

st.title("Reporte automatico para tienda de artesanias La Guajira")

# Cargar Excel - busca el archivo automaticamente
import glob
archivos_excel = glob.glob("*.xlsx")
if not archivos_excel:
    st.error("No se encontro archivo Excel")
    st.stop()

archivo = archivos_excel[0]
df = pd.read_excel(archivo)

st.success(f"Archivo cargado: {archivo}")
st.write("Columnas encontradas:", list(df.columns))
st.dataframe(df.head())

# Detectar columna de total / precio / valor automaticamente
col_total = None
for c in df.columns:
    nombre = c.lower()
    if 'total' in nombre or 'valor' in nombre or 'precio' in nombre or 'venta' in nombre or 'monto' in nombre:
        col_total = c
        break

# Si no encuentra, usa la primera columna numerica
if col_total is None:
    numericas = df.select_dtypes(include='number').columns
    if len(numericas) > 0:
        col_total = numericas[0]

col1, col2 = st.columns(2)
if col_total:
    total = df[col_total].sum()
    col1.metric("Ventas Totales", f"${total:,.0f} COP")
else:
    col1.metric("Total registros", f"{len(df)}")

col2.metric("Numero de ventas", f"{len(df)}")

st.bar_chart(df[col_total] if col_total else df.iloc[:,0])
