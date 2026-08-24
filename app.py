import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_processing import get_cleaned_data
from src.analysis import (
    top_10_lucrativos, 
    media_notas_por_genero, 
    diretores_mais_bem_avaliados, 
    media_notas_por_ano
)

# Configuração da Página
st.set_page_config(
    page_title="Dashboard de Filmes",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada para visual mais "Premium"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Estilo do título principal */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    /* Estilo das métricas */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #FF416C;
    }

    /* Card estilo streaming */
    .movie-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 28px;
        border: 1px solid rgba(255, 65, 108, 0.25);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        margin-bottom: 12px;
    }
    .movie-title {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }
    .movie-meta {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #aaa;
        margin-bottom: 16px;
    }
    .movie-badge {
        display: inline-block;
        background: rgba(255, 65, 108, 0.2);
        border: 1px solid rgba(255, 65, 108, 0.5);
        color: #FF416C;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .movie-synopsis {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #ddd;
        line-height: 1.7;
        margin-top: 14px;
        border-left: 3px solid #FF416C;
        padding-left: 14px;
    }
    .rating-star {
        color: #FFD700;
        font-size: 1.3rem;
        font-weight: 700;
    }

    /* Comparador */
    .compare-card {
        background: linear-gradient(160deg, #12122a 0%, #1e1e3a 100%);
        border-radius: 14px;
        padding: 22px;
        border: 1px solid rgba(130, 80, 255, 0.3);
        box-shadow: 0 6px 24px rgba(0,0,0,0.5);
        height: 100%;
    }
    .compare-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #fff;
        margin: 10px 0 4px 0;
    }
    .compare-meta {
        font-size: 0.82rem;
        color: #999;
        margin-bottom: 10px;
    }
    .compare-synopsis {
        font-size: 0.88rem;
        color: #ccc;
        line-height: 1.6;
        border-left: 3px solid #8250ff;
        padding-left: 12px;
        margin-top: 10px;
        display: -webkit-box;
        -webkit-line-clamp: 5;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .vs-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 900;
        color: #FF416C;
        text-shadow: 0 0 20px rgba(255,65,108,0.6);
        height: 100%;
        padding-top: 140px;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar os dados
@st.cache_data
def load_data():
    try:
        return get_cleaned_data('data/movies.csv')
    except ValueError as e:
        st.error(f"Erro: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Erro inesperado ao carregar dados: {e}")
        st.stop()

# Inicialização
st.markdown('<p class="main-title">🎬 Movie Insights Dashboard</p>', unsafe_allow_html=True)
st.write("Explore dados de filmes populares, tendências e retornos financeiros usando dados do TMDb.")

# Carregar e preparar os dados
df = load_data()

if df.empty:
    st.warning("O dataset está vazio. Tente alterar os parâmetros ou verifique a extração.")
    st.stop()

# --- SIDEBAR (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Gênero
generos_disponiveis = df['genero'].dropna().unique().tolist()
generos_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Gênero(s):",
    options=generos_disponiveis,
    default=generos_disponiveis[:3] if len(generos_disponiveis) > 3 else generos_disponiveis
)

# Filtro de Ano
min_ano = int(df['ano_str'].min())
max_ano = int(df['ano_str'].max())
ano_selecionado = st.sidebar.slider(
    "Selecione o Intervalo de Anos:",
    min_value=min_ano,
    max_value=max_ano,
    value=(min_ano, max_ano)
)

# Filtro de Diretor
diretores_disponiveis = df['diretor'].dropna().unique().tolist()
diretor_selecionado = st.sidebar.selectbox(
    "Filtrar por Diretor (opcional):",
    options=["Todos"] + sorted(diretores_disponiveis)
)

# Aplicação dos Filtros
df_filtrado = df.copy()

if generos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['genero'].isin(generos_selecionados)]

df_filtrado = df_filtrado[
    (df_filtrado['ano_str'] >= ano_selecionado[0]) & 
    (df_filtrado['ano_str'] <= ano_selecionado[1])
]

if diretor_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['diretor'] == diretor_selecionado]

# --- KPIs ---
st.markdown("### 📊 Principais Indicadores")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Filmes", f"{len(df_filtrado)}")
with col2:
    nota_media = df_filtrado['nota'].mean()
    st.metric("Nota Média Global", f"{nota_media:.1f}" if pd.notna(nota_media) else "N/A")
