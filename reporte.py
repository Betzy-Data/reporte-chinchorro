import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tienda La Guajira - Inventario Pro", layout="wide")

# --- CSS PROFESIONAL COMO LAS FOTOS ---
st.markdown("""
<style>
.metric-card {background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:4px solid #4F46E5;}
.semaforo-verde {background:#DCFCE7; color:#166534; padding:4px 10px; border-radius:20px; font-weight:bold; font-size:12px;}
.semaforo-rojo {background:#FEE2E2; color:#991B1B; padding:4px 10px; border-radius:20px; font-weight:bold; font-size:12px;}
.semaforo-amarillo {background:#FEF3C7; color:#92400E; padding:4px 10px; border-radius:20px; font-weight:bold; font-size:12px;}
</style>
""", unsafe_allow_html=True)

# --- DATOS INICIALES (PRUEBA Y MANUAL) ---
if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame([
        {"SKU":"CHIN-001","Nombre":"Chinchorro Tradicional Wayuu","Categoría":"Chinchorros","Precio":180000,"Costo":120000,"Stock":18,"Minimo":20,"Unidades Vendidas":45},
        {"SKU":"MOCH-002","Nombre":"Mochila Wayuu Grande","Categoría":"Mochilas","Precio":95000,"Costo":60000,"Stock":5,"Minimo":10,"Unidades Vendidas":80},
        {"SKU":"CHIN-003","Nombre":"Chinchorro Doble King","Categoría":"Chinchorros","Precio":250000,"Costo":160000,"Stock":0,"Minimo":5,"Unidades Vendidas":12},
        {"SKU":"MANI-004","Nombre":"Manilla Wayuu","Categoría":"Accesorios","Precio":15000,"Costo":8000,"Stock":120,"Minimo":30,"Unidades Vendidas":200},
    ])
if 'movimientos' not in st.session_state:
    st.session_state.movimientos = pd.DataFrame(columns=["Fecha","SKU","Tipo","Cantidad","Nota"])

def semaforo(stock, minimo):
    if stock == 0:
        return '<span class="semaforo-rojo">● AGOTADO</span>'
    elif stock <= minimo:
        return '<span class="semaforo-amarillo">● BAJO</span>'
    else:
        return '<span class="semaforo-verde">● SALUDABLE</span>'

# --- INDICADORES PRINCIPALES ---
st.title("🧶 Inventario - Tienda La Guajira")
df = st.session_state.productos
df["Valor Inventario"] = df["Stock"] * df["Costo"]
df["Valor Venta"] = df["Stock"] * df["Precio"]

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="metric-card"><small>Unidades Disponibles</small><h2>{df["Stock"].sum()}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="metric-card"><small>Productos Agotados</small><h2 style="color:red">{len(df[df["Stock"]==0])}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="metric-card"><small>Stock Bajo</small><h2 style="color:orange">{len(df[df["Stock"]<=df["Minimo"]])}</h2></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="metric-card"><small>Valor Inventario</small><h2>${df["Valor Inventario"].sum():,.0f}</h2></div>', unsafe_allow_html=True)

st.write("---")
# --- FILTROS Y BÚSQUEDA ---
col_f1, col_f2 = st.columns([2,1])
busqueda = col_f1.text_input("🔍 Buscar producto, SKU o categoría")
categoria = col_f2.selectbox("Categoría", ["Todas"] + list(df["Categoría"].unique()))

df_filtro = df.copy()
if busqueda:
    df_filtro = df_filtro[df_filtro.apply(lambda x: busqueda.lower() in str(x).lower(), axis=1)]
if categoria != "Todas":
    df_filtro = df_filtro[df_filtro["Categoría"]==categoria]

# --- TABS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 Stock por producto", "📥 Entradas y Salidas", "🛒 Recomendación de Compra", "💰 Ventas y Rentabilidad"])

