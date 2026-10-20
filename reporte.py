import streamlit as st
import pandas as pd
import glob

st.title("Reporte automatico para artesanias La Guajira")

archivos = glob.glob("*.xlsx")
archivo = archivos[0]
st.success(f"Archivo cargado: {archivo}")

# Leer Excel - prueba con y sin encabezados
df = pd.read_excel(archivo, header=1)

# Si sale Unnamed, quiere decir que no tiene titulos, leemos de otra forma
if all("Unnamed" in str(c) for c in df.columns):
    df_temp = pd.read_excel(archivo, header=None)
    # Busca la primera fila que tenga texto
    for i in range(min(5, len(df_temp))):
        fila = df_temp.iloc[i].dropna()
        if len(fila) >= 2:
            df = pd.read_excel(archivo, header=i)
            break
    # Si sigue sin titulos, le ponemos nosotros
    if all("Unnamed" in str(c) for c in df.columns):
        df = pd.read_excel(archivo, header=None)
        df.columns = [f"Columna_{j+1}" for j in range(len(df.columns))]

st.write("Columnas encontradas:", list(df.columns))
st.dataframe(df.head(10))

# Buscar columna numerica para total
col_num = df.select_dtypes(include='number').columns
if len(col_num) > 0:
    col_total = col_num[-1]  # ultima columna numerica suele ser el total
    total = df[col_total].sum()
    c1, c2 = st.columns(2)
    c1.metric("Ventas Totales", f"${total:,.0f} COP")
    c2.metric("Numero de ventas", f"{len(df)}")
    st.bar_chart(df[col_total])
else:
    st.warning("Tu Excel no tiene numeros, solo texto")
    st.write(df)

st.info("Tip: Para que se vea bonito, en tu Excel pon en la primera fila: Producto, Cantidad, Precio, Total")
