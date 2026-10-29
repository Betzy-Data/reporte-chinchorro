import streamlit as st
import pandas as pd
st.set_page_config(page_title="Tienda La Guajira", layout="wide", page_icon="🧶")

# CSS PREMIUM - ESTO ES LO QUE LO PONE BONITO
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
body{font-family:'Inter';}
div[data-testid="stMetric"]{background:white; padding:18px; border-radius:14px; box-shadow:0 4px 12px rgba(0,0,0,0.06); border:1px solid #f1f1f1;}
.card{background:white; border-radius:16px; padding:20px; box-shadow:0 4px 20px rgba(0,0,0,0.07);}
</style>
""", unsafe_allow_html=True)

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame([
        ["CHIN-001","Chinchorro Tradicional","Chinchorros",180000,120000,18,20,45],
        ["MOCH-002","Mochila Wayuu Grande","Mochilas",95000,60000,5,10,80],
        ["CHIN-003","Chinchorro Doble","Chinchorros",250000,160000,0,5,12],
        ["ACC-004","Manilla Wayuu","Accesorios",15000,8000,120,30,200],
    ], columns=["SKU","Nombre","Categoría","Precio","Costo","Stock","Minimo","Vendidos"])

df = st.session_state.df
df["Valor"] = df["Stock"]*df["Precio"]

# HEADER
st.markdown("### 🧶 TIENDA LA GUAJIRA — Inventory Dashboard")
st.caption(f"Wayuu Chinchorros & Mochilas • {pd.Timestamp.now().strftime('%b %d, %Y')}")

c1,c2,c3,c4 = st.columns(4)
c1.metric("TOTAL UNITS", f"{df['Stock'].sum():,}", "8.2% vs last month")
c2.metric("OUT OF STOCK", f"{len(df[df['Stock']==0])}", "-3 items", delta_color="inverse")
c3.metric("LOW STOCK", f"{len(df[df['Stock']<=df['Minimo']])}", "Below threshold")
c4.metric("INVENTORY VALUE", f"${df['Valor'].sum():,.0f}", "5.4% vs last month")

st.write("")
col_izq, col_der = st.columns([1.3,1])

with col_izq:
    st.markdown('<div class="card"><b>Stock by Product Category</b>', unsafe_allow_html=True)
    st.bar_chart(df.groupby("Categoría")["Stock"].sum())
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="card"><b>Low Stock Alerts</b><br>Requires attention</div>', unsafe_allow_html=True)
    def sem(s,m):
        if s==0: return "🔴 Out of Stock"
        if s<=m: return "🟡 Low Stock"
        return "🟢 In Stock"
    df["Status"] = df.apply(lambda r: sem(r["Stock"], r["Minimo"]), axis=1)
    st.dataframe(df[["Nombre","Categoría","Stock","Status"]], hide_index=True, use_container_width=True)

st.markdown("---")
st.subheader("Recomendación de compra")
bajo = df[df["Stock"]<=df["Minimo"]].copy()
bajo["Reponer"] = bajo["Minimo"]*2 - bajo["Stock"]
st.dataframe(bajo[["SKU","Nombre","Stock","Minimo","Reponer"]], use_container_width=True)

# FORMULARIO BONITO
with st.form("add"):
    st.write("➕ Carga de productos - Nombre, SKU, Categoría, Precio, Cantidad")
    a,b,c,d,e = st.columns(5)
    sku=a.text_input("SKU"); nom=b.text_input("Nombre"); cat=c.selectbox("Categoría",["Chinchorros","Mochilas","Accesorios","Mantas"]); pre=d.number_input("Precio",0); sto=e.number_input("Cantidad",0)
    if st.form_submit_button("Guardar"):
        st.session_state.df.loc[len(df)]=[sku,nom,cat,pre,0,sto,10,0]
        st.rerun()
