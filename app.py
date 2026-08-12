import streamlit as st
from datetime import date

st.set_page_config(page_title="Vistoria EEE - Saneflow", page_icon="💧", layout="centered")

# --- TELA DE LOGIN ---
senha_digitada = st.text_input("🔑 Digite a senha da equipe para acessar:", type="password")

if senha_digitada != "SANEFLOW2026":
    st.warning("Aguardando senha correta...")
    st.stop()
# ---------------------

st.title("💧 Vistoria Técnica - EEEs")
st.markdown("**Saneflow Engenharia** | Preencha os dados em campo. Campos com * são obrigatórios.")

lista_eees = [
    "Jacarepaguá (JPA)", "Itanhangá", "Amil", "Olímpica", "Taquara V", 
    "Jardim Clarice", "Rio das Pedras II", "Quintas do Rio", "Barra Bonita", "Henfil", 
    "Recreio", "Marapendi", "Camara Cascudo II", "Rio das Pedras I", "Bandeirantes", 
    "Jardim Oceânico I", "César Morani", "Barrinha", "Jarbas de Carvalho", "Clóvis Salgado", 
    "Vila dos Atletas", "Chico Mendes", "Canal das Taxas", "Alvorada", "Anil", 
    "Beira Rio I", "Beira Rio II", "Benvindo de Novaes", "Cascatinha", "Centro Metropolitano", 
    "Curicica", "Eugênio Macedo", "Hermes de Lima", "Lagoa da Tijuca", "Mont Serrat I", 
    "Mont Serrat II", "Olof Palme", "Península", "Pontal Oceânico", "Santa América", 
    "Jose Duarte", "Vila da Amizade", "CTS Canal das Taxas", "Chico City"
]

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Cadastro", "2. Extravasor", "3. Operacional", 
    "4. Elétrica", "5. Automação", "6. Segurança", "7. Fechar"
])

