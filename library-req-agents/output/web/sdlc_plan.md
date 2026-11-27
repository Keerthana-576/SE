# Project-specific SDLC workflow - V-Model

**Recommended:** V-Model

V-Model scores highest (78) against Agile-V-Model hybrid (71) and Waterfall (51). High factors: regulatory, security, stakeholder_availability, verification. Low factors: uncertainty. Rules applied: Strict verification needed -> V-Model family. This is a heuristic recommendation; the project manager, architect, security team and compliance officer must approve it.

**Ranking (heuristic suitability, not probability):**
1. V-Model: 78%
2. Agile-V-Model hybrid: 71%
3. Waterfall: 51%
4. DevSecOps: 51%
5. Agile-DevSecOps hybrid: 45%
6. Spiral: 45%
7. Agile: 23%

**Decision factors (0-1):** volatility=0.5, regulatory=1.0, security=1.0, uncertainty=0.1, integration=0.42, continuous_delivery=0.33, stakeholder_availability=0.6, verification=1.0

**Approval:** Pending - requires project manager, architect, security team and compliance officer

## Workflow

### Phase 1: Requirements and Acceptance Test Planning

- **Activities:** Baseline requirements; Write acceptance tests per requirement
- **Roles:** Business Analyst, QA
- **Deliverables:** SRS, Acceptance test plan
- **Security controls:** Data classification
- **Compliance checkpoints:** Policy mapping reviewed, Interface conformance tests (SIP2 / NCIP / OAI-PMH / SSO), WCAG 2.1 AA audit with screen reader, Licence-limit tests (simultaneous users, download caps), Audit-log completeness and report-accuracy checks, Data-retention and deletion schedule verified, Accreditation report sample reviewed by librarian
- **Entry criteria:** Approved scope and stakeholder list
- **Exit criteria:** Requirements baseline approval recorded in the audit log
- **Human-approval gate:** Requirements baseline approval

### Phase 2: System Design and System Test Planning

- **Activities:** Architecture; System test design
- **Roles:** Architect, QA
- **Deliverables:** Design, System test plan
- **Security controls:** Threat modelling
- **Compliance checkpoints:** Privacy impact assessment, Privacy impact assessment (DPDP Act), Role and permission matrix reviewed, Interface conformance tests (SIP2 / NCIP / OAI-PMH / SSO), WCAG 2.1 AA audit with screen reader, Licence-limit tests (simultaneous users, download caps), Audit-log completeness and report-accuracy checks
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Design review recorded in the audit log
- **Human-approval gate:** Design review

### Phase 3: Module Design and Implementation

- **Activities:** Detailed design; Coding; Unit tests
- **Roles:** Developers
- **Deliverables:** Code, Unit test results
- **Security controls:** Static analysis
- **Compliance checkpoints:** Traceability to requirement IDs, Privacy impact assessment (DPDP Act), Role and permission matrix reviewed
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Code review gate recorded in the audit log
- **Human-approval gate:** Code review gate

### Phase 4: Integration and System Verification

- **Activities:** Integration test; System test; Interface conformance
- **Roles:** QA, Integrator
- **Deliverables:** Verification reports
- **Security controls:** Security testing
- **Compliance checkpoints:** Evidence mapped to controls, Interface conformance tests (SIP2 / NCIP / OAI-PMH / SSO), WCAG 2.1 AA audit with screen reader, Licence-limit tests (simultaneous users, download caps), Audit-log completeness and report-accuracy checks
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Verification gate recorded in the audit log
- **Human-approval gate:** Verification gate

### Phase 5: Acceptance and Release

- **Activities:** User acceptance testing; Deployment
- **Roles:** Librarians, Compliance Officer
- **Deliverables:** UAT sign-off
- **Security controls:** Hardening
- **Compliance checkpoints:** Compliance sign-off, Data-retention and deletion schedule verified, Accreditation report sample reviewed by librarian
- **Entry criteria:** Previous gate approved
- **Exit criteria:** Production-readiness approval recorded in the audit log
- **Human-approval gate:** Production-readiness approval
