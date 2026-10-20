import streamlit as st
import pandas as pd

st.set_page_config(page_title="Reporte Chinchorro", page_icon="🧶")
st.title("🧶 Dashboard Ventas - Chinchorros")
st.write("Reporte automatico para tienda de artesanias La Guajira")

df = pd.read_excel("Hoja de cálculo sin título.xlsx")

col1, col2 = st.columns(2)
col1.metric("Ventas Totales", f"${df['Total'].sum():,} COP")
col2.metric("Productos", df['Cantidad'].sum())

st.divider()
st.bar_chart(df.groupby('Producto')['Total'].sum())
st.dataframe(df)
