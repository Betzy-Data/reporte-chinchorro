import streamlit as st
import pandas as pd
import glob
from datetime import date
import urllib.parse

st.set_page_config(page_title="Tienda La Guajira", layout="wide")

# TU NUMERO - YA PUESTO
NUMERO_ARTESANA = "573003508492"  # Betzy 3003508492

st.title("🧶 Tienda La Guajira - Que se vendio hoy?")
st.write("Sube tu Excel de ventas y te digo que pedir y cuanto ganaste")

# Buscar Excel
archivos = glob.glob("*.xlsx")
if not archivos:
    st.error("No encuentro tu Excel. Súbelo a GitHub.")
    st.stop()

archivo = archivos[0]
df_raw = pd.read_excel(archivo, header=None)

# Detectar donde empieza tu tabla
fila_header = 0
for i in range(20):
    texto = " ".join(str(x) for x in df_raw.iloc[i].tolist() if str(x) != 'nan')
    if "Fecha" in texto or "Producto" in texto or "Factura" in texto:
        fila_header = i
        break

df_raw.columns = df_raw.iloc[fila_header]
df = df_raw.iloc[fila_header+1:].reset_index(drop=True)
df = df.dropna(how="all")
df.columns = [str(c).strip() for c in df.columns]

# Limpiar columnas
for col in ["Fecha","Total","Cantidad","Precio","Vendido","Ganancia"]:
    if col in df.columns:
        if col == "Fecha":
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

if "Producto" in df.columns:
    df["Producto"] = df["Producto"].astype(str).str.strip()
if "Cantidad" not in df.columns:
    df["Cantidad"] = 1

# Costos
costos = {
    "Chinchorro": 120000, "Chinchorros": 120000,
    "Mochila Wayuu": 80000, "Mochilas": 80000, "Mochila": 80000,
    "Manilla artesanal": 15000, "Manilla": 15000,
    "Hamaca": 60000, "Bolso cuero": 90000, "Bolso": 60000,
    "Sombrero Vueltiao": 45000, "Sombrero": 45000
}

if "Costo" not in df.columns:
    df["Costo"] = df["Producto"].map(costos).fillna(70000) * df["Cantidad"].fillna(1)
if "Ganancia" not in df.columns and "Total" in df.columns:
    df["Ganancia"] = df["Total"] - df["Costo"]

# ====== NUEVO: FORMULARIO PARA AGREGAR DESDE EL CELULAR ======
st.divider
