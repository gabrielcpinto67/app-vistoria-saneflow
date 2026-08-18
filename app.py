import streamlit as st
from datetime import date, datetime
import json
import base64
import requests
import gspread
from google.oauth2.service_account import Credentials

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
    foto_cadastro = st.file_uploader("Anexe fotos da fachada", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    
with tab2:
    st.header("2. Extravasor (Hidráulica e Civil)")
    
    # --- NOVIDADE AQUI: DESTINO DO ESGOTO ---
    destino_esgoto = st.text_input("Para onde o esgoto é escoado?", help="Ex: Rio, Galeria pluvial, Terreno baldio, etc.")
    
    tipo_extravasor = st.selectbox("Tipo de estrutura", ["Selecione...", "Vertedor", "Tubo", "Canal", "Caixa", "Outro", "N/A"])
    if tipo_extravasor == "Outro": tipo_extravasor = st.text_input("Qual o tipo de estrutura?")

    col1, col2 = st.columns(2)
    with col1:
        diametro_largura = st.number_input("Diâmetro/Largura (m)", min_value=0.0, format="%.2f")
        # Ajustei o min_value para 0.01 para não dar erro de divisão por zero no cálculo
        comprimento = st.number_input("Comprimento (m)", min_value=0.01, format="%.2f") 
        # --- NOVIDADE AQUI: COTA DE ENTRADA ---
        cota_entrada = st.number_input("Cota de Entrada (m)", value=0.00, format="%.2f") 
    with col2:
        altura_soleira = st.number_input("Altura de Soleira (m)", min_value=0.0, format="%.2f")
        cota_soleira = st.number_input("Cota da soleira", min_value=0.0, format="%.2f")
        # --- NOVIDADE AQUI: COTA DE SAÍDA ---
        cota_saida = st.number_input("Cota de Saída (m)", value=0.00, format="%.2f")

    # --- NOVIDADE AQUI: CÁLCULO DE INCLINAÇÃO ---
    st.markdown("---")
    st.subheader("📐 Cálculo de Inclinação (Automático)")
    desnivel = cota_entrada - cota_saida
    inclinacao_percentual = (desnivel / comprimento) * 100

    if desnivel > 0:
        st.success(f"Desnível: **{desnivel:.2f} m** | Inclinação: **{inclinacao_percentual:.2f}%**")
    elif desnivel < 0:
        st.error(f"⚠️ Atenção: A cota de saída está MAIOR que a de entrada (Contra-declive). Desnível: {desnivel:.2f} m")
    else:
        st.info("Nenhum desnível detectado (Nivelado).")
    st.markdown("---")
        
    estado_conservacao = st.selectbox("Estado de conservação", ["Bom", "Regular", "Ruim", "Outro"])
    if estado_conservacao == "Outro": estado_conservacao = st.text_input("Descreva o estado:")
        
    regime_escoamento = st.radio("Regime de escoamento", ["Livre", "Afogado", "Outro"])
    if regime_escoamento == "Outro": regime_escoamento = st.text_input("Descreva o regime:")
        
    obs_extravasor = st.text_area("Presença de sólidos, gordura, assoreamento ou maré:")
    st.subheader("📸 Fotos Obrigatórias (Extravasor)")
    foto_extravasor = st.file_uploader("Anexe fotos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="f_ext")

with tab3:
    st.header("3. Regime Operacional")
    col3, col4, col5 = st.columns(3)
    with col3: vazao_min = st.number_input("Vazão Mín. (L/s)", min_value=0.0)
    with col4: vazao_med = st.number_input("Vazão Méd. (L/s)", min_value=0.0)
    with col5: vazao_max = st.number_input("Vazão Máx. (L/s)", min_value=0.0)
    
    hist_extravasamento = st.text_area("Histórico, frequência e duração dos extravasamentos")
    bombas = st.text_input("Nº e potência das bombas (ex: 2x 15cv)")
    niveis_poco = st.text_input("Níveis de partida/parada e volume do poço")
    st.subheader("📸 Evidências Operacionais")
    foto_operacional = st.file_uploader("Anexe fotos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="f_ope")

with tab4:
    st.header("4. Infraestrutura Elétrica")
    energia_disp = st.radio("Disponibilidade de energia junto ao ponto?", ["Sim", "Não", "Parcial", "Outro"])
    if energia_disp == "Outro": energia_disp = st.text_input("Descreva a disponibilidade:")
        
    distancia_qgbt = st.number_input("Distância ao QGBT (metros)", min_value=0.0)
    tensao = st.selectbox("Tensão disponível", ["110V", "220V", "380V", "440V", "N/A", "Outra"])
    if tensao == "Outra": tensao = st.text_input("Qual a tensão?")
        
    necessidade_energia = st.multiselect("Necessidades", ["Alimentação dedicada", "No-break", "Painel Solar", "Aterramento/DPS", "Outra"])
    if "Outra" in necessidade_energia: nec_outra = st.text_input("Qual outra?")
    st.subheader("📸 Fotos do Painel Elétrico")
    foto_eletrica = st.file_uploader("Anexe fotos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="f_ele")

with tab5:
    st.header("5. Automação e Telemetria")
    clp_existente = st.text_input("Existência de CLP/RTU/SCADA (Marca/Modelo)")
    telemetria = st.selectbox("Telemetria", ["Nenhuma", "Celular (3G/4G)", "Rádio", "Fibra Óptica", "Outra"])
    if telemetria == "Outra": telemetria = st.text_input("Descreva a telemetria:")
        
    sinal = st.slider("Qualidade do Sinal (0=Sem sinal, 10=Excelente)", 0, 10, 5)
    pontos_io = st.text_input("Pontos de I/O disponíveis")
    st.subheader("📸 Fotos da Automação")
    foto_automacao = st.file_uploader("Anexe fotos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="f_aut")

with tab6:
    st.header("6. Acessibilidade e Segurança")
    acesso = st.multiselect("Condições de acesso", ["Espaço Confinado", "Trabalho em Altura", "Uso de Escadas", "Acesso Livre", "Outra"])
    if "Outra" in acesso: acesso_outro = st.text_input("Qual outra condição?")
        
    riscos = st.text_area("Riscos presentes e EPIs necessários:")
    vulnerabilidade = st.checkbox("Exposição a alagamento, intempéries ou vandalismo?")
    st.subheader("📸 Fotos de Segurança")
    foto_seguranca = st.file_uploader("Anexe fotos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="f_seg")

with tab7:
    st.header("7. Documentação e Fechamento")
    as_built = st.checkbox("Projeto as-built / cadastro GIS conferido no local?")
    pendencias = st.text_area("Pendências e observações finais:")
    st.subheader("📸 Documentos de Campo")
    foto_doc = st.file_uploader("Anexe fotos de croquis", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key="f_doc")
    
    st.markdown("---")
    
    if st.button("💾 ENVIAR DADOS DA VISTORIA", use_container_width=True):
        if eee_selecionada == "Selecione...":
            st.error("Por favor, selecione a EEE na Aba 1 antes de salvar.")
        else:
            with st.spinner('Criando pastas, convertendo imagens e enviando dados...'):
                try:
                    URL_APPS_SCRIPT = st.secrets["url_script"]
                    id_pasta_mae = "1lVPOzLMM4lq_qL89CqjKMsUNtHMgp3uq"

                    # 1. Pede para o Google Script criar a pasta (com lógica inteligente)
                    nome_base = f"{eee_selecionada} - {data_vistoria.strftime('%d-%m-%Y')}"
                    payload_pasta = {
                        "action": "create_folder",
                        "parentFolderId": id_pasta_mae,
                        "baseName": nome_base
                    }
                    resp_pasta = requests.post(URL_APPS_SCRIPT, json=payload_pasta).json()
                    
                    id_nova_pasta = resp_pasta["folderId"]
                    link_pasta = resp_pasta["folderLink"]
                    nome_pasta = resp_pasta["folderName"]

                    # 2. Função para subir as fotos via Google Script
                    def subir_fotos(lista_arquivos, prefixo):
                        if not lista_arquivos: return "Nenhuma foto anexada"
                        links = []
                        for i, arquivo in enumerate(lista_arquivos):
                            nome_arquivo = f"{prefixo}_{i+1}_{arquivo.name}"
                            encoded_string = base64.b64encode(arquivo.getvalue()).decode("utf-8")
                            
                            payload_foto = {
                                "action": "upload_file",
                                "folderId": id_nova_pasta,
                                "filename": nome_arquivo,
                                "fileData": encoded_string,
                                "mimeType": arquivo.type
                            }
                            resp_foto = requests.post(URL_APPS_SCRIPT, json=payload_foto).json()
                            if resp_foto.get("status") == "success":
                                links.append(resp_foto["link"])
                            else:
                                links.append(f"Erro ao subir {nome_arquivo}")
                        
                        return "\n".join(links)

                    # Subindo todas as categorias
                    link_f_gerais = subir_fotos(foto_cadastro, "1_Gerais")
                    link_f_ext = subir_fotos(foto_extravasor, "2_Extravasor")
                    link_f_ope = subir_fotos(foto_operacional, "3_Operacional")
                    link_f_ele = subir_fotos(foto_eletrica, "4_Eletrica")
                    link_f_aut = subir_fotos(foto_automacao, "5_Automacao")
                    link_f_seg = subir_fotos(foto_seguranca, "6_Seguranca")
                    link_f_doc = subir_fotos(foto_doc, "7_Documentos")

                    # 3. Conecta ao Sheets e salva
                    credenciais_json = json.loads(st.secrets["google_json"])
                    escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                    credenciais = Credentials.from_service_account_info(credenciais_json, scopes=escopos)
                    
                    conta_robo_planilha = gspread.authorize(credenciais)
                    planilha = conta_robo_planilha.open("Base_Dados_Vistorias_App")
                    aba_master = planilha.worksheet("Base_Master")
                    
                    # --- ATENÇÃO AQUI: ADICIONEI AS 4 NOVAS VARIÁVEIS NESTA LISTA ---
                    dados = [
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"), eee_selecionada, data_vistoria.strftime("%d/%m/%Y"), 
                        responsavel, coordenadas, sub_bacia, link_f_gerais, 
                        destino_esgoto, # <--- ADICIONADO AQUI
                        tipo_extravasor, diametro_largura, comprimento, 
                        cota_entrada, cota_saida, inclinacao_percentual, # <--- ADICIONADOS AQUI
                        altura_soleira, cota_soleira, estado_conservacao, regime_escoamento, obs_extravasor, link_f_ext, 
                        vazao_min, vazao_med, vazao_max, hist_extravasamento, bombas, niveis_poco, link_f_ope, 
                        energia_disp, distancia_qgbt, tensao, ", ".join(necessidade_energia), link_f_ele, 
                        clp_existente, telemetria, sinal, pontos_io, link_f_aut, ", ".join(acesso), riscos, 
                        "Sim" if vulnerabilidade else "Não", link_f_seg, "Sim" if as_built else "Não", 
                        pendencias, link_f_doc, "Gerar na próxima fase", link_pasta
                    ]
                    
                    aba_master.append_row(dados)
                    st.success(f"✅ Vistoria da unidade {eee_selecionada} salva! A pasta '{nome_pasta}' foi criada com sucesso.")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Erro interno do sistema: {e}")
