# Books Analytics — Data Pipeline de Scraping (Airflow + Postgres + dbt + Streamlit)

Pipeline **fim-a-fim** com **logging** para estudo/portfólio:
- Scraping (**Airflow**) → `raw.books`
- Transformação (**dbt**) → `analytics.stg_books` / `analytics.dim_books`
- Visualização (**Streamlit**)

## 🧱 Stack
Docker, Apache Airflow 2.9, Postgres 15, dbt-postgres 1.7, Python 3.11, Streamlit.

## 🗂️ Estrutura
data-pipeline-scraping/
├─ docker-compose.yml
├─ .env.sample
├─ airflow/
│ ├─ dags/
│ │ └─ scrape_books_dag.py
│ └─ requirements.txt
├─ dbt/
│ ├─ profiles.yml
│ └─ models/
│ ├─ staging/
│ │ └─ stg_books.sql
│ └─ marts/
│ └─ dim_books.sql
├─ streamlit/
│ └─ app.py
└─ README.md


## ⚙️ Pré-requisitos
- Docker Desktop
- Portas livres: `8080`, `8501`, `5432`

## 🔐 Variáveis de ambiente
Crie um `.env` a partir de `.env.sample` (não comite o `.env` real):
```env
DATABASE_URL=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
DBT_HOST=postgres
DBT_USER=airflow
DBT_PASSWORD=airflow
DBT_DBNAME=airflow
DBT_SCHEMA=analytics
🚀 Como rodar
Suba os serviços


docker compose up -d
(Primeira carga) Rode a DAG no Airflow para popular raw.books
Abra o Airflow: http://localhost:8080
Ative e faça Trigger na DAG scrape_books.

Materialize os modelos com dbt

# roda o dbt dentro do container (sem abrir bash)
docker compose run --rm dbt run --select stg_books+ \
  --profiles-dir /usr/app --project-dir /usr/app

# (opcional) teste/validação
docker compose run --rm dbt debug --profiles-dir /usr/app --project-dir /usr/app
Abra o Streamlit
http://localhost:8501

🔎 Verificações rápidas
Listar objetos no schema analytics:

docker compose exec postgres psql -U airflow -d airflow -c "\dt analytics.*"
Contagem e última data de carga:

docker compose exec postgres psql -U airflow -d airflow \
  -c "select count(*), max(load_date) from analytics.dim_books;"
🌐 Serviços
Airflow UI → http://localhost:8080 (login conforme docker-compose; ex.: admin/admin)

Streamlit → http://localhost:8501

Postgres → localhost:5432 (usuário airflow, senha airflow, apenas em dev)

🧪 Logs
Airflow (DAG/task): UI do Airflow e docker compose logs -f airflow

Streamlit: arquivo streamlit/logs/streamlit.log

Postgres: docker compose logs -f postgres

🧰 Troubleshooting
Streamlit vazio → rode a DAG scrape_books e depois dbt run (gera analytics.dim_books).

Erro dbt “syntax error at or near '﻿'” → arquivo .sql salvo com UTF-8 com BOM. Salve como UTF-8 sem BOM.

Conexão psycopg2 falhou → confirme DATABASE_URL e se o container postgres está healthy (docker compose ps).

📜 Ética de scraping
Use Books to Scrape apenas para prática. Em sites reais, respeite termos/robots e limites.

🖼️ Screenshots (recomendado no portfólio)
Coloque em docs/screenshots/:

airflow.png — DAG scrape_books em execução

streamlit.png — dashboard carregado

## 📄 Licença
Este projeto está licenciado sob a licença MIT — veja o arquivo [LICENSE](./LICENSE) para detalhes.
