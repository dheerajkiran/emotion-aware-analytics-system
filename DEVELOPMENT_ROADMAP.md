# Development Roadmap and Checkpoints

**Updated:** November 3, 2026

**Status:** P0.C1 planning documentation is published directly to `main` as one documentation commit. Implementation checkpoints have not started.

Read [README.md](README.md) for the overview and [PROJECT_PLAN.md](PROJECT_PLAN.md) for the product and technical design. This roadmap is the execution and progress record. The phases below are sequential by default; individual preparatory work may overlap when dependencies are explicit.

## Commit and PR workflow

The initial planning baseline (P0.C1) is published directly to `main` as one documentation commit. Subsequent work follows the branch, PR, and squash-merge workflow below. This initial direct commit has no PR number.

### Publication hygiene

This is a required check before every commit and push, including documentation updates.

- Keep source comments, documentation, commit messages, branch names, and PR titles/descriptions focused on the project. Exclude tool signatures, generated-by notices, and unsolicited authorship/co-author trailers.
- Keep chat transcripts, session identifiers, development-session prompts, and personal tool configuration out of published project files and artifacts.
- Inspect the staged diff, intended commit message, configured author/committer metadata, and PR text before publication. Check export files and generated artifacts for accidental session details as well.
- Preserve required third-party notices, dataset/model provenance, and accurate implementation and validation records. Technical references to a model or service used by the application remain part of its documentation.
- Correct any publication-hygiene issue before committing or pushing. Recheck the final commit and PR text after creation.

### Checkpoint lifecycle

1. **Choose the checkpoint.** Confirm its scope, dependencies, required checks, and observable result. Decide whether it has its own PR or belongs to a small group before implementing it.
2. **Work on a branch.** Start from current `main`, for example `phase-1/p1-c2-review-importer`. For a grouped PR, keep consecutive checkpoint commits on one branch. After a prerequisite is squash-merged, start dependent work from updated `main`, or rebase only the remaining work onto it; avoid including already-merged changes again.
3. **Implement and test.** Run the checkpoint's checks and relevant regression checks. Demonstrate the result using a small, traceable input. Fix failed required checks before declaring the checkpoint validated.
4. **Record the evidence.** Summarize what works, actual test commands and outcomes, input/model versions, demonstration artifacts, and known limitations. Update this roadmap's progress table.
5. **Commit the checkpoint.** On the feature branch, use one coherent checkpoint commit or a small set of commits with a clear final checkpoint boundary, for example `feat(data): add repeatable review importer (P1.C2)`. Each checkpoint must remain identifiable even when grouped in one PR.
6. **Open the PR after local validation.** List the included checkpoint IDs, what changed, test evidence, demonstration, and any migration or artifact requirements. PR CI then verifies the pushed commit.
7. **Review and squash-merge.** Resolve review findings and use squash and merge only after all required checks pass for the latest PR commit. Update with `main` and rerun affected checks if integration changes the code. Inspect the final squash message, include all checkpoint IDs, and append the actual PR number to the title as `(#N)`. Do not count a failed or skipped required check as a pass.
8. **Record the merge.** Add the PR reference and resulting squash commit SHA to each included checkpoint's progress entry. At the final checkpoint of a phase, demonstrate the combined capability before calling the phase complete.

Completed checkpoints get commits even if their PR will include a later related checkpoint. A committed checkpoint is not automatically merged or phase-complete. Draft work may be saved in intermediate commits, but must not be labeled a validated checkpoint until its gate passes.

### Merge method: squash and merge

Use **squash and merge** for checkpoint and grouped phase PRs. This creates one final commit per PR on `main`; the feature branch's individual checkpoint and intermediate commits do not become separate commits on `main`.

For a single-checkpoint PR, include its ID in the final commit message. For a grouped PR, list every included checkpoint ID in the final commit message and PR description, and link each progress entry to the same resulting squash commit. Retain the individual checkpoints' validation evidence in the PR and checkpoint records.

