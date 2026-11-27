# Project-specific SDLC workflow - Agile-V-Model hybrid

**Recommended:** Agile-V-Model hybrid

Agile-V-Model hybrid scores highest (84) against V-Model (67) and Spiral (55). High factors: volatility, regulatory, stakeholder_availability, verification. Low factors: continuous_delivery. Rules applied: Strict verification needed -> V-Model family. This is a heuristic recommendation; the project manager, architect, security team and compliance officer must approve it.

**Ranking (heuristic suitability, not probability):**
1. Agile-V-Model hybrid: 84%
2. V-Model: 67%
3. Spiral: 55%
4. Waterfall: 51%
5. Agile-DevSecOps hybrid: 49%
6. DevSecOps: 47%
7. Agile: 39%

**Decision factors (0-1):** volatility=0.6, regulatory=1.0, security=0.5, uncertainty=0.48, integration=0.33, continuous_delivery=0.27, stakeholder_availability=0.7, verification=1.0

**Approval:** Pending - requires project manager, architect, security team and compliance officer

## Workflow

### Phase 1: Baseline Requirements and Acceptance Tests

- **Activities:** Baseline high-risk and regulated requirements; Write acceptance tests
- **Roles:** Business Analyst, Compliance Officer, QA
- **Deliverables:** Baselined SRS, Acceptance test plan
- **Security controls:** Data classification
- **Compliance checkpoints:** Policy mapping approved, Interface conformance tests (SIP2 / NCIP / OAI-PMH / SSO), WCAG 2.1 AA audit with screen reader, Licence-limit tests (simultaneous users, download caps), Audit-log completeness and report-accuracy checks, Data-retention and deletion schedule verified, Accreditation report sample reviewed by librarian
- **Entry criteria:** Approved scope and stakeholder list
- **Exit criteria:** Requirements baseline approval recorded in the audit log
- **Human-approval gate:** Requirements baseline approval

### Phase 2: Iteration Planning

- **Activities:** Refine backlog; Select iteration scope
- **Roles:** Product Owner, Developers
- **Deliverables:** Iteration backlog
- **Security controls:** None specific
- **Compliance checkpoints:** Story-level policy tags
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Iteration scope accepted recorded in the audit log
- **Human-approval gate:** Iteration scope accepted

### Phase 3: Iterative Design and Build

- **Activities:** Design per epic; Build and unit test
- **Roles:** Architect, Developers
- **Deliverables:** Increment
- **Security controls:** Threat modelling, Static analysis
- **Compliance checkpoints:** Privacy impact assessment for personal-data epics, Privacy impact assessment (DPDP Act), Role and permission matrix reviewed
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Design review recorded in the audit log
- **Human-approval gate:** Design review

### Phase 4: Integration and System Verification (V-leg)

- **Activities:** Integration test; System test; Interface conformance
- **Roles:** QA, Integrator
- **Deliverables:** Verification reports
- **Security controls:** Security testing
- **Compliance checkpoints:** Evidence mapped to controls, Interface conformance tests (SIP2 / NCIP / OAI-PMH / SSO), WCAG 2.1 AA audit with screen reader, Licence-limit tests (simultaneous users, download caps), Audit-log completeness and report-accuracy checks
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Verification gate recorded in the audit log
- **Human-approval gate:** Verification gate

### Phase 5: Acceptance and Release

- **Activities:** UAT; Compliance review; Release
- **Roles:** Librarians, Compliance Officer
- **Deliverables:** UAT sign-off
- **Security controls:** Hardening
- **Compliance checkpoints:** Compliance sign-off, Data-retention and deletion schedule verified, Accreditation report sample reviewed by librarian
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Production-readiness approval recorded in the audit log
- **Human-approval gate:** Production-readiness approval
