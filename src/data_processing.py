import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def _request_with_retry(url, max_retries=3, timeout=10):
    """
    Faz uma requisição GET com retry automático em caso de erros de conexão.
    Aguarda 2^tentativa segundos entre cada retry (backoff exponencial).
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            return response
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            wait_time = 2 ** attempt  # 1s, 2s, 4s...
            print(f"  ⚠️  Erro de conexão (tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"  ⏳ Aguardando {wait_time}s antes de tentar novamente...")
                time.sleep(wait_time)
    return None  # Retorna None se todas as tentativas falharem

def fetch_tmdb_data(api_key, max_pages=25):
    """
    Busca dados na API do TMDb e retorna uma lista de dicionários com detalhes dos filmes.
    Inclui retry automático e delay entre requisições para evitar rate limit.
    """
    base_url = "https://api.themoviedb.org/3"
    movies_data = []
    ids_vistos = set()  # evita duplicatas

    for page in range(1, max_pages + 1):
        print(f"📄 Baixando página {page}/{max_pages}...")
        url_discover = (
            f"{base_url}/discover/movie?api_key={api_key}"
            f"&language=pt-BR&sort_by=popularity.desc&page={page}"
        )
        response = _request_with_retry(url_discover)

        if response is None or response.status_code != 200:
            status = response.status_code if response else "sem resposta"
            print(f"  ❌ Falha na página {page} (status: {status}). Pulando...")
            time.sleep(3)
            continue

        results = response.json().get('results', [])

        for i, movie in enumerate(results):
            movie_id = movie['id']
            if movie_id in ids_vistos:
                continue
            ids_vistos.add(movie_id)

            # Delay leve para não sobrecarregar a API
            time.sleep(0.25)

            url_detail = (
                f"{base_url}/movie/{movie_id}?api_key={api_key}"
                f"&language=pt-BR&append_to_response=credits"
            )
            detail_res = _request_with_retry(url_detail)

            if detail_res is None or detail_res.status_code != 200:
                print(f"  ⚠️  Filme ID={movie_id} ignorado (falha na requisição).")
                continue

            detail = detail_res.json()

            crew = detail.get('credits', {}).get('crew', [])
            director = next(
                (m['name'] for m in crew if m['job'] == 'Director'), 'Desconhecido'
            )

            genres = [g['name'] for g in detail.get('genres', [])]
            genre = genres[0] if genres else 'Desconhecido'

            poster_path = detail.get('poster_path')
            poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None

            movies_data.append({
                'id': movie_id,
                'titulo': detail.get('title'),
                'ano': detail.get('release_date', ''),
                'genero': genre,
                'nota': detail.get('vote_average'),
                'votos': detail.get('vote_count', 0),
                'orcamento': detail.get('budget', 0),
                'receita': detail.get('revenue', 0),
                'diretor': director,
                'poster': poster_url,
                'sinopse': detail.get('overview', 'Sinopse não disponível.'),
                'duracao': detail.get('runtime', 0),
                'popularidade': detail.get('popularity', 0),
            })

        print(f"  ✅ {len(movies_data)} filmes coletados até agora.")

    return movies_data


def get_cleaned_data(file_path='data/movies.csv'):
    """
    Carrega os dados do CSV (ou da API se o CSV não existir), limpa e cria colunas derivadas.
    """
    if not os.path.exists(file_path):
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key or api_key == "sua_chave_aqui":
            raise ValueError(
                "Arquivo CSV não encontrado e Chave da API do TMDb não configurada no .env!"
            )

        print("🔍 CSV não encontrado. Buscando dados da API do TMDb...")
        print("⏱️  Isso pode levar alguns minutos. Aguarde...")
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        raw_data = fetch_tmdb_data(api_key, max_pages=50)  # ~1000 filmes
        df_raw = pd.DataFrame(raw_data)
        df_raw.to_csv(file_path, index=False)
        print(f"🎉 Dados salvos em {file_path}! ({len(df_raw)} filmes)")

    # Ler os dados
    df = pd.read_csv(file_path)

    # 1. Tratar valores nulos / vazios
    df = df.dropna(subset=['titulo'])
    df = df[df['ano'].notna() & (df['ano'].astype(str).str.strip() != '')]

    # 2. Converter ano para datetime e extrair ano e década
    df['ano_lancamento'] = pd.to_datetime(df['ano'], errors='coerce')
    df = df.dropna(subset=['ano_lancamento'])
    df['ano_str'] = df['ano_lancamento'].dt.year.astype(int)
    df['decada'] = (df['ano_str'] // 10) * 10
    df['decada'] = df['decada'].astype(str) + 's'

    # 3. Criar coluna de retorno financeiro
    df['retorno_financeiro'] = df['receita'] - df['orcamento']

    return df


if __name__ == "__main__":
    df = get_cleaned_data()
    print(df.head())
    print(df.info())