The final squash title must include the actual PR number, for example `docs: establish project plan (P0.C1) (#N)`, where `N` is the number assigned to that PR. Preserve this suffix when editing GitHub's suggested title or supplying a custom title through the CLI.

Inspect and edit the proposed squash title/body before merging so it contains the project change, checkpoint IDs, and relevant context. Apply the publication-hygiene check to that final message as well as the original branch commits.

After merging, update local `main` and delete the completed remote and local feature branches while preserving uncommitted work. A squash-merged branch may fail Git's ordinary ancestry check for local deletion. Verify that its PR is merged and the intended changes are present on `main` before removing that local branch.

### Choosing the merge boundary

- **Default: one PR per checkpoint.** Use this for independently testable capabilities and changes to contracts, migrations, inference, or reporting behavior.
- **Grouped or phase PR:** use only for closely related checkpoints that still form a small, reviewable diff. Each checkpoint gets its own feature-branch commit, evidence, and passing checks; the PR becomes one squash commit on `main`. Grouped PRs must include the checks for every included checkpoint plus an integration demonstration.
- **Split oversized work:** divide a checkpoint further if it grows beyond a coherent review. Extend its ID, such as `P3.C2a`, and update the roadmap before claiming completion.
- **Keep `main` usable:** partially introduced capabilities must be isolated or disabled until their dependencies and tests are ready. Do not expose an unfinished feature simply because its infrastructure merged.
- **PR gate after the initial baseline:** after the direct P0.C1 planning commit, all subsequent changes to `main`, including documentation updates, follow the testing and PR gate. Whether a PR is a checkpoint or phase PR does not weaken the gate.

These are project workflow rules, not a claim that GitHub branch protection or CI is already configured. P0.C3 implements automated checks; required-check enforcement should be configured when repository permissions allow it. Until then, verify the equivalent checks explicitly before merging.

### Test and artifact rules

- Select tests appropriate to the change. Documentation needs link/format checks; it does not need a model-training run. Recheck affected behavior after code changes.
- Keep routine checks reproducible without Reddit/Claude credentials, paid calls, bulk downloads, or production database writes. Use small fixtures, isolated test databases, and test doubles where appropriate.
- List manual, live-site, full-training, and domain-evaluation gates separately from fast CI. A passing smoke test does not establish model quality or complete site support.
- Run required integration tests against disposable resources. Record versions and setup so their results can be reproduced.
- Commit code, bounded fixtures, manifests, configurations, and metric summaries. Store large datasets, model weights, and full experiment outputs outside ordinary Git commits; record their artifact locations, versions, and hashes.
- Training infrastructure may merge before its model is good enough to select for use. P2.C3 is the separate model-selection gate. Define its criteria after the baseline and before inspecting final held-out results.

### Checkpoint evidence and PR contents

For implementation checkpoints, keep a concise record using the planned convention `docs/checkpoints/P1.C2.md`, or an equivalent linked artifact. Include:

- Checkpoint ID, scope, dependencies, and completion criteria.
- What changed and the user-visible or developer-visible demonstration.
- Exact validation commands, outcomes, and relevant environment details.
- Data/model/artifact references and any migrations.
- Known limitations, required checks still outstanding, and current status.
- Commit and PR references once available; the PR itself can record its own commit link.

Do not invent command results or mark planned tests as passed. These documentation records and test commands will be added as their checkpoints are implemented.

## Development checkpoints

Every row below is a separate checkpoint and feature-branch commit boundary. The validation column is required evidence for that checkpoint. Phase merge recommendations allow small groups; each merged PR becomes one squash commit on `main`. Independently working changes can merge before phase-end.

### Phase 0: Project foundation

