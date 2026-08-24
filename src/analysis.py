import pandas as pd

def top_10_lucrativos(df):
    """Retorna os top 10 filmes com maior retorno financeiro."""
    return df.nlargest(10, 'retorno_financeiro')[['titulo', 'retorno_financeiro', 'ano_str']]

def media_notas_por_genero(df):
    """Retorna a média de notas por gênero, ordenado."""
    return df.groupby('genero')['nota'].mean().sort_values(ascending=False).reset_index()

def diretores_mais_bem_avaliados(df, min_filmes=1):
    """Retorna os diretores mais bem avaliados (com pelo menos N filmes)."""
    agrupado = df.groupby('diretor').agg({'nota': 'mean', 'titulo': 'count'})
    agrupado = agrupado[agrupado['titulo'] >= min_filmes]
    return agrupado.sort_values(by='nota', ascending=False).reset_index().head(10)

def distribuicao_decadas(df):
    """Conta filmes por década."""
    return df['decada'].value_counts().reset_index()

def media_notas_por_ano(df):
    """Média de notas agregadas por ano."""
    return df.groupby('ano_str')['nota'].mean().reset_index()

if __name__ == "__main__":
    from data_processing import get_cleaned_data
    df = get_cleaned_data('../data/movies.csv')
    print("--- TOP 10 Lucrativos ---")
    print(top_10_lucrativos(df))
    print("\n--- Média por Gênero ---")
    print(media_notas_por_genero(df))
    print("\n--- Top Diretores ---")
    print(diretores_mais_bem_avaliados(df))
