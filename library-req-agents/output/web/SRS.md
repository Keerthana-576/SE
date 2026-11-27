# Software Requirements Specification - College Library Management System

*Generated 2026-11-26 23:43 by the Library Requirements Multi-Agent Prototype. Advisory draft: nothing here is baselined until approved by authorised stakeholders.*

## 1. Summary

- Requirements extracted: **6** (0 rejected)
- Need clarification: **0**
- High-risk: **5**
- Compliance gaps found: **10**
- Recommended SDLC: **V-Model** (pending approval)
- Personal data masked before processing: none found
- Lines blocked as possible prompt injection: 0

## 2. Requirements

| ID | Requirement | Source | Priority | Categories | Risk | Conf. | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR-DIG-001 | The system shall allow Student users to access IEEE and Springer e-journals from off-campus using my university email ID without configuring a complex VPN | Student | Medium | Functional, Privacy, Operational, Copyright/Licence, Regulatory | High | 0.8 | Pending Approval |
| FR-REP-001 | The system shall allow downloading up to 50 research papers per day for thesis supervision, and cite them automatically in APA and BibTeX formats | Faculty | Medium | Functional | Low | 0.77 | Pending Approval |
| FR-GEN-001 | Simultaneous user access for the Economics database shall be strictly capped at 15 concurrent users, and bulk automated scraping must be blocked | Publisher | High | Functional, Copyright/Licence, Performance, Data Management, Regulatory | High | 0.93 | Pending Approval |
| FR-CIR-001 | The system shall provide monthly COUNTER-compliant usage statistics broken down by department to justify subscription renewals | Librarian | Medium | Functional, Copyright/Licence, Audit & Reporting, Regulatory | High | 0.8 | Pending Approval |
| FR-GEN-002 | The system shall be accessible for visually impaired students with screen-reader support and high-contrast modes | Admin | High | Functional, Accessibility, Regulatory | High | 0.93 | Pending Approval |
| FR-SEC-001 | All remote sessions shall enforce single sign-on (SSO) with multi-factor authentication and log user IP addresses for 180 days | It-security | High | Functional, Security, Privacy, Integration, Audit & Reporting, Regulatory | High | 0.9 | Pending Approval |

## 3. Requirement details

### FR-DIG-001

**Statement:** The system shall allow Student users to access IEEE and Springer e-journals from off-campus using my university email ID without configuring a complex VPN

**Source:** Student - original: "I need to access IEEE and Springer e-journals from off-campus using my university email ID without configuring a complex VPN."

**Categories:** Functional, Privacy, Operational, Copyright/Licence, Regulatory | **Priority:** Medium | **Risk:** High | **Confidence:** 0.8 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall allow Student users to access IEEE and Springer e-journals from off-campus using my university email ID without configuring a complex VPN.
2. Personal data is masked in logs and exports; consent and purpose are recorded where data is collected.

**Evidence (citations):**
- [KB-COPYRIGHT-LICENCE] Copyright Act, 1957 and publisher licence terms for e-resources (India, per-licence), retrieval score 0.488
- [KB-DPDP-2023] Digital Personal Data Protection Act, 2023 (India, 2023), retrieval score 0.392

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### FR-REP-001

**Statement:** The system shall allow downloading up to 50 research papers per day for thesis supervision, and cite them automatically in APA and BibTeX formats

**Source:** Faculty - original: "The portal should allow downloading up to 50 research papers per day for thesis supervision, and cite them automatically in APA and BibTeX formats."

**Categories:** Functional | **Priority:** Medium | **Risk:** Low | **Confidence:** 0.77 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall allow downloading up to 50 research papers per day for thesis supervision, and cite them automatically in APA and BibTeX formats.

**Evidence (citations):**
- [KB-OA-REPO] Institutional repository and open-access policy (UGC ETD regulations) (India, policy-v1), retrieval score 0.365
- [KB-COPYRIGHT-LICENCE] Copyright Act, 1957 and publisher licence terms for e-resources (India, per-licence), retrieval score 0.362

### FR-GEN-001

**Statement:** Simultaneous user access for the Economics database shall be strictly capped at 15 concurrent users, and bulk automated scraping must be blocked

**Source:** Publisher - original: "Simultaneous user access for the Economics database must be strictly capped at 15 concurrent users, and bulk automated scraping must be blocked."

**Categories:** Functional, Copyright/Licence, Performance, Data Management, Regulatory | **Priority:** High | **Risk:** High | **Confidence:** 0.93 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: Simultaneous user access for the Economics database shall be strictly capped at 15 concurrent users, and bulk automated scraping must be blocked.
2. Licence limits (simultaneous users, download caps) are enforced as written in the publisher agreement.
3. The agreed response-time target (value to be confirmed with stakeholders) is met under peak load.

**Evidence (citations):**
- [KB-COPYRIGHT-LICENCE] Copyright Act, 1957 and publisher licence terms for e-resources (India, per-licence), retrieval score 1.0
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.3

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### FR-CIR-001