**Goal:** Establish the plan and a runnable, testable foundation for the new workflow.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P0.C1 | Publish the pivot plan, code-reuse assessment, phased checkpoints, and PR rules. Review the documentation as the planning baseline. | Check local links, heading references, Markdown structure, whitespace, and consistency between documents. Clearly distinguish current code from planned features. |
| P0.C2 | Establish the new application/module boundary and reproducible development/test setup. Keep legacy Reddit/Claude code isolated from the new path. Demonstrate a health request without external-service credentials. | Import/start the new path with Reddit/Claude credentials absent; verify health behavior and relevant reusable-module regressions. Document the setup commands that actually work. |
| P0.C3 | Add automated PR checks and separate fast, integration, and expensive/manual test entry points. Demonstrate that a deliberate failure fails the check. | Run checks locally and in CI; show that routine checks do not need production secrets or live paid services. Record required check names and repository enforcement status. |

**Merge recommendation:** P0.C1 is the initial direct documentation commit. P0.C2 and P0.C3 may share one small foundation PR, with separate checkpoint commits.

**Phase completion:** A clean checkout has documented setup and passing automated checks for the new foundation.

### Phase 1: Data and source-neutral contracts

**Dependencies:** Phase 0 foundation.

**Goal:** Obtain real usable opinions and define what the model and reports will consume.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P1.C1 | Audit the emotion training dataset and a bounded review sample; select the initial category/cohort. Define versioned opinion, collection, and label contracts plus dataset manifests. Show normalized sample records and the data-audit findings. | Validate label definitions, fields, source-scoped IDs, optional publication dates, source provenance, sample quality, and contract rejection of invalid inputs. Keep open data decisions explicit. |
| P1.C2 | Build repeatable CSV/JSON import, normalization, quality reporting, and duplicate handling. Demonstrate importing the same real sample twice with stable identities and consistent counts. | Check malformed/empty inputs, missing dates, language handling, duplicate policy, cross-source ID collisions, idempotency, and reconciliation of raw/usable/excluded counts. |
| P1.C3 | Prepare annotation guidance, a human-labeled domain evaluation sample, and a documented split/evaluation protocol. Show label coverage, ambiguity review, and the separation of development and held-out examples. | Audit split overlap and near-duplicate leakage; verify annotation structure, per-label support, and agreement review on a subset. Freeze held-out data before model selection. |

**Merge recommendation:** One PR per checkpoint. Contracts and importer changes should be easy to review independently.

**Phase completion:** A traceable real collection imports reproducibly, and a domain evaluation protocol and labeled sample are ready.

### Phase 2: Model training and selection

**Dependencies:** Phase 1 contracts and evaluation data.

**Goal:** Produce reproducible experiments and select a model using measured results.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P2.C1 | Train the multi-label TF-IDF/logistic-regression baseline, implement shared metrics, and save its configuration and artifact manifest. Show validation results and predictions on validation examples. | Check that preprocessing fits only on training data, label order is stable, metrics match a small known example, and the saved baseline reloads consistently. Set model-selection criteria using baseline/validation evidence before final held-out evaluation. |
| P2.C2 | Implement reproducible transformer fine-tuning with configuration, seed, checkpoint save/reload, and experiment tracking. Show a small training run and register a full experiment's artifact reference when available. | Run a bounded training/evaluation smoke test; check multi-label targets/loss/output shapes, finite loss, checkpoint reload, and split/configuration provenance. Record the full training run separately from routine CI. |
| P2.C3 | Select the candidate and thresholds using validation data, then perform final benchmark and domain held-out acceptance evaluation. Publish metrics, error analysis, latency measurements, and a versioned artifact manifest. | Meet the previously recorded selection criteria; report macro/micro F1 and per-label support/precision/recall/F1. Verify no tuning on test data and that the selected artifact reloads. If criteria fail, commit the experiment findings without claiming the gate passed. Further development must not tune against those final results; confirm any subsequent promotion on untouched evaluation data under a protocol declared in advance. |

**Merge recommendation:** One PR per checkpoint. Training-code improvements can merge with passing engineering tests; P2.C3 separately gates the selected model used by later demonstrations.

**Phase completion:** The chosen model and thresholds are reproducible, evaluated, and traceable to recorded data and configurations.

### Phase 3: Core inference, analytics, and reports

**Dependencies:** Phase 1 contracts and the selected Phase 2 model.

