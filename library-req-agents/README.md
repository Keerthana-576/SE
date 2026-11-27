# Library Requirements Multi-Agent Prototype

An Agentic AI prototype for **requirement gathering, analysis and SDLC identification in library systems** (college/university Library Management System). It is the library-domain adaptation of the financial-sector problem statement: five collaborating agents, retrieval-grounded policy mapping, rule-based compliance checks, confidence scoring, a tamper-evident audit trail and human-in-the-loop approval gates.

It runs **fully offline** with no dependencies (Python 3.9+). If you set `ANTHROPIC_API_KEY` and pass `--llm`, extraction and the SDLC explanation also use Claude, with automatic fallback to the offline path.

## Quick start

**Web UI (recommended)**

```bash
python server.py                    # opens http://127.0.0.1:8000
```

1. **Input**: paste stakeholder text (or click *Load sample* / upload a .txt), set the project profile, press *Run the 5 agents*.
2. **Overview**: counts, what each agent did, masked data and blocked prompt-injection lines.
3. **Requirements**: filter and search; expand a requirement to see the original stakeholder wording, categories, acceptance criteria, cited policies, issues and escalations. Approve, reject or edit each one.
4. **Clarification**: resolve conflicts and duplicates (keep one or both), reword vague requirements, answer questions about areas nobody mentioned. Agents re-check after every change.
5. **Compliance**: policy coverage and missing controls, each with a one-click "Add as requirement".
6. **SDLC**: ranked models, decision factors, project-specific workflow with approval gates. Approve it, or override the agent's pick (logged as a human override).
7. **Outputs & audit**: download the SRS, traceability matrix, compliance matrix, risk register and audit log (or everything as a zip), see the approval log and verify the audit chain.

The server uses only the Python standard library, listens on 127.0.0.1 only, rejects foreign Host headers and non-JSON POSTs, and keeps one in-memory session (single user). Use `python server.py --port 9000 --no-browser` to change port or skip opening the browser.

**Command line**

```bash
python main.py                      # run on data/sample_transcript.txt (advisory mode)
python main.py --interactive        # clarification questions + human approval gates
python main.py --input my_notes.txt --name "My College LMS"
python -m unittest discover -s tests -v    # 13 tests (agents, pipeline, web API)

# optional: use Claude (works in both CLI and UI)
pip install anthropic
export ANTHROPIC_API_KEY=...        # never commit this
python main.py --llm
```

Outputs go to `output/` (CLI) or `output/web/` (UI): `SRS.md`, `sdlc_plan.md`, `requirements.json`, `traceability_matrix.csv`, `compliance_matrix.csv`, `risk_register.csv`, `audit_log.jsonl`.

## Input format

Plain text, one stakeholder statement per line, tagged with the role:

```
[Librarian] The system must block issue if the member's fines exceed the limit.
[Student] I want to renew books online.
```

Lines starting with `#` are ignored. Untagged lines get the source "Unknown" and are flagged.

## The five agents

| # | Agent | File | What it does |
|---|-------|------|--------------|
| 1 | Requirement Extraction | `agents/extraction.py` | Finds requirement sentences, rewrites them as "The system shall...", links each to its stakeholder and original wording, sets priority |
| 2 | Quality and Clarification | `agents/quality.py` | Detects ambiguity, missing values, missing controls (e.g. override without logging), duplicates, numeric/polarity conflicts, and missing requirement areas; scores confidence; writes the clarification questions |
| 3 | Classification | `agents/classification.py` | Multi-label classification into 14 categories, assigns module and ID (`FR-CIR-001`, `NFR-GEN-001`, `BR-CIR-002`), drafts acceptance criteria |
| 4 | Policy and Compliance | `agents/compliance.py` | Retrieval-grounded mapping to the knowledge base with citations and scores, rule-based gap detection, risk level, escalation to humans |
| 5 | SDLC Selection | `agents/sdlc.py` | Derives 8 decision factors, scores 7 SDLC models, applies selection rules, returns a ranked list and a project-specific workflow |

