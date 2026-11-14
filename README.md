# Smart Resume Screening

A human-in-the-loop platform for matching technical resumes to job descriptions, ranking candidates, retrieving requirement-level evidence, and producing evidence-grounded fit explanations with Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

## Project Status

This project is currently under development.

Current focus: structured job-description extraction before moving into ranking, retrieval, RAG, and LLM-based explanation generation.

## Overview

Smart Resume Screening will allow reviewers to:

- Upload PDF and DOCX resumes
- Enter or upload a technical job description
- Extract structured candidate and job requirements
- Separate identity information from ranking features
- Match resumes to required and preferred job qualifications
- Rank candidates using structured, lexical, and semantic signals
- Retrieve requirement-specific resume evidence with hybrid search
- Use Retrieval-Augmented Generation (RAG) to build grounded context for each requirement
- Use an LLM to generate evidence-grounded strengths, gaps, and uncertainty explanations
- Review citations supporting every generated explanation
- Compare candidate strengths, gaps, and uncertainties
- Override system results and provide reviewer feedback

The platform is intended to support human reviewers. It will not automatically reject candidates or make final hiring decisions.

## Initial Role Scope

The first version will focus on:

- Machine Learning Engineer
- Data Scientist
- Data Engineer
- Software Engineer
- Cloud and DevOps Engineer
- Cybersecurity Analyst

## End-to-End Architecture

```text
Resume / Job Description
        ↓
Document and text ingestion
        ↓
Structured extraction
        ↓
CandidateProfile + JobProfile
        ↓
Skill / occupation normalization
        ↓
Structured matching + BM25 lexical retrieval
        ↓
BGE-M3 semantic retrieval
        ↓
Hybrid retrieval
        ↓
BGE reranking
        ↓
Requirement-level RAG context
        ↓
LLM / MLLM
        ↓
Evidence-grounded fit explanation
        ↓
Human reviewer
```

The retrieval and RAG layers are designed to connect each job requirement to the most relevant candidate evidence before the LLM generates an explanation.

## Planned Architecture

The project will include:

### Ingestion and structured data

- Docling for local PDF and DOCX parsing
- AWS Textract as a cloud parsing option
- Deterministic structured extraction as a testable baseline
- LLM-assisted extraction for ambiguous or difficult cases where it provides measurable value
- O*NET-based occupation and skill normalization
- Pydantic domain schemas for candidates, jobs, requirements, and evidence

### Retrieval, ranking, RAG, and LLMs

- Structured requirement-to-candidate matching
- BM25 lexical retrieval
- BGE-M3 semantic embeddings
- Hybrid lexical + semantic retrieval
- BGE reranking
- Requirement-level Retrieval-Augmented Generation (RAG)
- LLM-based evidence-grounded candidate-fit explanations
- Multimodal language-model support where visual document evidence is useful
- Prompt and context controls to reduce unsupported claims and data leakage

### Backend and persistence

- FastAPI backend
- PostgreSQL for application data
- OpenSearch for lexical and vector retrieval
- SQLAlchemy and Alembic for persistence and database migrations

### MLOps and infrastructure

- Docker and Docker Compose
- GitHub Actions CI/CD
- AWS ECS Fargate deployment
- MLflow experiment tracking and tracing
- CloudWatch monitoring
- Terraform infrastructure as code

## Repository Structure

- `.github/workflows/`
- `apps/`
- `infra/`
- `monitoring/`
- `notebooks/`
- `src/resume_screening/`
- `tests/`
- `.env.example`
- `.gitignore`
- `pyproject.toml`
- `README.md`

## Development Roadmap

- [x] Initialize Git repository
- [x] Create initial repository structure
- [x] Add environment configuration template
- [x] Configure Python project
- [x] Rescope the repository for resume screening
- [x] Create API and domain schemas
- [x] Add Docker development environment
- [x] Add PostgreSQL persistence and database migrations
- [x] Build PDF and DOCX ingestion with Docling
- [x] Implement structured resume extraction
- [ ] Implement structured job-description extraction
- [ ] Build controlled ranking benchmarks and classical baselines
- [ ] Add BM25 lexical retrieval
- [ ] Add BGE-M3 semantic retrieval
- [ ] Add hybrid retrieval and BGE reranking
- [ ] Build requirement-level RAG pipeline
- [ ] Integrate LLMs for evidence-grounded fit explanations
- [ ] Evaluate RAG retrieval quality and LLM grounding
- [ ] Add fairness and robustness evaluations
- [ ] Deploy to AWS
- [ ] Add monitoring and automated evaluation
- [ ] Codify infrastructure using Terraform

## Evaluation

The system will be evaluated at each layer rather than only on the final generated answer.

### Extraction

- Precision
- Recall
- F1 score
- Evidence-span recall
- Employment-date accuracy
- Requirement extraction accuracy

### Ranking

- nDCG@5 and nDCG@10
- Recall@5 and Recall@10
- Mean reciprocal rank
- Mean average precision
- Pairwise ranking accuracy

### Retrieval and RAG

- Precision@k
- Recall@k
- Mean reciprocal rank
- Requirement-to-evidence retrieval accuracy
- Evidence-span recall
- Reranker improvement over first-stage retrieval

### LLM explanation quality

- Citation precision
- Citation recall
- Requirement coverage
- Unsupported-claim rate
- Correct missing-information rate
- Faithfulness to retrieved evidence
- Explanation consistency under equivalent evidence

### Fairness and robustness

- Counterfactual rank difference
- Top-k flip rate
- Resume-format sensitivity
- Keyword-stuffing resistance
- Prompt-injection resistance
- Identity-removal consistency

## Responsible-Use Principles

- Human reviewers make all final decisions
- Identity information is excluded from ranking
- Missing information is not treated as evidence of missing ability
- Candidate scores remain decomposable and reviewable
- RAG retrieval should expose the evidence used for each requirement
- LLM-generated claims must be grounded in retrieved candidate evidence
- Unsupported claims should be measurable and treated as evaluation failures
- The LLM must not infer personality, culture fit, or protected characteristics
- Generated explanations must distinguish evidence, gaps, and uncertainty
- Real resumes will not be published without explicit consent

## Local Development

Install dependencies:

```bash
uv sync --all-extras
```

Start the local PostgreSQL service:

```bash
docker compose up -d db
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

Start the FastAPI application:

```bash
uv run uvicorn apps.api.main:app --reload
```

Run the quality checks:

```bash
uv run pytest
uv run ruff check .
uv run pyright
```

Docling PDF models should be downloaded during environment setup and reused from the local model cache rather than downloaded during normal API requests.

## Benchmark

The project will introduce a controlled technical-role matching benchmark built from synthetic candidate profiles, synthetic and manually reviewed job requirements, and manually reviewed relevance labels.

The benchmark will support separate evaluation of:

- Structured extraction
- Candidate-job requirement matching
- Lexical and semantic retrieval
- Reranking
- RAG evidence selection
- LLM explanation grounding

Publicly scraped resumes will not be included in the repository.

## Author

Matthew Shokrolahi

## License

A project license will be selected before the first public release.