**Goal:** Generate the first complete report locally before adding browser or web interfaces.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P3.C1 | Implement batch inference, versioned predictions, caching, analysis snapshots, and new database migrations. Demonstrate inference over the real sample, then repeat it using the cache. | Check label/version handling, batching, invalid input, partial failures, cache invalidation after text/model changes, and source isolation. Test migrations against fresh and existing legacy schemas, idempotency, and preservation of legacy data using a disposable database. |
| P3.C2 | Implement theme discovery and emotion aggregation. Show theme memberships, evidence IDs, emotion counts, and comparisons for the sample. | Verify denominators, overlapping labels, exclusions, duplicate policy, empty/small collections, and time-window rules using known fixtures. Review representative real theme groups; disclose ungrouped/uncertain cases and the limits of opinion-level associations. |
| P3.C3 | Generate HTML/JSON reports with statistics, coverage, evidence, model versions, and export metadata. Demonstrate an end-to-end local report over a frozen real collection. | Trace every reported count to aggregation results and each excerpt to an input opinion; check HTML escaping, failure/empty states, and reproducibility from the same snapshot/configuration. Review the rendered HTML and record integration evidence. |

**Merge recommendation:** One PR per checkpoint. Keep migration/inference changes separate from theme/report presentation where practical.

**Phase completion:** One real opinion collection produces an evaluated, reproducible, evidence-backed report without the UI or extension.

### Phase 4: Analysis API and web application

**Dependencies:** Phase 3 reports and shared analytics.

**Goal:** Let a user import, analyze, inspect, and export through the application.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P4.C1 | Expose the analysis/report API with bounded inputs, status/results, partial-failure details, and version metadata. Add job execution only if measured workloads require it. Demonstrate the report through API requests. | Check validation, limits, POST/CORS behavior, error responses, input/result isolation, snapshot references, and report retrieval. Check pending/retry behavior if asynchronous execution is introduced. Run API-to-database/report integration checks. |
| P4.C2 | Build collection import, analysis progress, emotion/theme results, source evidence, and report export in the web interface. Demonstrate the complete journey against the existing API. | Check import and validation feedback, loading/pending, empty/error/retry states, evidence navigation, export, keyboard access, and usable layouts at supported screen sizes. Use API fixtures for UI checks plus one integration path. |
| P4.C3 | Validate the combined application using a real sample and the selected model. Document runnable setup and remaining limitations. Show import through to a source-backed exported report. | Run the end-to-end user journey and relevant regression suites; confirm UI/API/export counts agree and model/input versions match. Record a visual review, runtime measurements, and a clean-checkout reproduction. |

**Merge recommendation:** P4.C1 gets its own PR. P4.C2 and P4.C3 may share a small application PR; split them if the UI diff becomes large, keeping unvalidated functionality isolated.

**Phase completion:** The user can complete the real-data analysis journey through the web application with passing integration evidence.

### Phase 5: Browser extension for one website

**Dependencies:** Phase 4 shared API and a feasibility check of the chosen website.

**Goal:** Analyze opinions already accessible on one supported page and display results with honest coverage.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P5.C1 | Select a feasible first website and create the extension shell, click-triggered access, side-panel opening, and API configuration. Demonstrate local installation and supported/unsupported page states. | Inspect required access and actual comment markup. Check the manifest/build, click-triggered behavior, tab navigation, unsupported pages, and local loading. Document how captured text is sent for analysis. |
| P5.C2 | Build the site's review/comment extractor with source IDs, text, subject metadata, deduplication, and coverage. Show the extracted collection before inference. | Test representative saved page fixtures for boilerplate exclusion, pagination/dynamic updates where supported, collapsed text, empty pages, and repeated scans. Verify a permitted live page manually and record differences from fixtures. |
| P5.C3 | Connect extraction to the shared API and display emotions, themes, counts, and supporting comments in the side panel. Demonstrate parity with analysis of the same captured inputs outside the extension. | Check request/response handling, API errors, insufficient-data states, navigation/stale-result handling, safe rendering of page text, and matching counts/versions for the same snapshot. |
| P5.C4 | Validate and package the complete extension for its supported scope. Document installation, supported pages, extraction limits, and the real-data demonstration. | Run extraction and API regression checks plus a full supported-site journey. Confirm reported coverage matches extracted opinions, no double counting occurs, and changing pages cannot show another page's findings as current. Review permissions and the packaged build. |

