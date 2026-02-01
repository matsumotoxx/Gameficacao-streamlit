import streamlit as st
import pandas as pd
import database as db
import time
import os
import extra_streamlit_components as stx
import language as lang
import io
from fpdf import FPDF
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DA PÁGINA ---
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

st.set_page_config(
    page_title="Petro Arena",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

def toggle_sidebar():
    st.session_state.sidebar_state = 'collapsed' if st.session_state.sidebar_state == 'expanded' else 'expanded'
    # st.rerun() # Rerun is automatic with button callback usually, but explicit is safe if needed.


# --- COOKIE MANAGER (PERSISTÊNCIA) ---
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# --- ESTILIZAÇÃO CSS GAMIFICADA (NEON/DARK) ---
def load_custom_css():
    theme = st.session_state.get('theme', 'Neon Blue')
    colors = {
        'Neon Blue': {'green': '#00ff9d', 'blue': '#00f3ff', 'purple': '#bc13fe'},
        'Neon Purple': {'green': '#d946ef', 'blue': '#8a2be2', 'purple': '#00ff9d'},
        'Cyberpunk Yellow': {'green': '#fcee0a', 'blue': '#00f3ff', 'purple': '#ff003c'},
    }
    c = colors.get(theme, colors['Neon Blue'])

    css_header = f"""
        <style>
        /* Importar fontes futuristas */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');
        
        /* Variáveis de Tema */
        :root {{
            --neon-green: {c['green']};
            --neon-blue: {c['blue']};
            --neon-purple: {c['purple']};
            --dark-bg: #0a0e17;
            --card-bg: #111625;
            --border-color: #2d3748;
        }}
    """
    
    css_body = """
        /* Base */
        .stApp {
            background-color: var(--dark-bg);
            font-family: 'Rajdhani', sans-serif;
        }
        
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            background: linear-gradient(90deg, var(--neon-blue), var(--neon-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #05080f;
            border-right: 1px solid var(--border-color);
        }

        /* Cards Gamificados */
        .gamified-card {
            background: rgba(17, 22, 37, 0.9);
            border: 1px solid var(--neon-blue);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .gamified-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 25px rgba(0, 243, 255, 0.2);
        }

        /* Métricas */
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s;
        }
        div[data-testid="stMetric"]:hover {
            border-color: var(--neon-green);
            box-shadow: 0 0 10px rgba(0, 255, 157, 0.2);
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            color: #a0aaec;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-green) !important;
            text-shadow: 0 0 10px rgba(0, 255, 157, 0.4);
        }

        /* Botões Neon */
        .stButton button {
            background: transparent;
            color: var(--neon-blue);
            border: 1px solid var(--neon-blue);
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 0 5px rgba(0, 243, 255, 0.2);
        }
        .stButton button:hover {
            background: var(--neon-blue);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
            border-color: var(--neon-blue);
        }
        
        /* Botão Primário (Ação) */
        .primary-btn button {
            border-color: var(--neon-green) !important;
            color: var(--neon-green) !important;
        }
        .primary-btn button:hover {
            background: var(--neon-green) !important;
            color: #000 !important;
            box-shadow: 0 0 20px rgba(0, 255, 157, 0.6) !important;
        }

        /* Inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
            background-color: #0e121b;
            color: #fff;
            border: 1px solid #333;
            border-radius: 4px;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: var(--neon-purple);
            box-shadow: 0 0 10px rgba(188, 19, 254, 0.3);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(255,255,255,0.02);
            padding: 10px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 4px;
            color: #888;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(188, 19, 254, 0.1);
            color: var(--neon-purple) !important;
            border: 1px solid var(--neon-purple);
            box-shadow: 0 0 10px rgba(188, 19, 254, 0.2);
        }

        /* Progress Bar Custom */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple));
        }
        
        /* Toast */
        .stToast {
            background-color: #1a1f2e;
            border: 1px solid var(--neon-green);
        }

        /* Badges & Medals */
        .badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }
        .badge-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 15px;
            width: 120px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .badge-card.earned {
            border-color: var(--neon-green);
            box-shadow: 0 0 15px rgba(0, 255, 157, 0.2);
            background: linear-gradient(135deg, rgba(0, 255, 157, 0.1) 0%, rgba(0,0,0,0) 100%);
        }
        .badge-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }
        
        /* Timeline */
        .timeline {
            position: relative;
            padding: 20px 0;
        }
        .timeline::before {
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #333;
        }
        .timeline-item {
            position: relative;
            padding-left: 50px;
            margin-bottom: 25px;
        }
        .timeline-dot {
            position: absolute;
            left: 11px;
            top: 0;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid var(--neon-blue);
            background: var(--dark-bg);
            z-index: 1;
        }
        .timeline-content {
            background: rgba(255,255,255,0.03);
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid var(--neon-blue);
        }
        </style>
    """
    
    st.markdown(css_header + css_body, unsafe_allow_html=True)
    hide_streamlit_ui = """
    <style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; display: none; }
    [data-testid="stDecoration"] { visibility: hidden; }
    .stAppDeployButton { display: none; }
    </style>
    """
    st.markdown(hide_streamlit_ui, unsafe_allow_html=True)

# Inicializar Banco de Dados e CSS
db.init_db()
load_custom_css()

# --- CACHED FUNCTIONS ---
@st.cache_data(ttl=60)
def get_cached_leaderboard(sort_by='balance'):
    return db.get_leaderboard(sort_by)

@st.cache_data(ttl=300)
def get_cached_store_items():
    return db.get_store_items()

@st.cache_data(ttl=60)
def get_cached_level_config():
    return db.get_level_config()

# Gerenciamento de Sessão
if 'user' not in st.session_state:
    st.session_state.user = None

from datetime import datetime, timedelta, timezone

# --- FUNÇÕES AUXILIARES ---
def logout():
    try:
        for k in list(st.session_state.keys()):
            try:
                del st.session_state[k]
            except Exception:
                pass
        st.session_state.user = None
        try:
            get_cached_leaderboard.clear()
            get_cached_store_items.clear()
            get_cached_level_config.clear()
        except Exception:
            pass
        try:
            cookies = cookie_manager.get_all()
            for key in list(cookies.keys()):
                try:
                    cookie_manager.delete(key)
                except Exception:
                    pass
            try:
                cookie_manager.set("user_email", "", expires_at=datetime.now() - timedelta(days=1))
            except Exception:
                pass
        except Exception:
            pass
        try:
            st.experimental_set_query_params()
        except Exception:
            pass
    except Exception:
        st.error("Falha ao encerrar sessão. Tente novamente.")
    finally:
        st.rerun()

def format_brt(ts):
    if ts is None or ts == "":
        return ""
    try:
        if isinstance(ts, datetime):
            dt = ts
        else:
            s = str(ts)
            try:
                dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    dt = datetime.strptime(s[:10], "%Y-%m-%d")
                    dt = dt.replace(hour=0, minute=0, second=0)
                except ValueError:
                    return s
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        brt = timezone(timedelta(hours=-3))
        local_dt = dt.astimezone(brt)
        return local_dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return str(ts)

def format_brt_date(ts):
    s = format_brt(ts)
    return s.split(" ")[0] if s else ""

# --- TELA DE LOGIN ---
def login():
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="font-size: 3em; margin-bottom: 0;">PETRO ARENA</h1>
                <p style="color: var(--neon-blue); letter-spacing: 3px; font-family: 'Orbitron';">ACESSO AO SISTEMA</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("login_form"):
                email = st.text_input("CREDENCIAL ID (E-mail)", placeholder="usuario@corp.com")
                password = st.text_input("CÓDIGO DE ACESSO (Senha)", type="password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("INICIAR SESSÃO", use_container_width=True)
            
            if submitted:
                user = db.authenticate_user(email, password)
                if user:
                    st.session_state.user = {
                        'id': user[0], 'username': user[1], 'role': user[2], 'balance': user[3],
                        'avatar_url': user[4], 'streak_days': user[5]
                    }
                    
                    # Daily Bonus Removed
                        
                    # Set cookie
                    cookie_manager.set("user_email", email, expires_at=datetime.now() + timedelta(days=7))
                    st.rerun()
                else:
                    st.error("ACESSO NEGADO: Credenciais Inválidas")

def register():
    st.markdown("<div class='main-header'><h1>📝 Novo Registro</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            new_user = st.text_input("👤 Nome de Usuário")
            new_email = st.text_input("📧 E-mail")
            new_pass = st.text_input("🔑 Senha", type="password")
            confirm_pass = st.text_input("🔑 Confirmar Senha", type="password")
            # Admin secret code to register as admin (optional, for demo)
            admin_code = st.text_input("🛡️ Código de Admin (Opcional)", type="password")
            
            submitted = st.form_submit_button("CRIAR CONTA ✨", use_container_width=True)
        
        if submitted:
            if new_pass != confirm_pass:
                st.error("As senhas não coincidem!")
            elif not new_user or not new_email or not new_pass:
                st.error("Preencha todos os campos obrigatórios.")
            else:
                role = 'Jogador'
                if admin_code == "admin123": # Simple hardcoded check for demo
                    role = 'Administrador'
                
                if db.create_user(new_user, new_email, new_pass, role):
                    st.success("Conta criada com sucesso! Faça login.")
                else:
                    st.error("Erro: Usuário ou E-mail já cadastrados.")

# --- INTERFACE DO ADMINISTRADOR ---
def admin_dashboard():
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(45deg, #bc13fe, #00f3ff); margin: 0 auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(188,19,254,0.5);">
                    <span style="font-size: 40px;">🛡️</span>
                </div>
                <h3 style="margin-top: 10px; font-size: 1.2em;">ADMINISTRADOR</h3>
                <p style="color: #888;">Controle do Sistema</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("ENCERRAR SESSÃO", use_container_width=True):
            logout()
        
        st.markdown("---")
        if st.button("⏪ OCULTAR MENU", use_container_width=True):
            toggle_sidebar()

    if st.session_state.sidebar_state == 'collapsed':
        if st.button("⏩ MOSTRAR MENU"):
            toggle_sidebar()

    st.markdown("## PAINEL DE CONTROLE")
    
    # Métricas
    users = db.get_all_users()
    pending_reqs = db.get_pending_requests()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("JOGADORES ATIVOS", len(users[users['role'] == 'Jogador']))
    c2.metric("SOLICITAÇÕES PENDENTES", len(pending_reqs), delta_color="off")
    c3.metric("PONTOS TOTAIS", users['balance'].sum())
    c4.metric("STATUS DO SISTEMA", "ONLINE", delta_color="normal")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🏆 RANKING", 
        "⚡ PONTUAÇÃO", 
        "🛍️ LOJA", 
        "✅ APROVAÇÕES",
        "👥 USUÁRIOS",
        "📜 AUDITORIA",
        "🏅 NÍVEIS",
        "🎯 MISSÕES",
        "📊 RELATÓRIOS",
        "💾 BACKUP & DADOS"
    ])
    
    # 1. Ranking Geral
    with tab1:
        st.markdown("### LEADERBOARD")
        col_sort, col_filter = st.columns([1, 4])
        with col_sort:
            sort_by = st.selectbox("Ordernar por:", ["balance", "date"], format_func=lambda x: "Pontuação" if x == "balance" else "Data de Registro")
            
        df_rank = get_cached_leaderboard(sort_by)
        
        if not df_rank.empty:
            # Podium Top 3
            if len(df_rank) >= 1:
                st.markdown("<br>", unsafe_allow_html=True)
                cols = st.columns([1, 1.2, 1])
                
                # 2nd Place
                if len(df_rank) >= 2:
                    row = df_rank.iloc[1]
                    with cols[0]:
                        st.markdown(f"""
                            <div class='gamified-card' style='text-align:center; border-color: #C0C0C0; margin-top: 20px;'>
                                <div style='font-size: 40px;'>🥈</div>
                                <h3 style='color: #C0C0C0;'>{row['username']}</h3>
                                <h2 style='color: #fff;'>{row['balance']}</h2>
                                <p style='color: #888;'>{row['level']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # 1st Place
                row = df_rank.iloc[0]
                with cols[1]:
                    st.markdown(f"""
                        <div class='gamified-card' style='text-align:center; border-color: #FFD700; transform: scale(1.05); box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);'>
                            <div style='font-size: 50px;'>🥇</div>
                            <h3 style='color: #FFD700;'>{row['username']}</h3>
                            <h1 style='color: #fff; font-size: 3em;'>{row['balance']}</h1>
                            <p style='color: #888;'>{row['level']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # 3rd Place
                if len(df_rank) >= 3:
                    row = df_rank.iloc[2]
                    with cols[2]:
                        st.markdown(f"""
                            <div class='gamified-card' style='text-align:center; border-color: #CD7F32; margin-top: 20px;'>
                                <div style='font-size: 40px;'>🥉</div>
                                <h3 style='color: #CD7F32;'>{row['username']}</h3>
                                <h2 style='color: #fff;'>{row['balance']}</h2>
                                <p style='color: #888;'>{row['level']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Full List
            st.markdown("#### LISTA COMPLETA")
            st.markdown("<div style='display: flex; flex-direction: column; gap: 10px;'>", unsafe_allow_html=True)
            
            # Reset index to get 0-based iteration but display 1-based rank
            for idx, row in df_rank.reset_index(drop=True).iterrows():
                rank_idx = idx + 1
                medal = "🔹"
                if rank_idx == 1: medal = "🥇"
                elif rank_idx == 2: medal = "🥈"
                elif rank_idx == 3: medal = "🥉"
                
                # Dynamic width bar
                max_pts = df_rank['balance'].max()
                width_pct = (row['balance'] / max_pts * 100) if max_pts > 0 else 0
                
                st.markdown(f"""
                <div class='gamified-card' style='padding: 15px; display: flex; align-items: center; justify-content: space-between; border-left: 5px solid var(--neon-blue);'>
                    <div style='display: flex; align-items: center; gap: 15px; flex: 1;'>
                        <div style='font-size: 1.5em; width: 40px; text-align: center; color: #888;'>#{rank_idx}</div>
                        <div style='font-size: 1.5em;'>{medal}</div>
                        <div>
                            <div style='font-weight: bold; font-size: 1.1em;'>{row['username']}</div>
                            <div style='color: #888; font-size: 0.8em;'>{row['level']} • Desde {format_brt_date(row['created_at'])}</div>
                        </div>
                    </div>
                    <div style='flex: 1; margin: 0 20px; display: flex; align-items: center; gap: 10px;'>
                        <div style='background: #333; height: 8px; border-radius: 4px; overflow: hidden; width: 100%;'>
                            <div style='background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple)); width: {width_pct}%; height: 100%;'></div>
                        </div>
                    </div>
                    <div style='font-family: "Orbitron"; font-size: 1.2em; color: var(--neon-green); min-width: 100px; text-align: right;'>
                        {row['balance']} PTS
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum dado disponível.")

    # 2. Adicionar/Remover Pontos
    with tab2:
        c_add, c_rem = st.columns(2)
        
        with c_add:
            st.markdown("<div class='gamified-card'>", unsafe_allow_html=True)
            st.markdown("#### ➕ RECOMPENSAR (EARN)")
            player_options = users[users['role'] == 'Jogador']
            
            if not player_options.empty:
                sel_player_earn = st.selectbox("Selecionar Agente", options=player_options['id'].tolist(), format_func=lambda x: player_options[player_options['id'] == x]['username'].values[0], key="sel_earn")
                pts_earn = st.number_input("Qtd. Pontos", min_value=10, step=10, key="pts_earn")
                reason_earn = st.text_input("Motivo (Missão)", key="reason_earn")
                
                if st.button("CONCEDER CRÉDITOS", use_container_width=True):
                    db.update_points(sel_player_earn, pts_earn, reason_earn, 'EARN', st.session_state.user['id'])
                    db.add_notification(sel_player_earn, f"MISSÃO CUMPRIDA: Você recebeu {pts_earn} pts! Motivo: {reason_earn}")
                    get_cached_leaderboard.clear()
                    st.success(f"Créditos transferidos para o agente.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c_rem:
            st.markdown("<div class='gamified-card' style='border-color: #ff4b4b;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #ff4b4b;'>➖ APLICAR PENALIDADE</h4>", unsafe_allow_html=True)
            
            if not player_options.empty:
                sel_player_pen = st.selectbox("Selecionar Agente", options=player_options['id'].tolist(), format_func=lambda x: player_options[player_options['id'] == x]['username'].values[0], key="sel_pen")
                pts_pen = st.number_input("Qtd. Pontos", min_value=10, step=10, key="pts_pen")
                reason_pen = st.text_input("Motivo (Infração)", key="reason_pen")
                
                if st.button("APLICAR PENALIDADE", use_container_width=True):
                    if not reason_pen:
                        st.error("Motivo é obrigatório para penalidades.")
                    else:
                        db.apply_penalty(sel_player_pen, pts_pen, reason_pen, st.session_state.user['id'])
                        db.add_notification(sel_player_pen, f"ALERTA: Penalidade de -{pts_pen} pts aplicada. Motivo: {reason_pen}")
                        get_cached_leaderboard.clear()
                        st.warning(f"Penalidade aplicada ao agente.")
            st.markdown("</div>", unsafe_allow_html=True)

    # 3. Gerenciar Loja
    with tab3:
        st.markdown("### ARSENAL & RECOMPENSAS")
        
        with st.expander("➕ CADASTRAR NOVO ITEM", expanded=False):
            with st.form("new_item_form"):
                item_name = st.text_input("Nome do Item")
                item_desc = st.text_area("Descrição")
                item_cost = st.number_input("Custo (Pts)", min_value=1)
                submitted = st.form_submit_button("SALVAR NO BANCO DE DADOS")
                if submitted:
                    db.add_store_item(item_name, item_desc, item_cost)
                    get_cached_store_items.clear()
                    st.success("Item registrado!")
                    st.rerun()
        
        items = get_cached_store_items()
        if not items.empty:
            st.markdown("#### CATÁLOGO ATUAL")
            # Grid view for Admin
            cols = st.columns(3)
            for idx, row in items.iterrows():
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div class='gamified-card'>
                            <h4 style='color: var(--neon-blue);'>{row['name']}</h4>
                            <p style='color: #888;'>{row['cost']} PTS</p>
                            <small>{row['description']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🗑️ EXCLUIR", key=f"del_item_{row['id']}", use_container_width=True):
                        success, msg = db.delete_store_item(row['id'], st.session_state.user['id'])
                        if success:
                            get_cached_store_items.clear()
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("Nenhum item cadastrado.")

    # 4. Validações (Store + Missions)
    with tab4:
        st.markdown("### CENTRAL DE VALIDAÇÃO")
        
        val_tab1, val_tab2 = st.tabs(["🛒 COMPRAS NA LOJA", "🎯 MISSÕES REALIZADAS"])
        
        with val_tab1:
            st.markdown("#### REQUISIÇÕES DE COMPRA")
            if not pending_reqs.empty:
                for index, row in pending_reqs.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="gamified-card" style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin:0; color: var(--neon-blue);">{row['item_name']}</h4>
                                <p style="margin:0; color: #888;">Agente: {row['username']} • Custo: {row['cost']} pts</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c_yes, c_no = st.columns(2)
                        if c_yes.button("✅ AUTORIZAR", key=f"app_{row['id']}", use_container_width=True):
                            if db.process_purchase_request(row['id'], 'APPROVE', st.session_state.user['id']):
                                st.success("Autorizado!")
                                st.rerun()
                            else:
                                st.error("Saldo insuficiente!")
                        
                        if c_no.button("❌ NEGAR", key=f"rej_{row['id']}", use_container_width=True):
                            db.process_purchase_request(row['id'], 'REJECT', st.session_state.user['id'])
                            st.info("Negado.")
                            st.rerun()
            else:
                st.info("Nenhuma requisição de compra pendente.")

        with val_tab2:
            st.markdown("#### MISSÕES AGUARDANDO VALIDAÇÃO")
            pending_missions = db.get_pending_mission_validations()
            
            if not pending_missions.empty:
                for idx, row in pending_missions.iterrows():
                    with st.container(border=True):
                        st.markdown(f"""
                        <div class="gamified-card" style="border-left: 5px solid orange;">
                            <div style="display:flex; justify-content:space-between;">
                                <h4>{row['title']}</h4>
                                <span style="color:var(--neon-green);">+{row['reward']} PTS</span>
                            </div>
                            <p><strong>Agente:</strong> {row['username']}</p>
                            <p><strong>Requisitos:</strong> {row['requirements']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        justification = st.text_input("Justificativa / Observação", key=f"just_{row['id']}")
                        
                        c_app, c_rej = st.columns(2)
                        
                        if c_app.button("✅ APROVAR MISSÃO", key=f"app_m_{row['id']}", use_container_width=True):
                            success, msg = db.process_mission_validation(row['id'], 'APPROVE', justification, st.session_state.user['id'])
                            if success:
                                st.success(msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
                                
                        if c_rej.button("❌ REJEITAR MISSÃO", key=f"rej_m_{row['id']}", use_container_width=True):
                            if not justification:
                                st.error("É obrigatório informar o motivo da rejeição.")
                            else:
                                success, msg = db.process_mission_validation(row['id'], 'REJECT', justification, st.session_state.user['id'])
                                if success:
                                    st.warning(msg)
                                    time.sleep(1)
                                    st.rerun()
            else:
                st.info("Nenhuma missão aguardando análise.")

    # 5. Gestão de Usuários
    with tab5:
        st.markdown("### DATABASE DE AGENTES")
        
        c_reg, c_man = st.columns(2)
        
        with c_reg:
            with st.expander("🆕 NOVO AGENTE", expanded=True):
                new_user = st.text_input("Codename (Usuário)")
                new_email = st.text_input("Email")
                new_pass = st.text_input("Senha Provisória", type="password")
                new_role = st.selectbox("Nível de Acesso", ["Jogador", "Administrador"])
                
                if st.button("CRIAR REGISTRO"):
                    if db.create_user(new_user, new_email, new_pass, new_role):
                        st.success("Agente registrado com sucesso.")
                        st.rerun()
                    else:
                        st.error("Erro: Usuário ou Email já existem.")

        with c_man:
            with st.expander("🔐 CREDENCIAIS (Reset de senha)", expanded=True):
                rst_user = st.selectbox("Selecionar Usuário", options=users['id'].tolist(), format_func=lambda x: users[users['id'] == x]['username'].values[0])
                rst_pass = st.text_input("Nova Senha", type="password", key="rst_pass")
                if st.button("REDEFINIR SENHA"):
                    db.reset_password(rst_user, rst_pass, st.session_state.user['id'])
                    st.success("Senha atualizada.")

        st.markdown("---")
        st.markdown("#### 🗑️ ZONA DE EXCLUSÃO (DANGER ZONE)")
        
        with st.container(border=True):
            del_user_id = st.selectbox("Selecionar Usuário para Exclusão", options=users[users['id'] != st.session_state.user['id']]['id'].tolist(), format_func=lambda x: users[users['id'] == x]['username'].values[0], key="del_user_sel")
            
            if del_user_id:
                deps = db.check_user_dependencies(del_user_id)
                st.info(f"Dados vinculados: {deps['transactions']} Transações, {deps['purchase_requests']} Compras, {deps['notifications']} Notificações")
                
                if st.button("❌ EXCLUIR USUÁRIO PERMANENTEMENTE", type="primary"):
                    success, msg = db.delete_user(del_user_id, st.session_state.user['id'])
                    if success:
                        get_cached_leaderboard.clear()
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Erro: {msg}")

    # 6. Auditoria
    with tab6:
        st.markdown("### LOGS DO SISTEMA")
        logs = db.get_audit_logs()
        
        if not logs.empty:
            # Filters
            f1, f2 = st.columns(2)
            with f1:
                action_filter = st.multiselect("Filtrar por Ação", options=logs['action'].unique(), format_func=lambda x: lang.get_text(x))
            with f2:
                admin_filter = st.multiselect("Filtrar por Admin", options=logs['admin_name'].unique())
            
            filtered_logs = logs
            if action_filter:
                filtered_logs = filtered_logs[filtered_logs['action'].isin(action_filter)]
            if admin_filter:
                filtered_logs = filtered_logs[filtered_logs['admin_name'].isin(admin_filter)]
                
            st.markdown("<div style='display: flex; flex-direction: column; gap: 10px;'>", unsafe_allow_html=True)
            for _, row in filtered_logs.iterrows():
                icon = "📝"
                color = "#888"
                if "DELETE" in row['action']:
                    icon = "🗑️"
                    color = "#ff4b4b"
                elif "APPROVE" in row['action']:
                    icon = "✅"
                    color = "var(--neon-green)"
                elif "REJECT" in row['action']:
                    icon = "❌"
                    color = "#ff4b4b"
                elif "PENALTY" in row['action']:
                    icon = "⚠️"
                    color = "orange"
                elif "EARN" in row['action']:
                    icon = "🎁"
                    color = "var(--neon-blue)"
                
                st.markdown(f"""
                <div class='gamified-card' style='padding: 10px 15px; border-left: 4px solid {color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='display: flex; align-items: center; gap: 10px;'>
                            <span style='font-size: 1.5em;'>{icon}</span>
                            <div>
                                <div style='font-weight: bold; color: {color};'>{lang.get_text(row['action'])}</div>
                                <div style='font-size: 0.9em; color: #ccc;'>{row['details']}</div>
                            </div>
                        </div>
                            <div style='text-align: right;'>
                            <div style='font-size: 0.8em; color: #888;'>{format_brt(row['timestamp'])}</div>
                            <div style='font-size: 0.8em; color: #aaa;'>Admin: {row['admin_name']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Logs limpos.")

    # 7. Níveis
    with tab7:
        st.markdown("### CONFIGURAÇÃO DE PATENTES (MEDALHAS)")
        st.markdown("Defina os intervalos de pontuação para cada nível.")
        
        levels = db.get_level_config().sort_values('min_points')
        
        # Validation & Edit Form
        with st.form("level_config_form"):
            edited_levels = {}
            for idx, row in levels.iterrows():
                c1, c2, c3 = st.columns([1, 2, 2])
                c1.markdown(f"<span style='font-size:30px'>{row['badge_icon']}</span>", unsafe_allow_html=True)
                c2.markdown(f"**{row['level_name']}**")
                
                new_val = c3.number_input(
                    f"Mínimo de Pontos ({row['level_name']})", 
                    min_value=0, 
                    value=int(row['min_points']), 
                    key=f"lvl_input_{row['level_name']}"
                )
                edited_levels[row['level_name']] = new_val
            
            if st.form_submit_button("💾 SALVAR CONFIGURAÇÕES"):
                # Validate
                valid = True
                values = list(edited_levels.values())
                # Check for uniqueness
                if len(set(values)) != len(values):
                    st.error("Erro: Pontuações não podem ser iguais.")
                    valid = False
                
                if valid:
                    for name, val in edited_levels.items():
                        db.update_level_threshold(name, val)
                    st.success("Configuração de níveis atualizada com sucesso!")
                    time.sleep(1)
                    st.rerun()

        # Preview
        st.markdown("---")
        st.markdown("#### 👁️ PREVIEW DE DISTRIBUIÇÃO")
        users = db.get_all_users()
        
        preview_data = []
        # Re-fetch levels to ensure order is correct for preview
        levels = db.get_level_config().sort_values('min_points')
        
        for i in range(len(levels)):
            row = levels.iloc[i]
            min_p = row['min_points']
            max_p = float('inf')
            if i < len(levels) - 1:
                max_p = levels.iloc[i+1]['min_points'] - 1
            
            count = users[(users['balance'] >= min_p) & (users['balance'] <= max_p)].shape[0] if max_p != float('inf') else users[users['balance'] >= min_p].shape[0]
            
            preview_data.append({
                "Nível": f"{row['badge_icon']} {row['level_name']}",
                "Faixa": f"{min_p} - {max_p if max_p != float('inf') else '∞'}",
                "Jogadores": count
            })
            
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True)

    # 8. Missões
    with tab8:
        st.markdown("### GERENCIAR MISSÕES")
        
        with st.expander("➕ CADASTRAR NOVA MISSÃO", expanded=False):
            with st.form("new_mission_form"):
                m_title = st.text_input("Título da Missão")
                m_desc = st.text_area("Descrição")
                m_reward = st.number_input("Recompensa (Pontos)", min_value=10, step=10)
                m_req = st.text_input("Requisitos (Texto Livre)")
                m_deadline = st.date_input("Prazo Final (Opcional)", value=None)
                
                if st.form_submit_button("CRIAR MISSÃO"):
                    if m_title and m_reward:
                        db.create_mission(m_title, m_desc, m_reward, m_deadline, m_req)
                        st.success("Missão criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Título e Recompensa são obrigatórios.")
        
        st.markdown("#### MISSÕES ATIVAS")
        missions = db.get_all_missions()
        
        if not missions.empty:
            for _, row in missions.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**{row['title']}** (+{row['reward']} pts)")
                        st.markdown(f"<small>{row['description']}</small>", unsafe_allow_html=True)
                        if row['deadline']:
                            st.markdown(f"<small style='color:orange'>Prazo: {format_brt_date(row['deadline'])}</small>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"Status: `{row['status']}`")
                    with c3:
                        if st.button("🗑️", key=f"del_mission_{row['id']}"):
                            db.delete_mission(row['id'])
                            st.success("Removida!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("Nenhuma missão cadastrada.")

    # 9. Relatórios
    with tab9:
        st.markdown("### 📊 GERADOR DE RELATÓRIOS")
        
        # Filters
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            rep_type = c1.selectbox("Tipo de Relatório", ["Usuários", "Missões", "Financeiro"])
            
            filters = {}
            if rep_type == "Usuários":
                role = c2.selectbox("Função", ["Todos", "Jogador", "Administrador"])
                if role != "Todos": filters['role'] = role
                
                min_pts = c3.number_input("Mínimo de Pontos", min_value=0, value=0)
                if min_pts > 0: filters['min_points'] = min_pts
                
            elif rep_type == "Missões":
                status = c2.selectbox("Status", ["Todos", "completed", "pending_validation", "accepted", "expired"])
                if status != "Todos": filters['status'] = status
                
            elif rep_type == "Financeiro":
                t_type = c2.selectbox("Tipo de Transação", ["Todos", "EARN", "SPEND", "PENALTY"])
                if t_type != "Todos": filters['type'] = t_type

        # Generate Data
        type_map = {"Usuários": "users", "Missões": "missions", "Financeiro": "financial"}
        df_rep = db.get_report_data(type_map[rep_type], filters)
        
        # Display
        st.dataframe(df_rep, use_container_width=True)
        
        # Exports
        c_exp1, c_exp2 = st.columns([1, 1])
        
        # Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_rep.to_excel(writer, index=False, sheet_name='Relatorio')
        
        c_exp1.download_button(
            label="📥 Baixar Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"relatorio_{type_map[rep_type]}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # PDF Helper
        def create_pdf(dataframe, title):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.ln(10)
            
            # Header
            pdf.set_font("Arial", 'B', 10)
            cols = dataframe.columns
            for col in cols:
                # Basic column width logic
                pdf.cell(40, 10, str(col)[:15], 1)
            pdf.ln()
            
            # Rows
            pdf.set_font("Arial", size=10)
            for _, row in dataframe.iterrows():
                for col in cols:
                    pdf.cell(40, 10, str(row[col])[:15], 1)
                pdf.ln()
            return pdf.output(dest='S').encode('latin-1', 'replace')

        # PDF Download
        try:
            pdf_data = create_pdf(df_rep, f"Relatório de {rep_type}")
            c_exp2.download_button(
                label="📥 Baixar PDF (.pdf)",
                data=pdf_data,
                file_name=f"relatorio_{type_map[rep_type]}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            c_exp2.error(f"Erro ao gerar PDF: {e}")


    # 10. Backup & Restore
    with tab10:
        st.markdown("### 💾 CENTRAL DE BACKUP E RESTAURAÇÃO")
        st.info("Utilize esta seção para realizar backups de segurança e restaurar dados do sistema.")
        
        c_export, c_import = st.columns(2)
        
        # --- EXPORT SECTION ---
        with c_export:
            st.markdown("#### 📤 EXPORTAR DADOS")
            st.markdown("Selecione o formato desejado para download.")
            
            with st.container(border=True):
                # 1. Full DB Backup
                st.markdown("##### 📦 Backup Completo (.db)")
                st.caption("Cópia binária exata do banco de dados SQLite atual.")
                
                try:
                    if hasattr(db, 'get_db_file_bytes'):
                        db_bytes = db.get_db_file_bytes()
                        st.download_button(
                            label="⬇️ BAIXAR BACKUP COMPLETO",
                            data=db_bytes,
                            file_name=f"petro_arena_full_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                            mime="application/x-sqlite3",
                            use_container_width=True
                        )
                    else:
                        st.warning("Função de backup aguardando atualização do sistema. Tente recarregar.")
                except Exception as e:
                    st.error(f"Erro ao gerar backup: {e}")
                
                st.markdown("---")
                
                # 2. SQL Dump
                st.markdown("##### 📜 Dump SQL (.sql)")
                st.caption("Script SQL contendo estrutura e dados para recriação.")
                
                if st.button("GERAR DUMP SQL", use_container_width=True):
                    try:
                        if hasattr(db, 'export_to_sql'):
                            sql_dump = db.export_to_sql()
                            st.download_button(
                                label="⬇️ DOWNLOAD SQL",
                                data=sql_dump,
                                file_name=f"petro_arena_dump_{datetime.now().strftime('%Y%m%d_%H%M')}.sql",
                                mime="text/plain",
                                use_container_width=True
                            )
                        else:
                            st.warning("Função de exportação SQL indisponível.")
                    except Exception as e:
                        st.error(f"Erro ao exportar SQL: {e}")
                
                st.markdown("---")
                
                # 3. Data Export (CSV/JSON ZIP)
                st.markdown("##### 📊 Exportar Dados (CSV/JSON)")
                st.caption("Arquivos de dados compactados para análise externa.")
                
                col_fmt1, col_fmt2 = st.columns(2)
                if col_fmt1.button("ZIP (CSV)", use_container_width=True):
                    try:
                        if hasattr(db, 'export_to_csv_zip'):
                            zip_csv = db.export_to_csv_zip()
                            st.download_button(
                                label="⬇️ DOWNLOAD CSVs",
                                data=zip_csv,
                                file_name=f"petro_arena_data_csv_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                        else:
                            st.warning("Função de exportação CSV indisponível.")
                    except Exception as e:
                        st.error(f"Erro ao exportar CSV: {e}")
                    
                if col_fmt2.button("ZIP (JSON)", use_container_width=True):
                    try:
                        if hasattr(db, 'export_to_json_zip'):
                            zip_json = db.export_to_json_zip()
                            st.download_button(
                                label="⬇️ DOWNLOAD JSONs",
                                data=zip_json,
                                file_name=f"petro_arena_data_json_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                        else:
                            st.warning("Função de exportação JSON indisponível.")
                    except Exception as e:
                        st.error(f"Erro ao exportar JSON: {e}")

        # --- IMPORT SECTION ---
        with c_import:
            st.markdown("#### 📥 RESTAURAR DADOS")
            st.warning("⚠️ A restauração substituirá os dados atuais. Faça backup antes de prosseguir!")
            
            with st.container(border=True):
                restore_type = st.radio("Método de Restauração", ["Arquivo de Banco (.db)", "Script SQL (.sql)"])
                
                uploaded_file = st.file_uploader(f"Carregar arquivo {restore_type.split()[-1]}", type=['db', 'sql'])
                
                if uploaded_file:
                    st.error("⚠️ ATENÇÃO: Esta ação é irreversível!")
                    confirm_check = st.checkbox("Eu entendo os riscos e desejo sobrescrever o banco de dados atual.")
                    
                    if confirm_check:
                        if st.button("🔴 INICIAR RESTAURAÇÃO", type="primary", use_container_width=True):
                            with st.spinner("Processando restauração..."):
                                success = False
                                msg = ""
                                
                                try:
                                    if restore_type == "Arquivo de Banco (.db)":
                                        success, msg = db.restore_from_db_file(uploaded_file.getvalue())
                                    else:
                                        # SQL Script
                                        string_data = uploaded_file.getvalue().decode("utf-8")
                                        success, msg = db.restore_from_sql(string_data)
                                    
                                    if success:
                                        # Log Action
                                        db.log_audit_action(
                                            st.session_state.user['id'], 
                                            "RESTORE_BACKUP", 
                                            f"Restored DB via {restore_type}"
                                        )
                                        st.success(msg)
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                except Exception as e:
                                    st.error(f"Erro crítico na restauração: {e}")
        
        # --- REPORT SCHEDULING (NEW) ---
        st.markdown("---")
        with st.expander("⏱️ AGENDAMENTO DE RELATÓRIOS AUTOMÁTICOS"):
            st.caption("Receba relatórios periódicos por e-mail (simulação).")
            
            c_sch1, c_sch2, c_sch3 = st.columns([2, 1, 1])
            
            with c_sch1:
                sch_type = st.selectbox("Tipo de Relatório", ["Relatório de Usuários", "Relatório de Missões", "Relatório Financeiro"])
                sch_freq = st.selectbox("Frequência", ["Diário (00:00)", "Semanal (Domingo)", "Mensal (Dia 1)"])
                sch_email = st.text_input("Email para envio (Opcional)")
                
                if st.button("➕ CRIAR AGENDAMENTO"):
                    try:
                        if hasattr(db, 'create_report_schedule'):
                            db.create_report_schedule(sch_type, sch_freq, sch_email)
                            st.success(f"Agendamento criado: {sch_type} - {sch_freq}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Funcionalidade de agendamento indisponível.")
                    except Exception as e:
                        st.error(f"Erro ao criar agendamento: {e}")

            # List Active Schedules
            st.markdown("##### 📅 Agendamentos Ativos")
            try:
                if hasattr(db, 'get_report_schedules'):
                    schedules_df = db.get_report_schedules()
                    
                    if not schedules_df.empty:
                        for _, row in schedules_df.iterrows():
                            c_row1, c_row2 = st.columns([4, 1])
                            with c_row1:
                                st.info(f"**{row['report_type']}** | {row['frequency']} | 📧 {row['email'] if row['email'] else 'N/A'}")
                            with c_row2:
                                if st.button("❌", key=f"del_sch_{row['id']}", help="Remover agendamento"):
                                    db.delete_report_schedule(row['id'])
                                    st.rerun()
                    else:
                        st.caption("Nenhum agendamento ativo.")
                else:
                    st.caption("Carregando agendamentos...")
            except Exception as e:
                st.error(f"Erro ao carregar agendamentos: {e}")

        # --- BACKUP SCHEDULER MOCK ---
        st.markdown("---")
        with st.expander("⏱️ AGENDAMENTO DE BACKUP AUTOMÁTICO"):
            c_sch1, c_sch2, c_sch3 = st.columns([2, 1, 1])
            freq = c_sch1.selectbox("Frequência Backup", ["Diário (00:00)", "Semanal (Domingo)", "Mensal (Dia 1)"])
            email = c_sch1.text_input("Email para notificação (Opcional)")
            
            status_ph = c_sch3.empty()
            if 'backup_schedule' not in st.session_state:
                st.session_state.backup_schedule = False
                
            if st.session_state.backup_schedule:
                status_ph.success("ATIVADO")
                if c_sch2.button("DESATIVAR"):
                    st.session_state.backup_schedule = False
                    st.rerun()
            else:
                status_ph.warning("DESATIVADO")
                if c_sch2.button("ATIVAR"):
                    st.session_state.backup_schedule = True
                    st.toast("Agendamento configurado! (Simulação)")
                    st.rerun()


# --- INTERFACE DO JOGADOR ---
def player_dashboard():
    # Atualizar dados do usuário
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id = ?", (st.session_state.user['id'],))
    current_balance = c.fetchone()[0]
    conn.close()
    
    # Notificações não lidas
    notifs = db.get_user_notifications(st.session_state.user['id'])
    unread_count = len(notifs[notifs['is_read'] == 0])
    
    # Sidebar
    with st.sidebar:
        # Avatar Display
        avatar = st.session_state.user.get('avatar_url')
        if not avatar or not os.path.exists(avatar):
             # Default avatar placeholder
             st.markdown(f"""
                <div style="text-align: center;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; border: 2px solid var(--neon-green); margin: 0 auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px var(--neon-green); background: #000;">
                        <span style="font-size: 50px;">👤</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
             # Custom avatar
             # We use st.image with some custom CSS to make it circular
             col_l, col_c, col_r = st.columns([1,2,1])
             with col_c:
                 st.image(avatar, width=100)
        
        st.markdown(f"""
            <div style="text-align: center;">
                <h2 style="margin-top: 15px; font-size: 1.5em; color: white;">{st.session_state.user['username']}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Avatar Upload
        with st.expander("📸 Alterar Avatar"):
            uploaded_file = st.file_uploader("Escolha uma imagem", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                # Ensure directory exists
                if not os.path.exists("static/avatars"):
                    os.makedirs("static/avatars")
                    
                # Save file
                file_ext = uploaded_file.name.split('.')[-1]
                file_name = f"avatar_{st.session_state.user['id']}.{file_ext}"
                save_path = os.path.join("static", "avatars", file_name)
                
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Update DB
                new_avatar_url = save_path.replace("\\", "/") # Normalize path
                db.update_avatar(st.session_state.user['id'], new_avatar_url)
                
                # Update session
                st.session_state.user['avatar_url'] = new_avatar_url
                st.success("Avatar atualizado!")
                time.sleep(1)
                st.rerun()
            
            # Remove Avatar - show only if custom exists
            has_custom = bool(st.session_state.user.get('avatar_url') and os.path.exists(st.session_state.user.get('avatar_url')))
            if has_custom:
                st.markdown("<hr/>", unsafe_allow_html=True)
                st.markdown("### 🧹 Remover Foto")
                if st.button("Remover Foto (Voltar ao Padrão)", key="btn_remove_avatar", use_container_width=True):
                    st.session_state.confirm_remove_avatar = True
                    st.experimental_rerun()
            
            if st.session_state.get("confirm_remove_avatar"):
                st.warning("Tem certeza que deseja remover sua foto de perfil?")
                c_yes, c_no = st.columns(2)
                if c_yes.button("Confirmar Remoção", key="confirm_remove_yes", use_container_width=True):
                    success, msg = db.remove_avatar(st.session_state.user['id'])
                    if success:
                        st.session_state.user['avatar_url'] = None
                        st.success(msg)
                        st.session_state.confirm_remove_avatar = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                        st.session_state.confirm_remove_avatar = False
                        st.experimental_rerun()
                if c_no.button("Cancelar", key="confirm_remove_no", use_container_width=True):
                    st.session_state.confirm_remove_avatar = False
                    st.experimental_rerun()

        # Theme Selector
        st.markdown("### 🎨 Personalização")
        st.selectbox("Escolha seu Tema", 
                     ['Neon Blue', 'Neon Purple', 'Cyberpunk Yellow'],
                     key='theme')
        
        # Nível Gamificado
        level_df = db.get_level_config()
        current_level_name = "Novato"
        next_level_points = 100
        
        # Determinar nível atual
        for _, row in level_df.iterrows():
            if current_balance >= row['min_points']:
                current_level_name = row['level_name']
            else:
                next_level_points = row['min_points']
                break
                
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center;">
                <small style="color: #888; text-transform: uppercase;">Patente Atual</small>
                <h3 style="margin: 5px 0; color: var(--neon-purple);">{current_level_name}</h3>
                <div style="background: #333; height: 6px; border-radius: 3px; margin-top: 10px; overflow: hidden;">
                    <div style="background: var(--neon-purple); width: {min(current_balance/next_level_points, 1.0)*100}%; height: 100%;"></div>
                </div>
                <small style="color: #666;">{current_balance} / {next_level_points} XP</small>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("LOGOUT / SAIR", use_container_width=True):
            logout()

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("CENTRAL DE COMANDO")
    with col_h2:
        st.markdown(f"""
            <div style="text-align: right; padding: 10px;">
                <span style="font-size: 24px; color: var(--neon-green); font-weight: bold; font-family: 'Orbitron';">{current_balance} PTS</span>
                <br><small style="color: #888;">SALDO DISPONÍVEL</small>
            </div>
        """, unsafe_allow_html=True)

    # Tabs Principais
    tab1, tab2, tab3, tab4 = st.tabs(["🛒 LOJA", "🏅 MISSÕES & CONQUISTAS", "📜 EXTRATO", f"🔔 NOTIFICAÇÕES ({unread_count})"])

    with tab1:
        st.markdown("### SUPRIMENTOS DISPONÍVEIS")
        items = get_cached_store_items()
        
        if not items.empty:
            # Grid Layout
            cols = st.columns(3)
            for idx, row in items.iterrows():
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div class="gamified-card" style="height: 100%;">
                            <h4 style="color: var(--neon-blue);">{row['name']}</h4>
                            <p style="color: #aaa; font-size: 0.9em; height: 60px; overflow: hidden;">{row['description']}</p>
                            <h3 style="color: var(--neon-green); margin: 10px 0;">{row['cost']} PTS</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("ADQUIRIR", key=f"buy_{row['id']}", use_container_width=True):
                            if current_balance >= row['cost']:
                                db.request_purchase(st.session_state.user['id'], row['id'])
                                st.toast("Solicitação enviada ao comando! 🛸")
                            else:
                                st.error("Saldo insuficiente para esta aquisição.")
        else:
            st.info("Arsenal vazio no momento.")

    with tab2:
        st.markdown("### 🏅 GALERIA DE CONQUISTAS")
        
        # Get all levels to show progress
        all_levels = db.get_level_config()
        
        # Display badges grid
        st.markdown("<div class='badge-container'>", unsafe_allow_html=True)
        for _, row in all_levels.iterrows():
            earned = current_balance >= row['min_points']
            is_current = row['level_name'] == current_level_name
            
            css_class = "earned" if earned else "locked"
            opacity = "1" if earned else "0.3"
            grayscale = "0" if earned else "1"
            
            # Dynamic Styles for Current Level
            border_style = "2px solid var(--neon-green)" if is_current else "1px solid rgba(0, 243, 255, 0.1)"
            box_shadow = "0 0 25px rgba(0, 255, 157, 0.3)" if is_current else "none"
            transform = "scale(1.05)" if is_current else "scale(1)"
            
            st.markdown(f"""
            <div class='badge-card {css_class}' style='opacity: {opacity}; filter: grayscale({grayscale}); border: {border_style}; box-shadow: {box_shadow}; transform: {transform}; transition: all 0.3s ease;'>
                <div class='badge-icon'>{row['badge_icon']}</div>
                <div style='font-weight:bold; color: var(--neon-blue); text-transform: uppercase;'>{row['level_name']}</div>
                <small style='color: #aaa;'>{row['min_points']} PTS</small>
                { "<div style='color: var(--neon-green); font-size: 0.8em; margin-top: 5px; font-weight: bold;'>⭐ ATUAL</div>" if is_current else "" }
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎯 CENTRO DE MISSÕES")
        
        # Filters
        filter_cols = st.columns([2, 1])
        with filter_cols[0]:
            filter_status = st.multiselect("Filtrar por Status", 
                                           options=["Em Andamento", "Disponíveis", "Concluídas", "Expiradas"],
                                           default=["Em Andamento", "Disponíveis"])
        
        my_missions = db.get_player_missions(st.session_state.user['id'])
        available = db.get_available_missions(st.session_state.user['id'])
        
        # Helper date
        today = datetime.now().strftime("%Y-%m-%d")

        # 1. Active Missions (Accepted & Valid)
        if "Em Andamento" in filter_status:
            st.markdown("#### 🔄 EM ANDAMENTO")
            # Filter accepted/pending/rejected and not expired
            active_missions = my_missions[
                (my_missions['status'].isin(['accepted', 'pending_validation', 'rejected'])) & 
                ((my_missions['deadline'].isna()) | (my_missions['deadline'] >= today) | (my_missions['deadline'] == ''))
            ]
            
            if not active_missions.empty:
                for _, m in active_missions.iterrows():
                    with st.container():
                        progress = m['progress'] if 'progress' in m else 0
                        status_display = "EM PROGRESSO ⏳"
                        border_color = "var(--neon-blue)"
                        
                        if m['status'] == 'pending_validation':
                            status_display = "EM ANÁLISE 🔍"
                            border_color = "orange"
                        elif m['status'] == 'rejected':
                            status_display = "REJEITADA ❌"
                            border_color = "#ff4b4b"
                        
                        st.markdown(f"""
                        <div class="gamified-card" style="border-left: 5px solid {border_color};">
                            <div style="display:flex; justify-content:space-between;">
                                <h4>{m['title']}</h4>
                                <span style="color:var(--neon-green); font-weight:bold;">+{m['reward']} PTS</span>
                            </div>
                            <p>{m['description']}</p>
                            <small style="color:#888;">Prazo: {format_brt_date(m['deadline']) if m['deadline'] else 'Sem prazo'}</small>
                            <div style="text-align:right; margin-top:5px; font-weight:bold; color:{border_color};">{status_display}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if m['status'] == 'accepted':
                            # Progress Bar
                            st.progress(int(progress))
                            st.caption(f"Progresso da Missão: {int(progress)}%")
                            
                            with st.expander("🔍 DETALHES & AÇÕES"):
                                st.write(f"**Requisitos:** {m.get('requirements', 'Consultar descrição')}")
                                if st.button("✅ SOLICITAR VALIDAÇÃO", key=f"req_val_{m['id']}"):
                                    success, msg = db.request_mission_validation(m['id'])
                                    if success:
                                        st.success(msg)
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                        elif m['status'] == 'pending_validation':
                            st.info("Sua missão está sob análise do comando. Aguarde a validação.")
                        elif m['status'] == 'rejected':
                            st.error("Sua validação anterior foi rejeitada. Verifique as notificações para saber o motivo.")
                            if st.button("🔄 REENVIAR PARA ANÁLISE", key=f"retry_{m['id']}"):
                                # Reset to accepted or directly request again? 
                                # Let's assume they fixed it and are requesting again.
                                success, msg = db.request_mission_validation(m['id'])
                                if success:
                                    st.success("Reenviada com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
            else:
                st.info("Nenhuma missão em andamento.")

        # 2. Available Missions
        if "Disponíveis" in filter_status:
            st.markdown("#### 🆕 DISPONÍVEIS PARA ACEITE")
            
            # Filter out expired from available
            valid_available = available[
                (available['deadline'].isna()) | (available['deadline'] >= today) | (available['deadline'] == '')
            ]
            
            if not valid_available.empty:
                for _, m in valid_available.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="gamified-card" style="border-left: 5px solid var(--neon-yellow);">
                            <div style="display:flex; justify-content:space-between;">
                                <h4>{m['title']}</h4>
                                <span style="color:var(--neon-green); font-weight:bold;">+{m['reward']} XP</span>
                            </div>
                            <p>{m['description']}</p>
                            <small style="color:#aaa;">Prazo: {format_brt_date(m['deadline']) if m['deadline'] else '∞'}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("ACEITAR DESAFIO", key=f"accept_{m['id']}"):
                            success, msg = db.accept_mission(st.session_state.user['id'], m['id'])
                            if success:
                                st.toast(msg, icon="🚀")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
            else:
                st.info("Nenhuma nova missão disponível no momento.")
            
        # 3. Completed History
        if "Concluídas" in filter_status:
            st.markdown("#### ✅ HISTÓRICO DE SUCESSO")
            completed = my_missions[my_missions['status'] == 'completed']
            if not completed.empty:
                 for _, m in completed.iterrows():
                     st.markdown(f"""
                     <div class="gamified-card" style="border-left: 5px solid var(--neon-green); opacity: 0.7;">
                        <div style="display:flex; justify-content:space-between;">
                            <h4 style="text-decoration: line-through; color: #888;">{m['title']}</h4>
                            <span style="color:var(--neon-green);">CONCLUÍDA</span>
                        </div>
                        <p style="color: #666;">{m['description']}</p>
                        <small style="color: #666;">Data: {format_brt(m['completed_at'])}</small>
                     </div>
                     """, unsafe_allow_html=True)
            else:
                st.info("Nenhuma missão concluída ainda.")
        
        # 4. Expired
        if "Expiradas" in filter_status:
            st.markdown("#### ⚠️ EXPIRADAS / FALHADAS")
            # Accepted but expired
            expired_missions = my_missions[
                (my_missions['status'] == 'accepted') & 
                (my_missions['deadline'] < today) & 
                (my_missions['deadline'] != '') & 
                (my_missions['deadline'].notna())
            ]
            
            if not expired_missions.empty:
                 for _, m in expired_missions.iterrows():
                     st.markdown(f"""
                     <div class="gamified-card" style="border-left: 5px solid #ff4b4b; opacity: 0.6;">
                        <div style="display:flex; justify-content:space-between;">
                            <h4 style="color: #ff4b4b;">{m['title']}</h4>
                            <span style="color:#ff4b4b;">EXPIRADA</span>
                        </div>
                        <p>{m['description']}</p>
                        <small style="color: #ff4b4b;">Prazo era: {format_brt_date(m['deadline'])}</small>
                     </div>
                     """, unsafe_allow_html=True)
            else:
                st.info("Nenhuma missão expirada.")

    with tab3:
        st.markdown("### 📜 HISTÓRICO DE OPERAÇÕES")
        history = db.get_user_history(st.session_state.user['id'])
        
        if not history.empty:
            st.markdown("<div class='timeline'>", unsafe_allow_html=True)
            for _, row in history.iterrows():
                color = "var(--neon-green)" if row['type'] == 'EARN' else "#ff4b4b"
                icon = "➕" if row['type'] == 'EARN' else "➖"
                if row['type'] == 'SPEND': icon = "🛒"
                
                st.markdown(f"""
                <div class='timeline-item'>
                    <div class='timeline-dot' style='border-color: {color}; box-shadow: 0 0 10px {color};'></div>
                    <div class='timeline-content' style='border-left-color: {color};'>
                        <div style='display:flex; justify-content:space-between;'>
                            <strong style='color:{color}'>{icon} {row['type']}</strong>
                            <span style='color:#888; font-size:0.8em;'>{format_brt(row['timestamp'])}</span>
                        </div>
                        <div style='font-size: 1.2em; color: white;'>{row['amount']} PTS</div>
                        <div style='color: #aaa;'>{row['description']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Sem registros operacionais.")

    with tab4:
        st.markdown("### COMUNICAÇÕES")
        if not notifs.empty:
            for _, row in notifs.iterrows():
                bg = "rgba(0, 255, 157, 0.1)" if row['is_read'] == 0 else "transparent"
                border = "1px solid var(--neon-green)" if row['is_read'] == 0 else "1px solid #333"
                
                st.markdown(f"""
                <div style="background: {bg}; border: {border}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                    <p style="margin: 0;">{row['message']}</p>
                    <small style="color: #666;">{format_brt(row['timestamp'])}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Marcar como lido automaticamente ao renderizar (simples)
                if row['is_read'] == 0:
                    db.mark_notification_read(row['id'])
        else:
            st.info("Nenhuma nova mensagem.")

# --- ROTEAMENTO ---
if st.session_state.user is None:
    # Check cookie just in case logic above missed it or to support refresh if session cleared
    # (Actually, we handled cookie check at startup in 'login' block implicitly? No.)
    # I added cookie check logic? Wait.
    # I added `cookie_manager = get_manager()` at top.
    # But I did NOT add the logic to *restore* the session from cookie if st.session_state.user is None.
    # I should add it here or at the top. 
    # Adding it here is safer before deciding to show login.
    
    cookies = cookie_manager.get_all()
    user_email = cookies.get("user_email")
    
    if user_email:
        # Try to auto-login
        user = db.get_user_by_email(user_email)
        if user:
            st.session_state.user = {'id': user[0], 'username': user[1], 'role': user[2], 'balance': user[3]}
            st.rerun()
    
    # If still None, show login/register tabs
    tab_login, tab_register = st.tabs(["🔐 LOGIN", "📝 REGISTRAR"])
    with tab_login:
        login()
    with tab_register:
        register()
else:
    if st.session_state.user['role'] == 'Administrador':
        admin_dashboard()
    else:
        player_dashboard()