with tab1:
    st.header("1. Identificação e cadastro da EEE")
    eee_selecionada = st.selectbox("Selecione a EEE *", ["Selecione..."] + lista_eees)
    data_vistoria = st.date_input("Data da Vistoria *", value=date.today())
    responsavel = st.text_input("Responsável pela Vistoria / Operacional *")
    coordenadas = st.text_input("Coordenadas GPS (Lat/Long)")
    sub_bacia = st.text_input("Sub-bacia e corpo receptor")
    
    st.subheader("📸 Fotos Gerais")
    foto_cadastro = st.file_uploader("Anexe fotos da fachada e visão geral", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_cad")
    
with tab2:
    st.header("2. Extravasor (Hidráulica e Civil)")
    
    tipo_extravasor = st.selectbox("Tipo de estrutura", ["Selecione...", "Vertedor", "Tubo", "Canal", "Caixa", "Outro", "N/A"])
    if tipo_extravasor == "Outro":
        tipo_extravasor = st.text_input("Qual o tipo de estrutura?")

    st.subheader("Dimensões Medidas")
    col1, col2 = st.columns(2)
    with col1:
        diametro_largura = st.number_input("Diâmetro/Largura (m)", min_value=0.0, format="%.2f")
        comprimento = st.number_input("Comprimento (m)", min_value=0.0, format="%.2f")
    with col2:
        altura_soleira = st.number_input("Altura de Soleira (m)", min_value=0.0, format="%.2f")
        cota_soleira = st.number_input("Cota da soleira", min_value=0.0, format="%.2f")
        
    estado_conservacao = st.selectbox("Estado de conservação", ["Bom", "Regular", "Ruim", "Outro"])
    if estado_conservacao == "Outro":
        estado_conservacao = st.text_input("Descreva o estado de conservação:")
        
    regime_escoamento = st.radio("Regime de escoamento", ["Livre", "Afogado", "Outro"])
    if regime_escoamento == "Outro":
        regime_escoamento = st.text_input("Descreva o regime de escoamento:")
        
    obs_extravasor = st.text_area("Presença de sólidos, gordura, assoreamento ou maré:")
    
    st.subheader("📸 Fotos Obrigatórias (Extravasor)")
    foto_extravasor = st.file_uploader("Anexe as fotos em múltiplos ângulos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_ext")

with tab3:
    st.header("3. Regime Operacional")
    col3, col4, col5 = st.columns(3)
    with col3:
        vazao_min = st.number_input("Vazão Mín. (L/s)", min_value=0.0)
    with col4:
        vazao_med = st.number_input("Vazão Méd. (L/s)", min_value=0.0)
    with col5:
        vazao_max = st.number_input("Vazão Máx. (L/s)", min_value=0.0)
    hist_extravasamento = st.text_area("Histórico, frequência e duração dos extravasamentos")
    bombas = st.text_input("Nº e potência das bombas (ex: 2x 15cv)")
    niveis_poco = st.text_input("Níveis de partida/parada e volume do poço")
    
    st.subheader("📸 Evidências Operacionais")
    foto_operacional = st.file_uploader("Anexe fotos das bombas e poço", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_ope")

with tab4:
    st.header("4. Infraestrutura Elétrica")
    
    energia_disp = st.radio("Disponibilidade de energia junto ao ponto?", ["Sim", "Não", "Parcial", "Outro"])
    if energia_disp == "Outro":
        energia_disp = st.text_input("Descreva a disponibilidade de energia:")
        
    distancia_qgbt = st.number_input("Distância ao QGBT (metros)", min_value=0.0)
    
    tensao = st.selectbox("Tensão disponível", ["110V", "220V", "380V", "440V", "N/A", "Outra"])
    if tensao == "Outra":
        tensao = st.text_input("Qual a tensão?")
        
    necessidade_energia = st.multiselect("Necessidades identificadas", ["Alimentação dedicada", "No-break", "Painel Solar", "Adequação de Aterramento/DPS", "Outra"])
    if "Outra" in necessidade_energia:
        nec_outra = st.text_input("Qual outra necessidade elétrica?")
    
    st.subheader("📸 Fotos do Painel Elétrico")
    foto_eletrica = st.file_uploader("Anexe fotos do QGBT e disjuntores", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_ele")

with tab5:
    st.header("5. Automação e Telemetria")
    clp_existente = st.text_input("Existência de CLP/RTU/SCADA (Marca/Modelo)")
    
    telemetria = st.selectbox("Telemetria existente", ["Nenhuma", "Celular (3G/4G)", "Rádio", "Fibra Óptica", "Outra"])
    if telemetria == "Outra":
        telemetria = st.text_input("Descreva a telemetria existente:")
        
    sinal = st.slider("Qualidade do Sinal (0=Sem sinal, 10=Excelente)", 0, 10, 5)
    pontos_io = st.text_input("Pontos de I/O disponíveis para integração")
    
    st.subheader("📸 Fotos da Automação")
    foto_automacao = st.file_uploader("Anexe fotos de CLPs e antenas", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_aut")

with tab6:
    st.header("6. Acessibilidade e Segurança")
    
    acesso = st.multiselect("Condições de acesso", ["Espaço Confinado", "Trabalho em Altura", "Uso de Escadas", "Acesso Livre", "Outra"])
    if "Outra" in acesso:
        acesso_outro = st.text_input("Qual outra condição de acesso?")
        
    riscos = st.text_area("Riscos presentes e EPIs necessários:")
    vulnerabilidade = st.checkbox("Exposição a alagamento, intempéries ou vandalismo?")
    
    st.subheader("📸 Fotos de Acessos e Riscos")
    foto_seguranca = st.file_uploader("Anexe fotos de restrições ou riscos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_seg")

with tab7:
    st.header("7. Documentação e Fechamento")
    as_built = st.checkbox("Projeto as-built / cadastro GIS conferido no local?")
    pendencias = st.text_area("Pendências e observações finais:")
    
    st.subheader("📸 Documentos de Campo")
    foto_doc = st.file_uploader("Anexe fotos de croquis desenhados em campo ou plantas", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="foto_doc")
    
    st.markdown("---")
    if st.button("💾 ENVIAR DADOS DA VISTORIA", use_container_width=True):
        if eee_selecionada == "Selecione...":
            st.error("Por favor, selecione a EEE na Aba 1 antes de salvar.")
        else:
            st.success(f"✅ Vistoria da unidade {eee_selecionada} processada com sucesso! (Modo de Teste)")
            st.info("A criação da planilha mestre, pasta de fotos e planilha individual será implementada na conexão com o Google.")
            st.balloons()
