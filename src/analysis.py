import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import time

# --- Configurações ---
ARQUIVO_INPUT = 'data/noticias_global.csv'
ARQUIVO_OUTPUT = 'data/dados_processados.csv'

# Dicionário do Fim do Mundo
# Se estas palavras aparecem, o peso da notícia aumenta drasticamente.
PALAVRAS_CHAVE = {
    'nuclear': 5.0,
    'war': 3.0,
    'missile': 3.0,
    'putin': 2.0,
    'trump': 2.0,
    'nato': 2.5,
    'china': 1.5,
    'strike': 2.0,
    'military': 1.5,
    'escalation': 3.0,
    'threat': 2.0
}

def traduzir_texto(texto):
    """Traduz para inglês usando o Google Translate (free version)"""
    if not isinstance(texto, str) or len(texto) < 3:
        return ""
    try:
        # A deep-translator é ótima, mas pode ser lenta se tiver muitas linhas.
        # Em produção real, usaríamos uma API paga.
        tradutor = GoogleTranslator(source='auto', target='en')
        return tradutor.translate(texto)
    except Exception as e:
        return texto # Se falhar, retorna o original

def analisar_risco(df):
    analyzer = SentimentIntensityAnalyzer()
    
    print("--- Iniciando Análise de Inteligência ---")
    
    resultados = []
    
    # Vamos iterar apenas nas notícias novas (que ainda não têm score)
    # Se o arquivo de saída já existe, carregamos ele para não reprocessar tudo
    ids_processados = []
    if pd.io.common.file_exists(ARQUIVO_OUTPUT):
        df_antigo = pd.read_csv(ARQUIVO_OUTPUT)
        ids_processados = df_antigo['link'].tolist()
        resultados = df_antigo.to_dict('records')

    # Filtra para processar só o que é novo
    df_novo = df[~df['link'].isin(ids_processados)].copy()
    print(f"Novas notícias para processar: {len(df_novo)}")

    for index, row in df_novo.iterrows():
        titulo_orig = row['titulo']
        regiao = row['regiao']
        
        # 1. TRADUÇÃO (Normalização)
        # Só traduz se não for das fontes em inglês para economizar tempo
        if regiao in ['Brasil', 'Europa'] and 'BBC' not in row['fonte']: 
            texto_en = traduzir_texto(titulo_orig)
            # Pequeno delay para não bloquear o IP do tradutor
            time.sleep(0.5) 
        else:
            texto_en = titulo_orig
            
        # 2. ANÁLISE DE SENTIMENTO (VADER)
        # O VADER retorna 'compound': -1 (Muito Negativo) a +1 (Muito Positivo)
        scores = analyzer.polarity_scores(texto_en)
        sentimento = scores['compound']
        
        # 3. PESO DAS PALAVRAS (Keyword Matching)
        peso_palavras = 0
        texto_lower = texto_en.lower()
        
        palavras_encontradas = []
        for palavra, peso in PALAVRAS_CHAVE.items():
            if palavra in texto_lower:
                peso_palavras += peso
                palavras_encontradas.append(palavra)
        
        # 4. CÁLCULO DO SCORE DE "DOOM" (A Lógica do Relógio)
        # Lógica: Sentimento Negativo + Palavras de Guerra = ALTO RISCO
        # Se sentimento for negativo (ex: -0.5), invertemos para somar ao risco
        
        fator_medo = 0
        if sentimento < 0:
            fator_medo = abs(sentimento) * 10 # Transforma -0.5 em +5 pontos de medo
        
        # O Score Final é a soma do medo (sentimento) + peso das palavras (contexto)
        score_risco = fator_medo + peso_palavras
        
        print(f"[{regiao}] Risco: {score_risco:.2f} | Termos: {palavras_encontradas} | {texto_en[:50]}...")

        nova_linha = row.to_dict()
        nova_linha['titulo_en'] = texto_en
        nova_linha['sentimento'] = sentimento
        nova_linha['score_risco'] = score_risco
        nova_linha['palavras_chave'] = ", ".join(palavras_encontradas)
        
        resultados.append(nova_linha)

    # Salva tudo
    df_final = pd.DataFrame(resultados)
    df_final.to_csv(ARQUIVO_OUTPUT, index=False)
    print(f"--- Processamento Concluído. Dados salvos em {ARQUIVO_OUTPUT} ---")

if __name__ == "__main__":
    try:
        df_raw = pd.read_csv(ARQUIVO_INPUT)
        analisar_risco(df_raw)
    except FileNotFoundError:
        print("Erro: Rode o 'collector.py' primeiro para gerar os dados!")