# ☢️ Doomsday Clock AI

Sistema experimental de monitoramento de risco existencial inspirado no Doomsday Clock oficial do Bulletin of the Atomic Scientists.

O projeto combina:
- 📡 Coleta automática de notícias globais via RSS
- 🧠 Análise de sentimento com VADER
- 🗂️ Classificação temática (Nuclear, Guerra, Clima, Política, etc.)
- 📊 Cálculo de risco global (0..1)
- 🕒 Conversão para "minutos até meia-noite"
- 📈 Histórico oficial desde 1947
- 🔍 Comparação entre modelo AI e valor oficial do Bulletin

---

## 🎯 Objetivo

Criar um indicador experimental de risco global baseado em dados públicos, mantendo arquitetura limpa (DDD + SOLID) e stack 100% portátil.

---

## 🏗️ Arquitetura

Estrutura baseada em DDD:
DoomsdayClock/
│
├── data/ # SQLite database
├── src/
│ ├── domain/ # Regras de negócio puras
│ ├── application/ # Use cases
│ ├── infra/ # SQLite, RSS, scraping oficial
│ ├── app.py # Interface Streamlit
│
├── requirements.txt
└── README.md




### Camadas

- **Domain:** scoring, categorias, conversões
- **Application:** orquestra pipeline (collect → score → persist)
- **Infrastructure:** SQLite + scraping + RSS
- **UI:** Streamlit

---

## 🧠 Stack Tecnológica

- Python 3.10+
- SQLite (zero servidor)
- Streamlit
- VADER (vaderSentiment)
- Pandas
- Plotly
- BeautifulSoup
- lxml

---

## ⚙️ Instalação Local

### 1️⃣ Clonar o projeto
git clone https://github.com/SEU_USUARIO/doomsday-clock-ai.git

cd doomsday-clock-ai


### 2️⃣ Criar ambiente virtual


python -m venv venv


Ativar:

Windows:

.\venv\Scripts\activate


Mac/Linux:

source venv/bin/activate


### 3️⃣ Instalar dependências


pip install -r requirements.txt


### 4️⃣ Rodar aplicação


python -m streamlit run src/app.py


---

## 📊 Funcionalidades

### Overview
- Risco global (0–1)
- Conversão para minutos até meia-noite
- Comparação com Doomsday Clock oficial
- Delta entre modelo AI e valor oficial

### Feed
- Últimas notícias analisadas
- Risco por item
- Categoria automática

### Histórico
- Linha do tempo oficial desde 1947
- Evolução do risco médio do modelo

---

## 📚 Fonte Oficial

Bulletin of the Atomic Scientists:
https://thebulletin.org/doomsday-clock/

Wikipedia Timeline:
https://en.wikipedia.org/wiki/Doomsday_Clock

---

## ⚠️ Aviso

Este projeto NÃO é afiliado ao Bulletin.
É um experimento educacional baseado em dados públicos.

---

## 🔥 Próximas Evoluções

- Persistir histórico oficial no SQLite
- Normalizar risco AI para escala oficial (segundos)
- Modelo híbrido com peso por categoria
- Deploy em nuvem (Streamlit Cloud / Railway)
