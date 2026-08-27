import streamlit as st
from datetime import date, datetime
import json
import base64
import requests
import gspread
from google.oauth2.service_account import Credentials
from streamlit_geolocation import streamlit_geolocation

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
    responsavel = st.text_input("Nosso Responsável (Saneflow) *")
    operador_igua = st.text_input("Operador da Iguá (Acompanhante)")
    
    qtd_extravasores = st.number_input("Nº de extravasores nesta EEE *", min_value=1, max_value=10, value=1, step=1)
    
    st.markdown("---")
    st.subheader("📍 Coordenadas GPS *")
    st.write("Clique para capturar a localização exata do celular:")
    localizacao = streamlit_geolocation()
    lat, lon = "", ""
    if localizacao and localizacao.get('latitude'):
        lat = str(localizacao.get('latitude'))
        lon = str(localizacao.get('longitude'))
        st.success(f"Capturado: Lat {lat} / Long {lon}")
    else:
        st.warning("Aguardando captura do GPS...")
        
    coordenadas = f"{lat}, {lon}" if lat else ""
    
    sub_bacia = st.text_input("Sub-bacia")
    st.subheader("📸 Fotos Gerais")
    foto_cadastro = st.file_uploader("Anexe fotos da fachada", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab2:
    st.header("2. Extravasor (Hidráulica e Civil)")
    st.info(f"Preencha as características para os {qtd_extravasores} extravasor(es) informados.")
    
    for i in range(qtd_extravasores):
        with st.expander(f"🔹 DADOS DO EXTRAVASOR {i+1}", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.selectbox("Localização *", ["Selecione...", "Poço de sucção", "Câmara de chegada", "By-pass", "Após reservatório de acumulação"], key=f"loc_{i}")
                st.selectbox("Regime *", ["Selecione...", "Livre", "Afogado", "Intermitente"], key=f"regime_{i}")
                st.selectbox("Material", ["Concreto", "Alvenaria", "PVC", "Outros"], key=f"mat_{i}")
            with col_b:
                dest = st.selectbox("Destino do esgoto *", ["Selecione...", "Lagoa", "Canal", "Mar/Orla", "Galeria de drenagem", "Outro"], key=f"dest_{i}")
                if dest == "Outro":
                    st.text_input("Qual o outro destino?", key=f"dest_outro_{i}")
                st.checkbox("Área ambientalmente sensível?", key=f"sensivel_{i}")

            col_c, col_d, col_e = st.columns(3)
            with col_c: st.radio("Válvula Flap?", ["Sim", "Não"], key=f"flap_{i}")
            with col_d: st.radio("Gradeamento antes?", ["Sim", "Não"], key=f"grade_{i}")
            with col_e: st.radio("Trecho reto p/ medidor?", ["Sim", "Não", "Talvez"], key=f"reto_{i}")

            col_f, col_g = st.columns(2)
            with col_f:
                mare = st.radio("Influência de maré/nível?", ["Sim", "Não"], key=f"mare_{i}")
                if mare == "Sim":
                    st.number_input("Cota de nível máx (m)", value=0.0, format="%.2f", key=f"cota_mare_{i}")
            with col_g:
                st.selectbox("Formato", ["Vertedor", "Tubo", "Canal", "Caixa", "Outro"], key=f"formato_{i}")
                st.number_input("Dimensão (m)", min_value=0.0, format="%.2f", key=f"dim_{i}")

            st.markdown("**Níveis e Inclinação**")
            col_h, col_i, col_j = st.columns(3)
            with col_h: st.number_input("Entrada (m)", value=0.0, format="%.2f", key=f"cota_ent_{i}") 
            with col_i: st.number_input("Saída (m)", value=0.0, format="%.2f", key=f"cota_sai_{i}")
            with col_j: st.number_input("Comprimento (m)", value=1.0, min_value=0.01, format="%.2f", key=f"comp_{i}")
            
            st.file_uploader(f"📸 Fotos Obrigatórias (Ext. {i+1})", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'], key=f"f_ext_{i}")

with tab3:
    st.header("3. Regime Operacional")
    
    st.markdown("**Histórico de Extravasamentos (Por ponto)**")
    for i in range(qtd_extravasores):
        st.markdown(f"*Extravasor {i+1}:*")
        st.multiselect("Causas prováveis", ["Falta de energia", "Falha de bomba", "Chuva", "Maré", "Entupimento"], key=f"causa_{i}")
        col_k, col_l = st.columns(2)
        with col_k: st.number_input("Frequência (Eventos/mês)", min_value=0, value=0, key=f"freq_{i}")
        with col_l:
            medidor = st.radio("Medidor de extravasamento existente?", ["Sim", "Não"], key=f"medidor_exist_{i}")
            if medidor == "Sim": st.text_input("Qual medidor?", key=f"qual_med_{i}")
    
    st.markdown("---")
    st.markdown("**Operação Geral da EEE**")
    scada_hist = st.radio("SCADA possui histórico de horas de operação/partidas?", ["Sim", "Não", "Não sei informar"])
    
    col3, col4, col5 = st.columns(3)
    with col3: vazao_min = st.number_input("Vazão Mín. (L/s)", min_value=0.0)
    with col4: vazao_med = st.number_input("Vazão Méd. (L/s)", min_value=0.0)
    with col5: vazao_max = st.number_input("Vazão Máx. (L/s)", min_value=0.0)
    
    bombas = st.text_input("Nº e potência das bombas (ex: 2x 15cv)")
    niveis_poco = st.text_input("Níveis de partida/parada e volume do poço")
    foto_operacional = st.file_uploader("📸 Evidências Operacionais", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab4:
    st.header("4. Infraestrutura Elétrica")
    energia_disp = st.selectbox("Energia no ponto? *", ["Selecione...", "Sim", "Não", "Parcial"])
    gerador = st.selectbox("Possui Gerador / No-break? *", ["Selecione...", "Sim - Gerador", "Sim - No-break", "Não possui"])
    aterramento = st.selectbox("Aterramento adequado?", ["Sim", "Não", "Não sei avaliar"])
    quedas = st.radio("Quedas de energia frequentes?", ["Sim", "Não", "Desconhecido"])
    solar = st.selectbox("Viabilidade p/ energia solar?", ["Sim", "Não", "Talvez"])
    
    distancia_qgbt = st.number_input("Distância ao QGBT (metros)", min_value=0.0)
    tensao = st.selectbox("Tensão disponível", ["110V", "220V", "380V", "440V", "N/A"])
    necessidade_energia = st.multiselect("Outras necessidades", ["Alimentação dedicada", "Aterramento/DPS", "Outra"])
    foto_eletrica = st.file_uploader("📸 Fotos do Painel Elétrico", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab5:
    st.header("5. Automação e Telemetria")
    clp_existente = st.text_input("Existência de CLP/RTU/SCADA (Marca/Modelo)")
    ligado_cco = st.radio("A EEE já é monitorada no CCO?", ["Sim", "Não"])
    telemetria = st.selectbox("Meio de Comunicação", ["Nenhuma", "Celular (3G/4G)", "Rádio", "Fibra Óptica"])
    protocolo = st.selectbox("Protocolo", ["Nenhum", "Modbus", "DNP3", "OPC", "MQTT", "Outro"])
    sinal_tipo = st.selectbox("Tipo de sinal suportado", ["4-20 mA", "Digital", "Ambos", "N/A"])
    sinal = st.slider("Qualidade do Sinal 3G/4G (0 a 10)", 0, 10, 5)
    pontos_io = st.text_input("Pontos de I/O disponíveis")
    foto_automacao = st.file_uploader("📸 Fotos da Automação", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab6:
    st.header("6. Acessibilidade e Segurança")
    espaco_confinado = st.radio("É Espaço Confinado (Exige NR)?", ["Sim", "Não"])
    gas_h2s = st.radio("Presença de Gás H2S perceptível?", ["Sim", "Não"])
    comunidade = st.radio("Localizada em área de comunidade?", ["Sim", "Não"])
    
    st.write("Vulnerabilidades do local:")
    risco_alagamento = st.checkbox("Risco de Alagamento")
    risco_intemperie = st.checkbox("Exposição a Intempéries (Sol/Chuva direto)")
    risco_vandalismo = st.checkbox("Risco Alto de Vandalismo / Furto")
    
    riscos_outros = st.text_area("Outros Riscos presentes e EPIs:")
    foto_seguranca = st.file_uploader("📸 Fotos de Segurança", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab7:
    st.header("7. Documentação e Fechamento")
    sugestao_tec = st.selectbox("Sugestão da Tecnologia (Opcional)", ["Deixar em branco", "Radar", "Ultrassônico", "Pressão (Nível)", "Inclinômetro (Flap)"])
    as_built = st.checkbox("Projeto as-built conferido no local?")
    pendencias = st.text_area("Pendências e observações finais:")
    foto_doc = st.file_uploader("📸 Anexe croquis", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    
    st.markdown("---")
    
    if st.button("💾 ENVIAR DADOS DA VISTORIA", use_container_width=True):
        if eee_selecionada == "Selecione..." or not lat or energia_disp == "Selecione..." or gerador == "Selecione...":
            st.error("Preencha todos os campos obrigatórios (EEE, GPS, Energia e Gerador).")
        else:
            with st.spinner('Consolidando dados, subindo fotos e enviando para o Sheets...'):
                try:
                    URL_APPS_SCRIPT = st.secrets["url_script"]
                    id_pasta_mae = "1lVPOzLMM4lq_qL89CqjKMsUNtHMgp3uq"
                    nome_base = f"{eee_selecionada} - {data_vistoria.strftime('%d-%m-%Y')}"
                    
                    # 1. Cria a pasta no Drive
                    payload_pasta = {"action": "create_folder", "parentFolderId": id_pasta_mae, "baseName": nome_base}
                    resp_pasta = requests.post(URL_APPS_SCRIPT, json=payload_pasta).json()
                    id_nova_pasta = resp_pasta["folderId"]
                    link_pasta = resp_pasta["folderLink"]

                    # Função para subir as fotos
                    def subir_fotos(lista_arquivos, prefixo):
                        if not lista_arquivos: return "Sem foto"
                        links = []
                        for i, arquivo in enumerate(lista_arquivos):
                            nome_arquivo = f"{prefixo}_{i+1}_{arquivo.name}"
                            encoded_string = base64.b64encode(arquivo.getvalue()).decode("utf-8")
                            payload_foto = {"action": "upload_file", "folderId": id_nova_pasta, "filename": nome_arquivo, "fileData": encoded_string, "mimeType": arquivo.type}
                            resp_foto = requests.post(URL_APPS_SCRIPT, json=payload_foto).json()
                            if resp_foto.get("status") == "success": links.append(resp_foto["link"])
                        return "\n".join(links)

                    # Subindo fotos estáticas
                    l_cad = subir_fotos(foto_cadastro, "1_Gerais")
                    l_ope = subir_fotos(foto_operacional, "3_Oper")
                    l_ele = subir_fotos(foto_eletrica, "4_Eletrica")
                    l_aut = subir_fotos(foto_automacao, "5_Automacao")
                    l_seg = subir_fotos(foto_seguranca, "6_Seguranca")
                    l_doc = subir_fotos(foto_doc, "7_Doc")

                    # Compilando dados dos múltiplos extravasores em Texto para o Sheets
                    dados_extravasores_compilados = ""
                    links_fotos_extravasores = []
                    
                    for i in range(qtd_extravasores):
                        # Pega os dados armazenados na memória (session_state) do Streamlit
                        d = st.session_state
                        dest_final = d[f'dest_outro_{i}'] if d[f'dest_{i}'] == "Outro" else d[f'dest_{i}']
                        inclinacao = ((d[f'cota_ent_{i}'] - d[f'cota_sai_{i}']) / d[f'comp_{i}']) * 100
                        
                        bloco = f"""--- PONTO {i+1} ---
Local: {d[f'loc_{i}']} | Regime: {d[f'regime_{i}']}
Destino: {dest_final} | Amb. Sensível: {d[f'sensivel_{i}']}
Material: {d[f'mat_{i}']} | Formato: {d[f'formato_{i}']} | Dim: {d[f'dim_{i}']}m
Flap: {d[f'flap_{i}']} | Grade: {d[f'grade_{i}']} | Trecho Reto: {d[f'reto_{i}']}
Inclinação: {inclinacao:.2f}% (Ent: {d[f'cota_ent_{i}']}, Sai: {d[f'cota_sai_{i}']}, Comp: {d[f'comp_{i}']})
Maré: {d[f'mare_{i}']}
Causas: {', '.join(d[f'causa_{i}'])} | Freq: {d[f'freq_{i}']} ev/mês | Medidor: {d[f'medidor_exist_{i}']}"""
                        dados_extravasores_compilados += bloco + "\n\n"
                        
                        # Sobe as fotos do Extravasor atual
                        fotos_deste_ext = d.get(f'f_ext_{i}')
                        links_fotos_extravasores.append(f"EXT {i+1}: " + subir_fotos(fotos_deste_ext, f"2_Ext_{i+1}"))

                    link_f_ext_todas = "\n".join(links_fotos_extravasores)

                    # 3. Conecta ao Sheets e salva
                    credenciais_json = json.loads(st.secrets["google_json"])
                    escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                    credenciais = Credentials.from_service_account_info(credenciais_json, scopes=escopos)
                    
                    conta_robo_planilha = gspread.authorize(credenciais)
                    planilha = conta_robo_planilha.open("Base_Dados_Vistorias_App")
                    aba_master = planilha.worksheet("Base_Master")
                    
                    dados = [
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"), eee_selecionada, data_vistoria.strftime("%d/%m/%Y"), 
                        responsavel, operador_igua, coordenadas, sub_bacia, l_cad, 
                        qtd_extravasores, dados_extravasores_compilados, link_f_ext_todas,
                        scada_hist, vazao_min, vazao_med, vazao_max, bombas, niveis_poco, l_ope, 
                        energia_disp, gerador, aterramento, quedas, solar, distancia_qgbt, tensao, ", ".join(necessidade_energia), l_ele, 
                        clp_existente, ligado_cco, telemetria, protocolo, sinal_tipo, sinal, pontos_io, l_aut, 
                        espaco_confinado, gas_h2s, comunidade, risco_alagamento, risco_intemperie, risco_vandalismo, riscos_outros, l_seg, 
                        sugestao_tec, as_built, pendencias, l_doc, link_pasta
                    ]
                    
                    aba_master.append_row(dados)
                    st.success(f"✅ Vistoria salva! Pasta criada no Drive.")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Erro interno do sistema: {e}")
