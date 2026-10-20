import streamlit as st
import pandas as pd

st.title("Reporte La Guajira - PRUEBA 5")
st.warning("Si ves PRUEBA 5, ya se actualizo!")

# Leemos el Excel tal cual esta
df = pd.read_excel("Hoja de cálculo sin título.xlsx", header=None)

st.write("PRIMERA FILA DEL EXCEL:")
st.write(df.iloc[0].tolist())

# Usamos la primera fila que tiene texto como titulos
df.columns = df.iloc[0]
df = df[1:]
df = df.dropna(how='all')

st.write("Columnas arregladas:")
st.write(list(df.columns))
st.dataframe(df)

if 'Total' in df.columns:
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    st.metric("Ventas Totales", f"${df['Total'].sum():,.0f} COP")