with col3:
    maior_receita = df_filtrado['receita'].max()
    st.metric("Maior Receita ($)", f"{maior_receita / 1e6:.1f}M" if pd.notna(maior_receita) else "N/A")
with col4:
    melhor_genero = df_filtrado.groupby('genero')['nota'].mean().idxmax() if not df_filtrado.empty else "N/A"
    st.metric("Gênero Top Avaliado", melhor_genero)

st.divider()

# --- VITRINE / GALERIA ---
st.markdown("### 🍿 Vitrine de Filmes (Top 5 Avaliados)")
# Usar a coluna 'poster' adicionada agora
if 'poster' in df_filtrado.columns:
    top_5_filmes = df_filtrado.dropna(subset=['poster']).nlargest(5, 'nota')
    if not top_5_filmes.empty:
        cols = st.columns(len(top_5_filmes))
        for idx, (_, filme) in enumerate(top_5_filmes.iterrows()):
            with cols[idx]:
                st.image(filme['poster'], width='stretch')
                st.markdown(f"**{filme['titulo']}**")
                st.caption(f"⭐ {filme['nota']} | 📅 {filme['ano_str']}")
    else:
        st.info("Nenhum filme com capa encontrado para estes filtros.")
else:
    st.warning("A coluna de capas não foi encontrada. Force a extração novamente deletando o arquivo movies.csv.")

st.divider()

# --- DETALHES DO FILME (estilo streaming) ---
st.markdown("### 🎞️ Detalhes do Filme")

_tem_sinopse = 'sinopse' in df_filtrado.columns
_filmes_opcoes = df_filtrado['titulo'].dropna().sort_values().unique().tolist()

if _filmes_opcoes:
    filme_selecionado_nome = st.selectbox(
        "Selecione um filme para ver os detalhes:",
        options=_filmes_opcoes,
        index=0
    )

    _filme = df_filtrado[df_filtrado['titulo'] == filme_selecionado_nome].iloc[0]

    col_poster, col_info = st.columns([1, 2.8], gap="large")

    with col_poster:
        if pd.notna(_filme.get('poster')):
            st.image(_filme['poster'], width='stretch')
        else:
            st.markdown(
                '<div style="background:#1a1a2e;border-radius:12px;height:360px;display:flex;'
                'align-items:center;justify-content:center;color:#555;font-size:3rem;">🎬</div>',
                unsafe_allow_html=True
            )

    with col_info:
        # Monta a nota
        nota_val = _filme.get('nota', 0)
        nota_str = f"{nota_val:.1f}" if pd.notna(nota_val) else "N/A"
        duracao = int(_filme.get('duracao', 0) or 0)
        votos = int(_filme.get('votos', 0) or 0)
        ano_exib = int(_filme.get('ano_str', 0))

        # Badges
        badges_html = ""
        for badge in [_filme.get('genero'), _filme.get('decada')]:
            if badge and badge != 'Desconhecido':
                badges_html += f'<span class="movie-badge">{badge}</span>'

        duracao_str = f"{duracao // 60}h {duracao % 60}min" if duracao > 0 else "—"

        st.markdown(f"""
        <div class="movie-card">
            <p class="movie-title">{_filme['titulo']}</p>
            <p class="movie-meta">
                📅 {ano_exib} &nbsp;|&nbsp;
                🎬 Dirigido por <strong style="color:#eee">{_filme.get('diretor', '—')}</strong> &nbsp;|&nbsp;
                ⏱️ {duracao_str}
            </p>
            <div>{badges_html}</div>
            <p style="margin:14px 0 4px 0;">
                <span class="rating-star">★</span>
                <span style="color:#FFD700;font-size:1.4rem;font-weight:700;"> {nota_str}</span>
                <span style="color:#888;font-size:0.85rem;"> / 10 &nbsp;·&nbsp; {votos:,} votos</span>
            </p>
            <p class="movie-synopsis">{_filme.get('sinopse', 'Sinopse não disponível.') if _tem_sinopse else '⚠️ Para ver a sinopse, delete o arquivo data/movies.csv e reinicie o servidor para uma nova extração.'}</p>
        </div>
        """, unsafe_allow_html=True)

        # Métricas financeiras abaixo do card
        orc = _filme.get('orcamento', 0) or 0
        rec = _filme.get('receita', 0) or 0
        ret = _filme.get('retorno_financeiro', 0) or 0

        m1, m2, m3 = st.columns(3)
        m1.metric("💵 Orçamento", f"${orc/1e6:.1f}M" if orc > 0 else "N/D")
        m2.metric("💰 Receita", f"${rec/1e6:.1f}M" if rec > 0 else "N/D")
        m3.metric(
            "📈 Retorno",
            f"${ret/1e6:.1f}M" if (orc > 0 and rec > 0) else "N/D",
            delta=f"+{((rec/orc - 1)*100):.0f}%" if orc > 0 and rec > 0 else None
        )
