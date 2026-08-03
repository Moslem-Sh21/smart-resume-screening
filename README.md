# Smart Resume Screening

A human-in-the-loop platform for matching technical resumes to job descriptions, ranking candidates, and producing evidence-grounded fit explanations.

## Project Status

This project is currently under development.

## Overview

Smart Resume Screening will allow reviewers to:

- Upload PDF and DOCX resumes
- Enter or upload a technical job description
- Extract structured skills, experience, education, and certifications
- Separate identity information from ranking features
- Match resumes to required and preferred job qualifications
- Rank candidates using lexical, semantic, and structured signals
- Review evidence supporting every score and explanation
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

## Planned Architecture

The project will include:

- Docling for local PDF and DOCX parsing
- AWS Textract as a cloud parsing option
- O*NET-based occupation and skill normalization
- BM25 lexical retrieval
- BGE-M3 semantic embeddings
- BGE reranking
- Evidence-grounded multimodal language-model explanations
- FastAPI backend
- PostgreSQL and OpenSearch
- Docker and Docker Compose
- GitHub Actions CI/CD
- AWS ECS Fargate deployment
- MLflow experiment tracking and tracing
- CloudWatch monitoring
- Terraform infrastructure as code

## Repository Structure

- `.github/workflows/`
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
- [ ] Create API and domain schemas
- [ ] Add Docker development environment
- [ ] Build PDF and DOCX ingestion
- [ ] Implement structured resume and job extraction
- [ ] Build ranking benchmarks and classical baselines
- [ ] Add dense retrieval and reranking
- [ ] Add evidence-grounded explanations
- [ ] Add fairness and robustness evaluations
- [ ] Deploy to AWS
- [ ] Add monitoring and automated evaluation
- [ ] Codify infrastructure using Terraform

## Evaluation

The system will be evaluated using:

### Extraction

- Precision
- Recall
- F1 score
- Evidence-span recall
- Employment-date accuracy

### Ranking

- nDCG@5 and nDCG@10
- Recall@5 and Recall@10
- Mean reciprocal rank
- Mean average precision
- Pairwise ranking accuracy

### Explanation quality

- Citation precision
- Requirement coverage
- Unsupported-claim rate
- Correct missing-information rate

### Fairness and robustness

- Counterfactual rank difference
- Top-k flip rate
- Resume-format sensitivity
- Keyword-stuffing resistance
- Prompt-injection resistance

## Responsible-Use Principles

- Human reviewers make all final decisions
- Identity information is excluded from ranking
- Missing information is not treated as evidence of missing ability
- Candidate scores remain decomposable and reviewable
- Generated claims must cite resume evidence
- The system will not infer personality or culture fit
- Real resumes will not be published without explicit consent

## Local Development

Local setup instructions will be added when the API and Docker environment are available.

## Benchmark

The project will introduce a controlled technical-role matching benchmark built from synthetic candidate profiles and manually reviewed relevance labels.

Publicly scraped resumes will not be included in the repository.

## Author

Matthew Shokrolahi

## License

A project license will be selected before the first public release.