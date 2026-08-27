import streamlit as st
from datetime import date, datetime
import json
import base64
import requests
import gspread
from google.oauth2.service_account import Credentials
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Vistoria EEE - Saneflow", page_icon="💧", layout="centered")

# --- MENSAGEM DE SUCESSO PÓS-RESET ---
if 'sucesso_envio' in st.session_state:
    st.success(st.session_state.sucesso_envio)
    del st.session_state.sucesso_envio

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
                loc_val = st.selectbox("Localização *", ["Selecione...", "Poço de sucção", "Câmara de chegada", "By-pass", "Após reservatório de acumulação", "Outro"], key=f"loc_{i}")
                if loc_val == "Outro": st.text_input("Qual localização?", key=f"loc_outro_{i}")
                
                regime_val = st.selectbox("Regime *", ["Selecione...", "Livre", "Afogado", "Intermitente", "Outro"], key=f"regime_{i}")
                if regime_val == "Outro": st.text_input("Qual regime?", key=f"regime_outro_{i}")
                
                mat_val = st.selectbox("Material", ["Concreto", "Alvenaria", "PVC", "Outro"], key=f"mat_{i}")
                if mat_val == "Outro": st.text_input("Qual material?", key=f"mat_outro_{i}")
                
            with col_b:
                dest_val = st.selectbox("Destino do esgoto *", ["Selecione...", "Lagoa", "Canal", "Mar/Orla", "Galeria de drenagem", "Outro"], key=f"dest_{i}")
                if dest_val == "Outro": st.text_input("Qual o outro destino?", key=f"dest_outro_{i}")
                
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
                formato_val = st.selectbox("Formato", ["Vertedor", "Tubo", "Canal", "Caixa", "Outro"], key=f"formato_{i}")
                if formato_val == "Outro": st.text_input("Qual formato?", key=f"formato_outro_{i}")
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
        
        causas = st.multiselect("Causas prováveis", ["Falta de energia", "Falha de bomba", "Chuva", "Maré", "Entupimento", "Outra"], key=f"causa_{i}")
        if "Outra" in causas:
            st.text_input("Especifique a outra causa:", key=f"causa_outro_{i}")
            
        col_k, col_l = st.columns(2)
        with col_k: st.number_input("Frequência (Eventos/mês)", min_value=0, value=0, key=f"freq_{i}")
        with col_l:
            medidor = st.radio("Medidor existente?", ["Sim", "Não"], key=f"medidor_exist_{i}")
            if medidor == "Sim": st.text_input("Qual medidor?", key=f"qual_med_{i}")
    
    st.markdown("---")
    st.markdown("**Operação Geral da EEE**")
    scada_hist = st.radio("SCADA possui histórico de horas de operação/partidas?", ["Sim", "Não", "A validar"])
    
    col3, col4, col5 = st.columns(3)
    with col3: vazao_min = st.number_input("Vazão Mín. (L/s)", min_value=0.0)
    with col4: vazao_med = st.number_input("Vazão Méd. (L/s)", min_value=0.0)
    with col5: vazao_max = st.number_input("Vazão Máx. (L/s)", min_value=0.0)
    
    bombas = st.text_input("Nº e potência das bombas (ex: 2x 15cv)")
    niveis_poco = st.text_input("Níveis de partida/parada e volume do poço")
    foto_operacional = st.file_uploader("📸 Evidências Operacionais", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab4:
    st.header("4. Infraestrutura Elétrica")
    energia_disp = st.selectbox("Energia no ponto? *", ["Selecione...", "Sim", "Não", "Parcial", "Outra"])
    if energia_disp == "Outra": energia_disp = st.text_input("Especifique a energia:")
        
    gerador = st.selectbox("Possui Gerador / No-break? *", ["Selecione...", "Sim - Gerador", "Sim - No-break", "Sim - Gerador e No-Brek", "Não possui", "Outro"])
    if gerador == "Outro": gerador = st.text_input("Especifique gerador/no-break:")
        
    aterramento = st.selectbox("Aterramento adequado?", ["Sim", "Não", "Outro"])
    if aterramento == "Outro": aterramento = st.text_input("Especifique o aterramento:")
        
    quedas = st.radio("Quedas de energia frequentes?", ["Sim", "Não", "Desconhecido"])
    solar = st.selectbox("Viabilidade p/ energia solar?", ["Sim", "Não", "Talvez"])
    
    distancia_qgbt = st.number_input("Distância ao QGBT (metros)", min_value=0.0)
    
    tensao = st.selectbox("Tensão disponível", ["110V", "220V", "380V", "440V", "N/A", "Outra"])
    if tensao == "Outra": tensao = st.text_input("Especifique a tensão:")
        
    necessidade_energia = st.multiselect("Outras necessidades", ["Alimentação dedicada", "Aterramento/DPS", "Outra"])
    if "Outra" in necessidade_energia: 
        nec_extra = st.text_input("Qual outra necessidade?")
        if nec_extra: necessidade_energia.append(nec_extra)
        
    foto_eletrica = st.file_uploader("📸 Fotos do Painel Elétrico", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

with tab5:
    st.header("5. Automação e Telemetria")
    clp_existente = st.text_input("Existência de CLP/RTU/SCADA (Marca/Modelo)")
    ligado_cco = st.radio("A EEE já é monitorada no CCO?", ["Sim", "Não"])
    
    telemetria = st.selectbox("Meio de Comunicação", ["Nenhuma", "Celular (3G/4G)", "Rádio", "Fibra Óptica", "Outro"])
    if telemetria == "Outro": telemetria = st.text_input("Especifique a comunicação:")
        
    protocolo = st.selectbox("Protocolo", ["Nenhum", "Modbus", "DNP3", "OPC", "MQTT", "Outro"])
    if protocolo == "Outro": protocolo = st.text_input("Especifique o protocolo:")
        
    sinal_tipo = st.selectbox("Tipo de sinal suportado", ["4-20 mA", "Digital", "Ambos", "N/A", "Outro"])
    if sinal_tipo == "Outro": sinal_tipo = st.text_input("Especifique o sinal:")
        
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
    sugestao_tec = st.selectbox("Sugestão da Tecnologia (Opcional)", ["Deixar em branco", "Radar", "Ultrassônico", "Pressão (Nível)", "Inclinômetro (Flap)", "Outra"])
    if sugestao_tec == "Outra": sugestao_tec = st.text_input("Especifique a tecnologia sugerida:")
        
    as_built = st.checkbox("Projeto as-built conferido no local?")
    pendencias = st.text_area("Pendências e observações finais:")
    foto_doc = st.file_uploader("📸 Anexe croquis", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    
    st.markdown("---")
    
    if st.button("💾 ENVIAR DADOS DA VISTORIA", use_container_width=True, type="primary"):
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

                    d = st.session_state
                    def resolve_outro(campo, indice):
                        valor = d.get(f'{campo}_{indice}')
                        return d.get(f'{campo}_outro_{indice}', valor) if valor == "Outro" else valor

                    # Lista que vai guardar todas as linhas a serem enviadas ao Excel
                    lista_de_linhas = []
                    
                    # --- LOOP PARA GERAR UMA LINHA DE EXCEL POR EXTRAVASOR ---
                    for i in range(qtd_extravasores):
                        ext_loc = resolve_outro('loc', i)
                        ext_reg = resolve_outro('regime', i)
                        ext_mat = resolve_outro('mat', i)
                        ext_dest = resolve_outro('dest', i)
                        ext_sensivel = "Sim" if d.get(f'sensivel_{i}') else "Não"
                        ext_flap = d.get(f'flap_{i}', '')
                        ext_grade = d.get(f'grade_{i}', '')
                        ext_reto = d.get(f'reto_{i}', '')
                        ext_mare = d.get(f'mare_{i}', '')
                        ext_cota_mare = d.get(f'cota_mare_{i}', 0.0) if ext_mare == "Sim" else "N/A"
                        ext_formato = resolve_outro('formato', i)
                        ext_dim = d.get(f'dim_{i}', 0.0)
                        ext_cota_ent = d.get(f'cota_ent_{i}', 0.0)
                        ext_cota_sai = d.get(f'cota_sai_{i}', 0.0)
                        ext_comp = d.get(f'comp_{i}', 1.0)
                        ext_incl = ((ext_cota_ent - ext_cota_sai) / ext_comp) * 100 if ext_comp > 0 else 0
                        
                        # Tratamento da lista de Causas para inserir o "Outra"
                        lista_causas = d.get(f'causa_{i}', []).copy()
                        if "Outra" in lista_causas:
                            causa_extra = d.get(f'causa_outro_{i}', '')
                            if causa_extra:
                                lista_causas[lista_causas.index("Outra")] = causa_extra
                        ext_causas = ", ".join(lista_causas)
                        
                        ext_freq = d.get(f'freq_{i}', 0)
                        ext_medidor_exist = d.get(f'medidor_exist_{i}', 'Não')
                        ext_medidor = d.get(f'qual_med_{i}', '') if ext_medidor_exist == "Sim" else "Não"
                        
                        ext_foto = subir_fotos(d.get(f'f_ext_{i}'), f"2_Ext_{i+1}")

                        linha = [
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"), eee_selecionada, data_vistoria.strftime("%d/%m/%Y"), 
                            responsavel, operador_igua, coordenadas, sub_bacia, l_cad, 
                            qtd_extravasores, 
                            
                            # Colunas Específicas do Extravasor atual
                            ext_loc, ext_reg, ext_mat, ext_dest, ext_sensivel, ext_flap, ext_grade, ext_reto, 
                            ext_mare, ext_cota_mare, ext_formato, ext_dim, ext_cota_ent, ext_cota_sai, ext_comp, ext_incl, 
                            ext_causas, ext_freq, ext_medidor, ext_foto,
                            
                            # Colunas do Antigo Compilado (Agora vazias para manter o alinhamento da planilha)
                            f"Extravasor {i+1} desmembrado", "N/A",
                            
                            scada_hist, vazao_min, vazao_med, vazao_max, bombas, niveis_poco, l_ope, 
                            energia_disp, gerador, aterramento, quedas, solar, distancia_qgbt, tensao, ", ".join(necessidade_energia), l_ele, 
                            clp_existente, ligado_cco, telemetria, protocolo, sinal_tipo, sinal, pontos_io, l_aut, 
                            espaco_confinado, gas_h2s, comunidade, "Sim" if risco_alagamento else "Não", "Sim" if risco_intemperie else "Não", "Sim" if risco_vandalismo else "Não", riscos_outros, l_seg, 
                            sugestao_tec, "Sim" if as_built else "Não", pendencias, l_doc, link_pasta
                        ]
                        lista_de_linhas.append(linha)

                    # 3. Conecta ao Sheets e salva TODAS as linhas de uma vez
                    credenciais_json = json.loads(st.secrets["google_json"])
                    escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                    credenciais = Credentials.from_service_account_info(credenciais_json, scopes=escopos)
                    
                    conta_robo_planilha = gspread.authorize(credenciais)
                    planilha = conta_robo_planilha.open("Base_Dados_Vistorias_App")
                    aba_master = planilha.worksheet("Base_Master")
                    
                    aba_master.append_rows(lista_de_linhas)
                    
                    # 4. RESET E REDIRECIONAMENTO AUTOMÁTICO
                    st.session_state.clear()
                    st.session_state.sucesso_envio = f"✅ Vistoria da unidade {eee_selecionada} salva no Drive e Excel! Formulário zerado para a próxima estação."
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro interno do sistema: {e}")
