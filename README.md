# Dash Filmes 🎬

Um dashboard interativo sobre filmes, construído com Streamlit, Pandas e Plotly. Os dados são consumidos a partir da API do TMDb.

## Funcionalidades
- Filtros interativos (Gênero, Ano, Diretor).
- Principais Indicadores (KPIs) de filmes, como nota média e receita.
- Vitrine dos filmes top avaliados.
- Detalhamento de filmes em estilo plataforma de streaming.
- Gráficos de análise variados.
- Comparador visual estilo duelo (Radar Chart) entre filmes.

## Como Executar Localmente

1. Clone este repositório:
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd dash-filmes
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure a chave da API:
   - Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base).
   - Insira sua chave do TMDb:
     ```env
     TMDB_API_KEY=sua_chave_aqui
     ```

5. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## Estrutura do Projeto
- `app.py`: Arquivo principal da interface gráfica em Streamlit.
- `src/`: Lógicas de processamento e análise de dados.
- `data/`: Armazenamento local do CSV extraído da API.
- `requirements.txt`: Lista de dependências do projeto.

## Atribuição
Este produto utiliza a API do [TMDb (The Movie Database)](https://www.themoviedb.org/), mas não é endossado ou certificado pelo TMDb.

