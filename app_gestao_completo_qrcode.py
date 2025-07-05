
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Gestão de Equipamentos", layout="wide")
st.title("🛠️ Gestão Completa de Equipamentos com QR Code")

# ---- CONFIGURAÇÕES ----
LOG_DIR = "logs_qrcode_streamlit"
DB_FILE = "Equipment.xlsx"
os.makedirs(LOG_DIR, exist_ok=True)

# ---- CARREGAR BASE DE DADOS ----
if os.path.exists(DB_FILE):
    df_db = pd.read_excel(DB_FILE)
else:
    df_db = pd.DataFrame(columns=[
        'Applicable for', 'Status', 'Equipment number', 'Description',
        'product', 'Model / type number', 'Measuring range',
        'Calibration performer', 'Physical location', 'Deadline'
    ])

# ---- LEITURA DE QR CODE VIA LINK ----
query_params = st.experimental_get_query_params()
equipamento_url = query_params.get("equipment", [None])[0]

st.sidebar.header("🔐 Operador")
operador = st.sidebar.text_input("Digite seu nome:")

aba = st.sidebar.radio("Navegar para:", ["Registro via QR Code", "Consulta de Equipamentos", "Novo Cadastro"])

# ==== ABA 1: REGISTRO VIA QR CODE ====
if aba == "Registro via QR Code":
    st.subheader("📥 Registro de Equipamentos Escaneados (QR Code)")
    if operador:
        data = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M:%S")
        log_file = os.path.join(LOG_DIR, f"log_{data}.xlsx")

        qr_input = st.text_input("📸 Escaneie ou cole o link do QR Code:", value=equipamento_url or "")

        if st.button("Registrar leitura"):
            if qr_input:
                if "#Equipment=" in qr_input:
                    equipamento = qr_input.split("#Equipment=")[-1]
                elif "equipment=" in qr_input:
                    equipamento = qr_input.split("equipment=")[-1]
                else:
                    equipamento = qr_input.strip()

                registro = {
                    "Data": data,
                    "Hora": hora,
                    "Operador": operador,
                    "Equipment number": equipamento,
                    "Link escaneado": qr_input
                }

                if os.path.exists(log_file):
                    df_existente = pd.read_excel(log_file)
                    df = pd.concat([df_existente, pd.DataFrame([registro])], ignore_index=True)
                else:
                    df = pd.DataFrame([registro])

                df.to_excel(log_file, index=False)
                st.success(f"✔ Equipamento {equipamento} registrado!")
            else:
                st.warning("Por favor, escaneie ou insira o link.")

        if os.path.exists(log_file):
            df_log = pd.read_excel(log_file)
            df_operador = df_log[df_log["Operador"] == operador]
            st.markdown("### 📋 Equipamentos escaneados hoje")
            st.dataframe(df_operador)

            csv = df_operador.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Baixar lista do dia", data=csv,
                            file_name=f"registro_{operador}_{data}.csv", mime="text/csv")

        st.markdown("### 🔍 Buscar em todos os registros do dia")
        busca = st.text_input("Buscar por equipamento, operador ou link:")
        if busca and os.path.exists(log_file):
            df_busca = pd.read_excel(log_file)
            filtro = df_busca.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
            resultados = df_busca[filtro]
            st.dataframe(resultados)
    else:
        st.info("Digite seu nome na barra lateral para iniciar.")

# ==== ABA 2: CONSULTA DE EQUIPAMENTOS ====
elif aba == "Consulta de Equipamentos":
    st.subheader("🔍 Consulta por Coluna na Base de Equipamentos")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        f_applicable = st.text_input("Applicable for")
    with col2:
        f_status = st.text_input("Status")
    with col3:
        f_eq_number = st.text_input("Equipment number")

    with col4:
        f_description = st.text_input("Description")
    with col5:
        f_model = st.text_input("Model / type number")
    with col6:
        f_location = st.text_input("Physical location")

    df_filtro = df_db.copy()
    if f_applicable:
        df_filtro = df_filtro[df_filtro['Applicable for'].astype(str).str.contains(f_applicable, case=False)]
    if f_status:
        df_filtro = df_filtro[df_filtro['Status'].astype(str).str.contains(f_status, case=False)]
    if f_eq_number:
        df_filtro = df_filtro[df_filtro['Equipment number'].astype(str).str.contains(f_eq_number, case=False)]
    if f_description:
        df_filtro = df_filtro[df_filtro['Description'].astype(str).str.contains(f_description, case=False)]
    if f_model:
        df_filtro = df_filtro[df_filtro['Model / type number'].astype(str).str.contains(f_model, case=False)]
    if f_location:
        df_filtro = df_filtro[df_filtro['Physical location'].astype(str).str.contains(f_location, case=False)]

    st.write(f"🔎 {len(df_filtro)} resultado(s) encontrado(s).")
    st.dataframe(df_filtro)

    csv = df_filtro.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar resultados filtrados", data=csv,
                       file_name="equipamentos_filtrados.csv", mime="text/csv")

# ==== ABA 3: NOVO CADASTRO ====
elif aba == "Novo Cadastro":
    st.subheader("➕ Cadastrar Novo Equipamento na Base")

    with st.form("novo_equipamento"):
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3)

        applicable = c1.text_input("Applicable for")
        status = c2.text_input("Status")
        eq_number = c3.text_input("Equipment number")
        description = c4.text_input("Description")
        product = c5.text_input("Product")
        model = c6.text_input("Model / type number")

        c7, c8, c9 = st.columns(3)
        range_ = c7.text_input("Measuring range")
        performer = c8.text_input("Calibration performer")
        location = c9.text_input("Physical location")
        deadline = st.date_input("Deadline")

        submitted = st.form_submit_button("Salvar equipamento")

        if submitted:
            novo = {
                'Applicable for': applicable,
                'Status': status,
                'Equipment number': eq_number,
                'Description': description,
                'product': product,
                'Model / type number': model,
                'Measuring range': range_,
                'Calibration performer': performer,
                'Physical location': location,
                'Deadline': deadline
            }
            df_db = pd.concat([df_db, pd.DataFrame([novo])], ignore_index=True)
            df_db.to_excel(DB_FILE, index=False)
            st.success(f"Equipamento {eq_number} cadastrado com sucesso!")