with tab1:
    # 1. CARGA DE PRODUCTOS
    st.subheader("1. Carga de productos")
    with st.expander("➕ Agregar nuevo producto (Nombre, SKU, Categoría, Precio, Cantidad)"):
        with st.form("nuevo"):
            c1,c2,c3 = st.columns(3)
            sku = c1.text_input("Código SKU")
            nombre = c2.text_input("Nombre")
            cat = c3.selectbox("Categoría", ["Chinchorros","Mochilas","Accesorios"])
            c4,c5,c6,c7 = st.columns(4)
            precio = c4.number_input("Precio", min_value=0)
            costo = c5.number_input("Costo", min_value=0)
            stock = c6.number_input("Cantidad disponible", min_value=0)
            minimo = c7.number_input("Stock mínimo", min_value=1, value=10)
            if st.form_submit_button("Guardar producto"):
                nuevo = pd.DataFrame([{"SKU":sku,"Nombre":nombre,"Categoría":cat,"Precio":precio,"Costo":costo,"Stock":stock,"Minimo":minimo,"Unidades Vendidas":0}])
                st.session_state.productos = pd.concat([st.session_state.productos, nuevo], ignore_index=True)
                st.success("Producto guardado!")
                st.rerun()

    # 3. SEMÁFORO DE INVENTARIO
    st.subheader("Stock por producto con Semáforo")
    df_show = df_filtro.copy()
    df_show["Semáforo"] = df_show.apply(lambda r: semaforo(r["Stock"], r["Minimo"]), axis=1)
    st.write(df_show[["SKU","Nombre","Stock","Minimo","Semáforo"]].to_html(escape=False), unsafe_allow_html=True)

    st.bar_chart(df_filtro.set_index("Nombre")["Stock"])

with tab2:
    # 2. ENTRADAS Y SALIDAS
    st.subheader("2. Entradas y salidas (sin editar manualmente)")
    with st.form("mov"):
        c1,c2,c3 = st.columns(3)
        sku_mov = c1.selectbox("Producto", df["SKU"].tolist())
        tipo = c2.selectbox("Tipo", ["Compra (Entrada)", "Venta (Salida)"])
        cant = c3.number_input("Cantidad", min_value=1, value=1)
        nota = st.text_input("Nota")
        if st.form_submit_button("Registrar movimiento"):
            idx = df.index[df["SKU"]==sku_mov][0]
            if "Venta" in tipo:
                st.session_state.productos.at[idx, "Stock"] -= cant
                st.session_state.productos.at[idx, "Unidades Vendidas"] += cant
            else:
                st.session_state.productos.at[idx, "Stock"] += cant
            
            mov = pd.DataFrame([{"Fecha":pd.Timestamp.now(),"SKU":sku_mov,"Tipo":tipo,"Cantidad":cant,"Nota":nota}])
            st.session_state.movimientos = pd.concat([st.session_state.movimientos, mov], ignore_index=True)
            st.success(f"Stock actualizado automáticamente")
            st.rerun()
    st.dataframe(st.session_state.movimientos, use_container_width=True)

with tab3:
    # 4. RECOMENDACIÓN DE COMPRA
    st.subheader("4. Recomendación de compra")
    bajo = df[df["Stock"] <= df["Minimo"]].copy()
    bajo["Cuánto reponer"] = bajo["Minimo"]*2 - bajo["Stock"]
    bajo["Prioridad"] = bajo.apply(lambda r: "URGENTE" if r["Stock"]==0 else "Pronto", axis=1)
    st.dataframe(bajo[["SKU","Nombre","Stock","Minimo","Cuánto reponer","Prioridad"]].sort_values("Stock"), use_container_width=True)
    if len(bajo)>0:
        st.warning(f"Debes pedir primero: {', '.join(bajo.sort_values('Stock')['Nombre'].tolist()[:3])}")

with tab4:
    # 6. VENTAS Y RENTABILIDAD
    st.subheader("6. Ventas y rentabilidad")
    df["Ganancia Unidad"] = df["Precio"] - df["Costo"]
    df["Ganancia Total"] = df["Ganancia Unidad"] * df["Unidades Vendidas"]
    colA, colB = st.columns(2)
    colA.metric("Ganancia total estimada", f"${df['Ganancia Total'].sum():,.0f}")
    colB.metric("Margen promedio", f"{(df['Ganancia Unidad'].mean()/df['Precio'].mean()*100):.1f}%")
    
    chart = alt.Chart(df).mark_bar().encode(
        x='Nombre', y='Ganancia Total', color='Categoría',
        tooltip=['Nombre','Unidades Vendidas','Ganancia Total']
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

st.caption("✅ Lista de comprobación completada: Prueba con datos de ejemplo de chinchorros. Para el manual, usa la pestaña Entradas y Salidas para mostrar cómo no editas el Excel a mano.")