else:
    st.info("Nenhum filme encontrado com os filtros aplicados.")

# --- GRÁFICOS ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 🏆 Gêneros Mais Bem Avaliados")
    df_genero = media_notas_por_genero(df_filtrado).head(10)
    fig_bar = px.bar(
        df_genero, x='genero', y='nota', 
        color='nota', color_continuous_scale='Sunsetdark',
        labels={'genero': 'Gênero', 'nota': 'Nota Média'},
        template='plotly_dark'
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, width='stretch')

with col_right:
    st.markdown("#### 📈 Evolução das Notas Médias por Ano")
    df_ano = media_notas_por_ano(df_filtrado)
    fig_line = px.line(
        df_ano, x='ano_str', y='nota', markers=True,
        line_shape='spline',
        labels={'ano_str': 'Ano', 'nota': 'Nota Média'},
        template='plotly_dark'
    )
    fig_line.update_traces(line_color='#FF416C', line_width=3)
    st.plotly_chart(fig_line, width='stretch')

st.divider()

col_bottom_left, col_bottom_right = st.columns(2)

with col_bottom_left:
    st.markdown("#### 💰 Orçamento vs Receita")
    # Filtrar apenas filmes que tem orçamento e receita maior que zero para o scatter plot
    df_scatter = df_filtrado[(df_filtrado['orcamento'] > 0) & (df_filtrado['receita'] > 0)]
    fig_scatter = px.scatter(
        df_scatter, x='orcamento', y='receita', 
        size='nota', color='genero', hover_name='titulo',
        labels={'orcamento': 'Orçamento ($)', 'receita': 'Receita ($)'},
        template='plotly_dark',
        log_x=True, log_y=True # Usar escala logaritmica por causa da variação
    )
    st.plotly_chart(fig_scatter, width='stretch')

with col_bottom_right:
    st.markdown("#### 🎬 Distribuição de Notas")
    fig_hist = px.histogram(
        df_filtrado, x='nota', nbins=20,
        color_discrete_sequence=['#FF4B2B'],
        labels={'nota': 'Nota'},
        template='plotly_dark',
        opacity=0.8
    )
    fig_hist.update_layout(yaxis_title="Quantidade de Filmes")
    st.plotly_chart(fig_hist, width='stretch')

st.divider()

# --- TOP LUCRATIVOS & DIRETORES ---
st.markdown("#### 🚀 Top 10 Filmes com Maior Retorno Financeiro")
top_lucrativos = top_10_lucrativos(df_filtrado)
# Formatação do DataFrame
if not top_lucrativos.empty:
    top_lucrativos['retorno_financeiro'] = top_lucrativos['retorno_financeiro'].apply(lambda x: f"${x:,.2f}")
st.dataframe(top_lucrativos, width='stretch', hide_index=True)

st.markdown("#### 🎥 Diretores Mais Bem Avaliados")
top_diretores = diretores_mais_bem_avaliados(df_filtrado)
st.dataframe(top_diretores, width='stretch', hide_index=True)

st.divider()

# --- COMPARADOR DE FILMES ---
st.markdown("### ⚖️ Comparador de Filmes")
st.caption("Escolha dois filmes para comparar lado a lado, estilo duelo!")

_todos_filmes = df['titulo'].dropna().sort_values().unique().tolist()

cc1, cc_vs, cc2 = st.columns([5, 1, 5], gap="small")

with cc1:
    filme_a_nome = st.selectbox("Filme A", options=_todos_filmes, index=0, key="comp_a")