**Merge recommendation:** P5.C1 and P5.C2 may share one small extraction PR. P5.C3 and P5.C4 normally get separate PRs. Do not label a website supported until P5.C4 passes.

**Phase completion:** One website has a validated extension journey and reproducible comparison with the shared analysis engine. Packaging does not imply store publication.

### Phase 6: Broader topics and release validation

**Dependencies:** A validated first domain and working shared analytics; extension-specific changes also depend on Phase 5.

**Goal:** Demonstrate the system on an event/public issue and consolidate a reproducible release candidate.

| ID | Deliverable and reviewable result | Validation before completion |
| --- | --- | --- |
| P6.C1 | Select a real event/issue collection, audit its context/coverage, and prepare separate domain labels. Evaluate transfer and document any adaptation needed. | Check source availability, topic identity, dates, campaign duplicates, annotation quality, and per-label domain results. Keep adaptation data separate from final evaluation. Do not infer stance or causation from emotion. |
| P6.C2 | Add the required adapter and event/issue report using the same contracts and engine. Demonstrate traceable findings and valid time comparisons only where supported. | Run adapter/import and existing-domain regressions; verify source IDs, counts, evidence, duplicate treatment, and date handling. Re-evaluate any adapted model and keep versioned results for both domains. |
| P6.C3 | Consolidate installation, model/data manifests, demonstrations, supported features, and release notes. Produce a reproducible release candidate for the validated scope. | Run the applicable combined regression suite, clean-setup reproduction, web journey, supported-extension journey, and domain-evaluation gates. Record actual remaining limitations; add deployment checks if a deployment target has been selected. |

**Merge recommendation:** Separate checkpoint PRs by default. P6.C1 and P6.C2 can share a small phase PR if the new-domain audit and adapter are closely coupled. Keep release validation as its own checkpoint.

**Phase completion:** The supported domains and extension scope have documented evidence, reproducible artifacts, and a passing combined release review. Public deployment and store publication are separate actions, not implied by a release-candidate checkpoint.

## Progress tracker

Statuses: **planned**, **in progress**, **implemented**, **validated**, and **merged**; **committed directly** applies only to the initial P0.C1 planning baseline. Use **blocked** only to describe a specific unmet dependency in this document. A phase completes when all required checkpoints are on `main` and its combined demonstration passes.

Track each checkpoint separately. Add links to its evidence, commit, and PR as work progresses.

| Checkpoint IDs | Current status | Evidence and commit/PR reference |
| --- | --- | --- |
| P0.C1 | Committed directly | Initial planning baseline published as one documentation commit on `main`, without a PR. Documentation links, headings, fences, whitespace, checkpoint IDs, and publication checks passed. See the P0.C1 commit in the [main history](https://github.com/dheerajkiran/emotion-aware-analytics-system/commits/main/). |
| P0.C2 | Planned | Not started |
| P0.C3 | Planned | Not started |
| P1.C1 | Planned | Not started |
| P1.C2 | Planned | Not started |
| P1.C3 | Planned | Not started |
| P2.C1 | Planned | Not started |
| P2.C2 | Planned | Not started |
| P2.C3 | Planned | Not started |
| P3.C1 | Planned | Not started |
| P3.C2 | Planned | Not started |
| P3.C3 | Planned | Not started |
| P4.C1 | Planned | Not started |
| P4.C2 | Planned | Not started |
| P4.C3 | Planned | Not started |
| P5.C1 | Planned | Not started |
| P5.C2 | Planned | Not started |
| P5.C3 | Planned | Not started |
| P5.C4 | Planned | Not started |
| P6.C1 | Planned | Not started |
| P6.C2 | Planned | Not started |
| P6.C3 | Planned | Not started |
