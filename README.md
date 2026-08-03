\# Visual Product RAG



An end-to-end multimodal product search and grounded comparison platform.



\## Project Status



This project is currently under development.



\## Overview



Visual Product RAG will allow users to:



\- Upload a product image

\- Search for visually similar products

\- Search using natural-language queries

\- Combine image and text constraints

\- Compare retrieved products using a multimodal language model

\- Receive answers grounded in product metadata and retrieved images



\## Planned Architecture



The project will include:



\- CLIP or SigLIP-based multimodal embeddings

\- FAISS for local vector search

\- Amazon OpenSearch for cloud vector search

\- FastAPI backend

\- Multimodal language model integration

\- Docker and Docker Compose

\- GitHub Actions CI/CD

\- AWS deployment using ECS Fargate

\- MLflow experiment tracking

\- CloudWatch monitoring

\- Terraform infrastructure as code



\## Repository Structure



\- `.github/workflows/`

\- `infra/`

\- `monitoring/`

\- `notebooks/`

\- `src/`

\- `tests/`

\- `.env.example`

\- `.gitignore`

\- `pyproject.toml`

\- `README.md`



\## Development Roadmap



\- \[x] Initialize Git repository

\- \[x] Create initial repository structure

\- \[x] Add environment configuration template

\- \[x] Configure Python project

\- \[ ] Create API skeleton

\- \[ ] Add Docker development environment

\- \[ ] Build dataset preprocessing pipeline

\- \[ ] Implement multimodal retrieval

\- \[ ] Add grounded product comparison

\- \[ ] Deploy to AWS

\- \[ ] Add monitoring and automated evaluation



\## Local Development



Local setup instructions will be added when the API and development environment are available.



\## Dataset



The project will initially use a curated subset of the Amazon Berkeley Objects dataset.



Dataset download and preprocessing instructions will be added later.



\## Evaluation



The system will be evaluated using:



\- Recall@k

\- Mean reciprocal rank

\- NDCG

\- Retrieval latency

\- Metadata accuracy

\- Citation accuracy

\- Unsupported-claim rate



\## Author



Matthew Shokrolahi



\## License



A project license will be selected before the first public release.