with cc_vs:
    st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
with cc2:
    _default_b = min(1, len(_todos_filmes) - 1)
    filme_b_nome = st.selectbox("Filme B", options=_todos_filmes, index=_default_b, key="comp_b")

if filme_a_nome and filme_b_nome:
    fa = df[df['titulo'] == filme_a_nome].iloc[0]
    fb = df[df['titulo'] == filme_b_nome].iloc[0]

    def _render_compare_card(f, accent):
        """Renderiza o card de um filme no comparador."""
        nota = f.get('nota', 0) or 0
        duracao = int(f.get('duracao', 0) or 0)
        duracao_str = f"{duracao // 60}h {duracao % 60}min" if duracao > 0 else "—"
        orc = f.get('orcamento', 0) or 0
        rec = f.get('receita', 0) or 0
        ret = f.get('retorno_financeiro', 0) or 0
        sinopse = f.get('sinopse', '') or 'Sinopse não disponível.'

        if pd.notna(f.get('poster')):
            st.image(f['poster'], width='stretch')

        border_color = accent
        st.markdown(f"""
        <div class="compare-card" style="border-color: {border_color}33; box-shadow: 0 0 20px {border_color}22;">
            <p class="compare-title">{f['titulo']}</p>
            <p class="compare-meta">
                📅 {int(f.get('ano_str', 0))} &nbsp;·&nbsp;
                🎬 {f.get('diretor', '—')} &nbsp;·&nbsp;
                ⏱️ {duracao_str}
            </p>
            <p style="margin:6px 0;">
                <span style="color:#FFD700;font-size:1.3rem;font-weight:700;">&#9733; {nota:.1f}</span>
                <span style="color:#888;font-size:0.82rem;"> / 10</span>
                &nbsp;&nbsp;
                <span style="background:{accent}33;border:1px solid {accent}88;color:{accent};
                             border-radius:20px;padding:2px 10px;font-size:0.78rem;font-weight:600;">
                    {f.get('genero', '—')}
                </span>
            </p>
            <p class="compare-synopsis" style="border-left-color:{accent};">{sinopse}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        m1, m2, m3 = st.columns(3)
        m1.metric("💵 Orçamento", f"${orc/1e6:.1f}M" if orc > 0 else "N/D")
        m2.metric("💰 Receita",   f"${rec/1e6:.1f}M" if rec > 0 else "N/D")
        m3.metric("📈 Retorno",   f"${ret/1e6:.1f}M" if (orc > 0 and rec > 0) else "N/D",
                  delta=f"+{((rec/orc - 1)*100):.0f}%" if orc > 0 and rec > 0 else None)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        _render_compare_card(fa, "#FF416C")
    with col_b:
        _render_compare_card(fb, "#8250ff")

    # --- Gráfico de radar comparativo ---
    st.markdown("#### 📊 Comparativo Visual")
    import plotly.graph_objects as go

    def _normalizar(val, max_val):
        return round((val / max_val) * 10, 2) if max_val > 0 else 0

    max_orc = df['orcamento'].max() or 1
    max_rec = df['receita'].max() or 1
    max_ret = df['retorno_financeiro'].max() or 1
    max_pop = df['popularidade'].max() if 'popularidade' in df.columns else 1

    categorias = ['Nota', 'Orçamento', 'Receita', 'Retorno', 'Popularidade']

    def _valores(f):
        return [
            float(f.get('nota', 0) or 0),
            _normalizar(float(f.get('orcamento', 0) or 0), max_orc),
            _normalizar(float(f.get('receita', 0) or 0), max_rec),
            _normalizar(float(f.get('retorno_financeiro', 0) or 0), max_ret),
            _normalizar(float(f.get('popularidade', 0) or 0), max_pop),
        ]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=_valores(fa), theta=categorias, fill='toself',
        name=fa['titulo'], line_color='#FF416C', fillcolor='rgba(255,65,108,0.15)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=_valores(fb), theta=categorias, fill='toself',
        name=fb['titulo'], line_color='#8250ff', fillcolor='rgba(130,80,255,0.15)'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        template='plotly_dark',
        legend=dict(font=dict(size=13)),
        margin=dict(t=40, b=40)
    )
    st.plotly_chart(fig_radar, width='stretch')