The UI (`web/index.html`) talks to `server.py`, which calls the orchestrator's step-by-step methods (`analyze`, `decide`, `revise`, `resolve_pair`, `add_requirement`, `set_sdlc_model`, ...).

The **orchestrator** (`orchestrator.py`) is not counted as an agent: it runs the pipeline, owns shared state, the clarification loop, the approval gates and the audit log.

```
raw text -> mask PII + drop injection lines -> [1 Extraction] -> [3 Classification]
        -> [2 Quality/Clarification] <-> (interactive clarification loop)
        -> [4 Policy/Compliance] -> [5 SDLC Selection]
        -> human approval gates -> SRS, RTM, compliance matrix, risk register, SDLC plan
                      every step -> hash-chained audit_log.jsonl
```

## How the professor's requirements map to the code

| Requirement in the problem statement | Where it is implemented |
|---|---|
| Sensitive data masked before the LLM | `privacy.py` (email, phone, Aadhaar, member IDs), applied before any agent |
| Prompt-injection protection | `privacy.screen_injection` drops suspicious lines and logs them; the LLM prompt also treats input as data |
| Retrieval-grounded generation, citations, confidence | `kb.py` + `agents/compliance.py` |
| Unsupported / low-confidence output escalated | `compliance._confidence_and_escalation` |
| Rule-based compliance validation | `compliance._gap_rules` using `required_controls` in the knowledge base |
| Ambiguity / conflict / duplicate detection | `agents/quality.py` |
| Traceability | `traceability_matrix.csv`: requirement -> stakeholder statement -> policy -> acceptance criteria -> test case IDs |
| SDLC ranking with justification | `agents/sdlc.py` (weighted scoring + deterministic rules + explanation) |
| Project-specific workflow with gates | `sdlc.BASE_PHASES` + project-specific checkpoints |
| Human-in-the-loop | Web UI (or CLI `--interactive`): accept/reject/edit each requirement, resolve conflicts, baseline approval, SDLC approval or override |
| Audit trail | `audit.py`: JSONL, each record hashes the previous one; `AuditLog.verify` detects tampering |
| Advisory mode first | Default run records no approvals; everything is "Pending Approval" |

## Customising for your college

1. **Knowledge base** (`data/knowledge_base.json`): replace the illustrative entries with your institution's real lending policy, IT policy, licence terms, and verified legal texts. Each entry carries source, jurisdiction, effective date and version.
2. **Project profile** (`data/project_profile.json`): set `requirement_stability`, `stakeholder_availability`, `extensive_approvals`, etc. (0 to 1). `null` means "estimate from the analysed requirements".
3. **SDLC models**: edit `IDEALS` and `WEIGHTS` in `agents/sdlc.py`, or the phase templates in `BASE_PHASES`.
4. **Vocabulary**: category and module keywords live at the top of `agents/classification.py`; vague words in `agents/quality.py`.

## Evaluating it (for your report)

Run the pipeline on requirements you collect from a librarian and students, then compare with a manually written SRS:

* extraction precision / recall / F1 against a hand-labelled list
* ambiguity and conflict detection accuracy (plant known defects, as `sample_transcript.txt` does)
* policy-mapping correctness (check the citations)
* SDLC recommendation vs. what an experienced architect chooses
* time taken vs. manual analysis, human correction rate, stakeholder satisfaction

## Honest limitations

* The offline agents are **rule-based heuristics**, not an LLM. They are transparent and testable but will miss subtle wording; the `--llm` path improves extraction only. A fuller version would let an LLM do classification, clarification and conflict reasoning, with these rules as validators.
* The retriever is TF-IDF plus trigger phrases. Swap `KnowledgeBase.search` for a vector database to scale.
* The knowledge base is **illustrative**. Legal citations must be verified by a compliance/legal officer; the system never makes legal determinations.
* SDLC scores are heuristic suitability scores, not probabilities. The factor values and ideal profiles are assumptions you should justify or calibrate (for example against architects' decisions).
* The UI is a local, single-user prototype (one in-memory session, no login). For multi-user use you would add authentication, per-user sessions and a database.