**Statement:** The system shall provide monthly COUNTER-compliant usage statistics broken down by department to justify subscription renewals

**Source:** Librarian - original: "We need monthly COUNTER-compliant usage statistics broken down by department to justify subscription renewals."

**Categories:** Functional, Copyright/Licence, Audit & Reporting, Regulatory | **Priority:** Medium | **Risk:** High | **Confidence:** 0.8 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall provide monthly COUNTER-compliant usage statistics broken down by department to justify subscription renewals.
2. Licence limits (simultaneous users, download caps) are enforced as written in the publisher agreement.
3. Each relevant action records user ID, timestamp, action and outcome in the audit log.

**Evidence (citations):**
- [KB-ACCREDITATION] Accreditation and ranking data requirements (NAAC / NBA / NIRF) (India, per-cycle), retrieval score 0.513
- [KB-COPYRIGHT-LICENCE] Copyright Act, 1957 and publisher licence terms for e-resources (India, per-licence), retrieval score 0.377
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.3

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### FR-GEN-002

**Statement:** The system shall be accessible for visually impaired students with screen-reader support and high-contrast modes

**Source:** Admin - original: "The portal must be accessible for visually impaired students with screen-reader support and high-contrast modes."

**Categories:** Functional, Accessibility, Regulatory | **Priority:** High | **Risk:** High | **Confidence:** 0.93 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall be accessible for visually impaired students with screen-reader support and high-contrast modes.
2. Affected screens pass a WCAG 2.1 AA check and work with a screen reader and keyboard only.

**Evidence (citations):**
- [KB-RPWD-WCAG] Rights of Persons with Disabilities Act, 2016 and WCAG 2.1 AA (India / International, WCAG-2.1-AA), retrieval score 1.0

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### FR-SEC-001

**Statement:** All remote sessions shall enforce single sign-on (SSO) with multi-factor authentication and log user IP addresses for 180 days

**Source:** It-security - original: "All remote sessions must enforce single sign-on (SSO) with multi-factor authentication and log user IP addresses for 180 days."

**Categories:** Functional, Security, Privacy, Integration, Audit & Reporting, Regulatory | **Priority:** High | **Risk:** High | **Confidence:** 0.9 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: All remote sessions shall enforce single sign-on (SSO) with multi-factor authentication and log user IP addresses for 180 days.
2. Attempts by unauthorised roles are rejected and the attempt is logged.
3. Personal data is masked in logs and exports; consent and purpose are recorded where data is collected.
4. The interface passes a conformance test against the agreed standard (e.g. SIP2, NCIP, OAI-PMH) in the test environment.
5. Each relevant action records user ID, timestamp, action and outcome in the audit log.

**Evidence (citations):**
- [KB-ASVS] Application security controls (OWASP ASVS / ISO 27001 aligned) (International, 4.0.3), retrieval score 0.907
- [KB-ITACT-2000] Information Technology Act, 2000 and institutional IT security policy (India, 2000-amended), retrieval score 0.685
- [KB-POL-RECORDS] Institutional records retention and audit policy (placeholder) (Institution, policy-v1), retrieval score 0.349

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

## 4. Open questions for stakeholders

- **Missing area - Availability:** What uptime, backup and recovery expectations apply?

## 5. Compliance gaps and suggested additions (not baselined)

| Policy | Missing control | Suggested requirement |
| --- | --- | --- |
| KB-DPDP-2023 | Consent and notice | The system shall record each member's consent and the purpose for which personal data is collected, and display a privacy notice at registration. |
| KB-DPDP-2023 | Retention and deletion | The system shall retain borrowing history only for the institution-approved retention period and then delete or anonymise it. |
| KB-DPDP-2023 | Data-subject rights | The system shall let members request access to, correction of, or erasure of their personal data, with each request logged. |
| KB-ITACT-2000 | Role-based access control | The system shall enforce role-based access control so each staff and member role can access only the functions and data it needs. |
| KB-ITACT-2000 | Encryption | The system shall encrypt personal and transaction data in transit and at rest. |
| KB-OA-REPO | Embargo handling | The system shall support embargo periods on deposited theses and release them automatically on the approved date. |
| KB-OA-REPO | Descriptive metadata | The system shall capture Dublin Core metadata for every deposited item. |
| KB-ACCREDITATION | Evidence export | The system shall export accreditation reports by academic year in CSV and PDF with drill-down to source records. |
| KB-POL-LENDING | Configurable policy parameters | The system shall let an authorised administrator configure loan period, borrowing limit and fine rate per member category. |
| KB-POL-RECORDS | Backup and recovery | The system shall back up data daily and support recovery within the institution-approved RTO and RPO. |

## 6. Approvals

No approvals recorded (advisory mode). All items are pending human approval.

## 7. SDLC recommendation

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

## 8. Disclaimer

Policy mappings come from an illustrative knowledge base and are not legal determinations. A compliance or legal officer must verify and approve every mapping.