# Emotion-Aware Analytics System

Train an emotion-recognition model and use it to analyze collections of real opinions about products, everyday experiences, public issues, and events. The system will produce reports that connect emotions with recurring themes and supporting comments.

The product will have two interfaces:

- **Web application:** import a collection of opinions, explore the findings, and export a report.
- **Browser extension:** analyze accessible reviews or comments on a supported webpage and display a compact result beside the page.

## Project status

**Planning the pivot as of November 3, 2026.** The code currently implements an earlier Reddit/Claude backend prototype. The trained model, new analysis workflow, web interface, and extension described here are planned work.

Read [PROJECT_PLAN.md](PROJECT_PLAN.md) for the scope, data strategy, training and evaluation approach, target architecture, extension design, and code reuse decisions. [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) defines the development phases, checkpoint tests, commit boundaries, and PR merge workflow. [ARCHITECTURE.md](ARCHITECTURE.md) preserves the superseded Reddit design for reference.

## Intended workflow

```text
Emotion-labeled examples -> training and evaluation -> versioned emotion model
                                                               |
Imported opinions or webpage comments -> model + theme analysis -> report
```

The analysis should answer:

- Which emotions are expressed in the collected opinions?
- Which themes are associated with those emotions?
- How do patterns differ across products, topics, or supported time periods?
- Which actual comments support each finding?

Reports will include the number of opinions analyzed, exclusions, collection coverage, model version, and supporting excerpts. Findings describe the collected opinions; they do not establish the views of the whole population.

## First version

The recommended initial scope is **English product reviews from one category**, using a small set of products with enough reviews for useful comparisons. The exact category and sample will be selected after inspecting the data. Support for public events and issues will follow through the same analysis interface.

Training data and analysis data serve different purposes:

| Purpose | Candidate source |
| --- | --- |
| Teach the model to recognize emotions | [GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions), a published dataset with human emotion annotations |
| Analyze everyday product experiences | [Amazon Reviews'23](https://amazon-reviews-2023.github.io/), with downloadable review text, product identifiers, and timestamps |
| Extend to public issues | [Regulations.gov](https://open.gsa.gov/api/regulationsgov/), with comments grouped around specific proposals |

The model will be fine-tuned from a pretrained text encoder and evaluated against a simple baseline and a manually labeled sample from the application domain. Multi-label predictions will allow one opinion to express several emotions. Report generation will use computed statistics and source excerpts.

## Browser extension

On a supported page, the user will click **Analyze opinions** to open a side panel containing emotion distributions, recurring themes, and evidence. It will state its coverage, for example: "Analyzed 40 reviews loaded on this page."

The first extension will support one website. Site-specific extraction, pagination, and dynamically loaded comments will be handled explicitly. Automatic analysis on supported sites is a later, optional feature. The extension and web application will share the same analysis API and trained model.

## Development phases and checkpoints

Each checkpoint has a stable ID, a concrete deliverable, required tests, and a visible result to review. Commit each completed checkpoint on its feature branch. Use **squash and merge** to merge PRs into `main` after the required checks pass, producing one final commit per PR. Use a checkpoint PR by default, or a small phase PR for closely related checkpoints, and include every checkpoint ID in the final squash commit message.

| Phase | Checkpoints | Result to review |
| --- | --- | --- |
| 0. Project foundation | P0.C1 plan; P0.C2 isolate the new application; P0.C3 automated checks | Documented scope and a runnable, independently tested starting point |
| 1. Data and contracts | P1.C1 data audit and contracts; P1.C2 importer; P1.C3 labeled domain evaluation set | A traceable real opinion collection and a usable evaluation protocol |
| 2. Model training | P2.C1 baseline; P2.C2 fine-tuning pipeline; P2.C3 model evaluation and selection | Reproducible experiments and an evaluated model artifact |
| 3. Core analytics | P3.C1 inference and storage; P3.C2 themes and statistics; P3.C3 reports | One reproducible report with source evidence |
| 4. API and web application | P4.C1 analysis API; P4.C2 web interface; P4.C3 integrated application | Import, analyze, inspect evidence, and export through the application |
| 5. Browser extension | P5.C1 extension shell; P5.C2 extraction; P5.C3 analytics panel; P5.C4 complete extension validation | Analysis on one supported website with accurate coverage |
| 6. Broader topics | P6.C1 new-domain evaluation; P6.C2 event/issue analysis; P6.C3 release validation | An evaluated second domain and a reproducible release candidate |

See [the detailed checkpoint roadmap](DEVELOPMENT_ROADMAP.md#development-checkpoints) for each deliverable and testing gate, and [the commit and PR workflow](DEVELOPMENT_ROADMAP.md#commit-and-pr-workflow) for merge rules. A phase is complete only when its checkpoints are merged and its combined demonstration passes.

Current progress: **P0.C1 planning documentation was merged in [PR #1](https://github.com/dheerajkiran/emotion-aware-analytics-system/pull/1). Implementation checkpoints have not started.**

## Existing code: reuse selectively

Keep this repository and its history. Build new training, analysis, and reporting modules around source-neutral contracts, while reusing suitable infrastructure.

| Existing area | Direction |
| --- | --- |
| FastAPI application and health endpoint | Reuse; adapt routes and request configuration |
| Batch embedding utilities | Reuse and evaluate on the chosen domain |
| HDBSCAN clustering | Evaluate and adapt for themes; current storyline grouping is a different task |
| Postgres access and migration patterns | Reuse patterns; introduce new tables and migrations |
| Reddit ingestion, `/landscape`, and engagement ranking | Preserve as legacy code during migration |
| Claude emotion classification and fixed Plutchik output | Replace in the primary workflow with trained-model inference and a versioned label schema |

The detailed file-by-file assessment is in [PROJECT_PLAN.md](PROJECT_PLAN.md#existing-code-and-migration).

## Repository today

- `api/src/`: legacy Reddit ingestion, Claude classification, embeddings, ranking, database access, and FastAPI routes.
- `db/migrations/`: existing Postgres/pgvector schema and index migrations.
- `scripts/`: legacy demo-data seeding.
- `tests/`: existing classification, embedding, database, ranking, and Reddit normalization checks.
- `PROJECT_PLAN.md`: current product and implementation plan.
- `DEVELOPMENT_ROADMAP.md`: phased checkpoints, validation requirements, progress, and commit/PR workflow.
- `ARCHITECTURE.md`: historical design of the Reddit prototype.

There are no runnable setup instructions for the pivot yet. The existing `.env.example` and dependency files belong to the legacy prototype. Some existing tests and scripts call Claude or write to the configured database; they are not a self-contained demonstration of the new product.

## License

Repository code is MIT-licensed; see [LICENSE](LICENSE). External datasets and pretrained models have their own terms and attribution requirements.
