import feedparser
import pandas as pd
from datetime import datetime
import os
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Fontes ampliadas para cobrir Hotspots de Conflito
rss_sources = {
    # --- AMÉRICAS ---
    'NYT_World': {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', 'regiao': 'USA'},
    'G1_Mundo': {'url': 'https://g1.globo.com/dynamo/mundo/rss2.xml', 'regiao': 'Brasil'},
    
    # --- EUROPA/RUSSIA/UCRÂNIA ---
    'BBC_World': {'url': 'http://feeds.bbci.co.uk/news/world/rss.xml', 'regiao': 'Europa'},
    'TASS_Russia': {'url': 'https://tass.com/rss/v2.xml', 'regiao': 'Russia'}, # Estatal Russa
    'KyivIndependent': {'url': 'https://kyivindependent.com/rss/', 'regiao': 'Ucrania'}, # Visão Ucraniana
    
    # --- ORIENTE MÉDIO (Israel/Irã) ---
    'Jerusalem_Post': {'url': 'https://www.jpost.com/rss/rssfeedsheadlines.aspx', 'regiao': 'Israel'},
    'AlJazeera_English': {'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'regiao': 'Oriente_Medio'},
    'Tehran_Times': {'url': 'https://www.tehrantimes.com/rss', 'regiao': 'Ira'}, # Visão Iraniana
    
    # --- ÁSIA (China/Taiwan) ---
    'Global_Times_China': {'url': 'https://www.globaltimes.cn/rss/index.xml', 'regiao': 'China'},
    'Taipei_Times': {'url': 'https://www.taipeitimes.com/xml/index.xml', 'regiao': 'Taiwan'}
}

def coletar_noticias():
    print(f"--- Iniciando Coleta Global 2.0: {datetime.now()} ---")
    noticias = []

    for nome_fonte, info in rss_sources.items():
        try:
            print(f"📡 Lendo {info['regiao']} -> {nome_fonte}...")
            feed = feedparser.parse(info['url'])
            
            for entry in feed.entries:
                noticia = {
                    'data_coleta': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'regiao': info['regiao'],
                    'fonte': nome_fonte,
                    'titulo': entry.title,
                    'link': entry.link,
                    'resumo': entry.get('summary', '')
                }
                noticias.append(noticia)
        except Exception as e:
            print(f"   ❌ Erro em {nome_fonte}: {e}")

    if not noticias:
        return pd.DataFrame()

    df = pd.DataFrame(noticias)
    df.drop_duplicates(subset=['titulo', 'fonte'], inplace=True)
    return df

def salvar_dados(df):
    os.makedirs('data', exist_ok=True)
    arquivo_csv = 'data/noticias_global.csv'
    
    if os.path.exists(arquivo_csv):
        df_historico = pd.read_csv(arquivo_csv)
        novas = df[~df['link'].isin(df_historico['link'])]
        if not novas.empty:
            novas.to_csv(arquivo_csv, mode='a', header=False, index=False)
            print(f"💾 {len(novas)} novas notícias adicionadas.")
    else:
        df.to_csv(arquivo_csv, index=False)
        print("📁 Arquivo criado.")

if __name__ == "__main__":
    df = coletar_noticias()
    if not df.empty:
        salvar_dados(df)