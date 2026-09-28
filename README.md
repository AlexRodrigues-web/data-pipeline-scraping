# Data Pipeline — Books to Scrape

Pipeline end-to-end para recolha, transformação e visualização de dados, usando **Airflow, Postgres, dbt e Streamlit**.

## Fluxo
Books to Scrape → Airflow → Postgres → dbt → Streamlit

## Componentes
- DAGs de ingestão/orquestração
- PostgreSQL para camada raw
- dbt para staging e marts
- Streamlit para exploração dos resultados
- Docker Compose para ambiente reproduzível

## Extensão SpaceX
O projeto inclui também exemplos de ingestão da API pública da SpaceX e modelos dbt para análises por ano.

## Execução
```bash
cp .env.example .env
docker compose up -d
```
Depois execute os DAGs/modelos conforme a configuração local.

## Segurança
O ficheiro `.env` real não é versionado. Use apenas os exemplos fornecidos no repositório.

## Autor
Alex Oliveira
