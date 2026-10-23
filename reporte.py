import streamlit as st
import pandas as pd
import glob
import urllib.parse
import altair as alt
import pydeck as pdk

st.set_page_config(page_title="Artesanias La Guajira", layout="wide")
st.title("Tienda La Guajira - Que se vendio hoy?")
st.write("Sube tu Excel de ventas y te digo que pedir y cuanto ganaste")

NUMERO_BETZY = "573003508492"
archivo = glob.glob("*.xlsx")[0]
df_raw = pd.read_excel(archivo, header=None)

fila_header = 0
for i in range(20):
    texto = " ".join(str(x) for x in df_raw.iloc[i].tolist() if str(x) != 'nan')
    if "Fecha" in texto or "Producto" in texto:
        fila_header = i
        break

df_raw.columns = df_raw.iloc[fila_header]
df = df_raw.iloc[fila_header + 1:].reset_index(drop=True)
df = df.dropna(how="all")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

costos_artesana = {"Chinchorro":180000,"Mochila Wayuu":80000,"Manilla":15000,"Sombrero":45000,"Bolso":60000,"Chinchorros":180000,"Mochilas":80000,"Bolso cuero":120000,"Hamaca":90000,"Manilla artesanal":15000,"Sombrero Vueltiao":45000}
df["Costo"] = df["Producto"].map(costos_artesana).fillna(50000)
df["Ganancia"] = df["Total"] - df["Costo"]

c1,c2,c3 = st.columns(3)
c1.metric("TU VENDIDO", f"${df['Total'].sum():,.0f}")
c2.metric("TU COSTO", f"${df['Costo'].sum():,.0f}")
c3.metric("TU GANANCIA", f"${df['Ganancia'].sum():,.0f}")

st.divider()
df["Mes"] = df["Fecha"].dt.strftime("%Y-%m")
ganancia_mes = df.groupby("Mes")["Ganancia"].sum()
st.subheader("Tu ganancia por mes")
st.bar_chart(ganancia_mes)
st.write(f"Tu mejor mes fue {ganancia_mes.idxmax()} con ${ganancia_mes.max():,.0f}")

top_producto = df["Producto"].mode()[0]
st.success(f"Lo que mas se vende es: {top_producto} - Pide mas de esto!")

st.divider()
st.subheader("Alerta de Inventario")
stock_inicial = 68
stock_objetivo = 50
ventas_por_producto = df["Producto"].value_counts()
stock_actual = stock_inicial - ventas_por_producto

for prod, stock in stock_actual.items():
    if stock < 10:
        st.error(f"Te quedan solo {stock} de {prod} - Pide ya a la artesana!")
        msg = f"Hola soy Betzy 3003508492 de Tienda La Guajira. Me quedan solo {stock} de {prod}. Necesito {stock_objetivo-stock} mas"
        link = f"https://wa.me/{NUMERO_BETZY}?text={urllib.parse.quote(msg)}"
        st.link_button(f"📲 Pedir {prod} por WhatsApp 3003508492", link)
    elif stock < 20:
        st.warning(f"Quedan {stock} de {prod} - Ve pidiendo")
    else:
        st.success(f"{prod}: te quedan {stock} - Vas bien")

st.write("## Que debes pedir hoy:")
pedidos = []
for prod, stock in stock_actual.items():
    if stock < stock_objetivo:
        pedir = stock_objetivo - stock
        st.write(f"Pide {pedir} de {prod} a la artesana")
        pedidos.append({"Producto": prod, "Te quedan": stock, "Pide": pedir})

if pedidos:
    df_pedidos = pd.DataFrame(pedidos)
    st.dataframe(df_pedidos)
    st.download_button("Descargar pedido para la artesana", df_pedidos.to_csv(index=False), "pedidos_artesana.csv", "text/csv")
else:
    st.write("Hoy no tienes que pedir nada, estas full!")

st.sidebar.header("Filtros")
producto_filtro = st.sidebar.multiselect("Producto", df["Producto"].unique(), default=df["Producto"].unique())
fechas_validas = df["Fecha"].dropna()
if not fechas_validas.empty:
    rango_fechas = st.sidebar.date_input("Rango de fechas", [fechas_validas.min().date(), fechas_validas.max().date()])
    if len(rango_fechas) == 2:
        df_f = df[(df["Fecha"] >= pd.to_datetime(rango_fechas[0])) & (df["Fecha"] <= pd.to_datetime(rango_fechas[1]))]
        df_f = df_f[df_f["Producto"].isin(producto_filtro)]
    else:
        df_f = df[df["Producto"].isin(producto_filtro)]
else:
    df_f = df[df["Producto"].isin(producto_filtro)]

c1,c2,c3 = st.columns(3)
c1.metric("Ventas Totales", f"${df_f['Total'].sum():,.0f} COP")
c2.metric("Total Pedidos", len(df_f))
c3.metric("Ticket Promedio", f"${df_f['Total'].mean():,.0f} COP")

st.subheader("Detalle de ventas")
st.dataframe(df_f, use_container_width=True)

st.subheader("Ventas con colores Wayuu")
ventas_producto = df_f.groupby("Producto")["Total"].sum().reset_index()
grafico = alt.Chart(ventas_producto).mark_bar().encode(x="Producto", y="Total", color=alt.Color("Producto", scale=alt.Scale(range=["#FFC300","#C70039","#581845","#FF5733","#DAF7A6"])), tooltip=["Producto","Total"]).properties(height=400)
st.altair_chart(grafico, use_container_width=True)

st.subheader("De dónde nos compran")
if "Ciudad" in df_f.columns:
    mapa_data = df_f.groupby("Ciudad").size().reset_index(name="Pedidos")
else:
    mapa_data = pd.DataFrame([{"Ciudad":"Riohacha","Pedidos":35},{"Ciudad":"Uribia","Pedidos":25},{"Ciudad":"Maicao","Pedidos":20}])

def get_lon(c): return {"Riohacha":-72.907,"Uribia":-72.268,"Maicao":-72.241,"Manaure":-72.445}.get(c,-72.907)
def get_lat(c): return {"Riohacha":11.544,"Uribia":11.714,"Maicao":11.379,"Manaure":11.779}.get(c,11.544)

mapa_data["lon"] = mapa_data["Ciudad"].apply(get_lon)
mapa_data["lat"] = mapa_data["Ciudad"].apply(get_lat)
mapa_data["size"] = mapa_data["Pedidos"]*2000
layer = pdk.Layer("ScatterplotLayer", mapa_data, get_position="[lon, lat]", get_color="[255, 87, 34, 200]", get_radius="size", pickable=True)
view = pdk.ViewState(latitude=11.5, longitude=-72.6, zoom=7.5)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"text":"{Ciudad}: {Pedidos} pedidos"}))
st.caption("Mientras más grande el punto, más pedidos de esa ciudad - Toca el punto para ver")
