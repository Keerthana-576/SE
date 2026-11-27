# Software Requirements Specification - College Library Management System

*Generated 2026-11-23 05:24 by the Library Requirements Multi-Agent Prototype. Advisory draft: nothing here is baselined until approved by authorised stakeholders.*

## 1. Summary

- Requirements extracted: **15** (0 rejected)
- Need clarification: **9**
- High-risk: **5**
- Compliance gaps found: **12**
- Recommended SDLC: **Agile-V-Model hybrid** (pending approval)
- Personal data masked before processing: {'PHONE': 1, 'EMAIL': 1, 'MEMBER_ID': 1}
- Lines blocked as possible prompt injection: 1

## 2. Requirements

| ID | Requirement | Source | Priority | Categories | Risk | Conf. | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR-CIR-001 | The system shall allow Student users to renew books online without visiting the library | Student | Medium | Functional | Low | 0.78 | Pending Approval |
| BR-CIR-001 | The loan period shall be 21 days for undergraduates | Student | Medium | Business | Low | 0.64 | Needs Clarification |
| NFR-GEN-001 | The system shall be fast | Student | High | Performance | Low | 0.65 | Needs Clarification |
| BR-CIR-002 | Loan period shall be 14 days for all members | Librarian | High | Business | Low | 0.65 | Needs Clarification |
| FR-CIR-002 | The system shall block issue if the member's fines exceed the limit | Librarian | High | Functional, Business | Low | 0.84 | Needs Clarification |
| FR-GEN-001 | The system shall allow librarians to override a block when needed | Librarian | Medium | Functional, Business | Low | 0.71 | Needs Clarification |
| BR-CIR-003 | Fine shall be Rs 2 per day per book | Librarian | Medium | Business | Low | 0.66 | Needs Clarification |
| FR-RPT-001 | Members' reading history shall be stored for analytics | Librarian | Medium | Functional, Privacy, Data Management, Audit & Reporting | High | 0.78 | Pending Approval |
| BR-CIR-004 | Fine of Rs 5 per day per book shall be charged for overdue items | Admin | High | Business | Low | 0.75 | Needs Clarification |
| FR-RPT-002 | The system shall provide reports for NAAC accreditation, etc | Admin | Medium | Functional, Regulatory, Audit & Reporting | High | 0.79 | Needs Clarification |
| FR-DIG-001 | The system shall provide remote access to e-journals from home with a user-friendly interface | Faculty | Medium | Functional, Usability, Copyright/Licence, Regulatory, Accessibility | High | 0.77 | Needs Clarification |
| FR-REP-001 | Theses shall be deposited in the repository with open access after the embargo | Faculty | Medium | Functional, Regulatory, Data Management | High | 0.93 | Pending Approval |
| NFR-INT-001 | The system shall integrate with Koha and the university ERP using SIP2 | IT Admin | High | Integration | Medium | 0.93 | Pending Approval |
| FR-INT-001 | The system shall support RFID self-checkout kiosks | IT Admin | High | Functional, Integration | Medium | 0.92 | Pending Approval |
| NFR-SEC-001 | The system shall use the university single sign-on for staff login | IT Security | High | Security | High | 0.89 | Pending Approval |

## 3. Requirement details

### FR-CIR-001

**Statement:** The system shall allow Student users to renew books online without visiting the library

**Source:** Student - original: "I want to renew books online without visiting the library."

**Categories:** Functional | **Priority:** Medium | **Risk:** Low | **Confidence:** 0.78 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall allow Student users to renew books online without visiting the library.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.414
- [KB-RPWD-WCAG] Rights of Persons with Disabilities Act, 2016 and WCAG 2.1 AA (India / International, WCAG-2.1-AA), retrieval score 0.36

### BR-CIR-001

**Statement:** The loan period shall be 21 days for undergraduates

**Source:** Student - original: "The loan period should be 21 days for undergraduates."

**Categories:** Business | **Priority:** Medium | **Risk:** Low | **Confidence:** 0.64 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The loan period shall be 21 days for undergraduates.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.463

**Quality issues:**
- Conflict (High): Conflicts with BR-CIR-002 (differ on loan period).

### NFR-GEN-001

**Statement:** The system shall be fast

**Source:** Student - original: "The system must be fast."

**Categories:** Performance | **Priority:** High | **Risk:** Low | **Confidence:** 0.65 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall be fast.
2. The agreed response-time target (value to be confirmed with stakeholders) is met under peak load.

**Quality issues:**
- Ambiguity (Medium): Vague term 'fast'.
- Incomplete (Medium): Statement is too short to test.

### BR-CIR-002

**Statement:** Loan period shall be 14 days for all members

**Source:** Librarian - original: "Loan period must be 14 days for all members."

**Categories:** Business | **Priority:** High | **Risk:** Low | **Confidence:** 0.65 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: Loan period shall be 14 days for all members.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.5

**Quality issues:**
- Conflict (High): Conflicts with BR-CIR-001 (differ on loan period).

### FR-CIR-002

**Statement:** The system shall block issue if the member's fines exceed the limit

**Source:** Librarian - original: "The system must block issue if the member's fines exceed the limit."

**Categories:** Functional, Business | **Priority:** High | **Risk:** Low | **Confidence:** 0.84 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall block issue if the member's fines exceed the limit.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.94

**Quality issues:**
- Incomplete (High): A limit/period/rate is mentioned but no value is given.

### FR-GEN-001

**Statement:** The system shall allow librarians to override a block when needed

**Source:** Librarian - original: "Librarians should be able to override a block when needed."

**Categories:** Functional, Business | **Priority:** Medium | **Risk:** Low | **Confidence:** 0.71 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall allow librarians to override a block when needed.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.882

**Quality issues:**
- Ambiguity (Medium): Vague term 'when needed'.
- Missing control (High): Override/waiver without logging or authorisation.

### BR-CIR-003

**Statement:** Fine shall be Rs 2 per day per book

**Source:** Librarian - original: "Fine should be Rs 2 per day per book."

**Categories:** Business | **Priority:** Medium | **Risk:** Low | **Confidence:** 0.66 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: Fine shall be Rs 2 per day per book.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.548

**Quality issues:**
- Conflict (High): Conflicts with BR-CIR-004 (differ on fine rate).

### FR-RPT-001

**Statement:** Members' reading history shall be stored for analytics

**Source:** Librarian - original: "Members' reading history should be stored for analytics."

**Categories:** Functional, Privacy, Data Management, Audit & Reporting | **Priority:** Medium | **Risk:** High | **Confidence:** 0.78 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: Members' reading history shall be stored for analytics.
2. Personal data is masked in logs and exports; consent and purpose are recorded where data is collected.
3. Each relevant action records user ID, timestamp, action and outcome in the audit log.

**Evidence (citations):**
- [KB-DPDP-2023] Digital Personal Data Protection Act, 2023 (India, 2023), retrieval score 0.436
- [KB-ACCREDITATION] Accreditation and ranking data requirements (NAAC / NBA / NIRF) (India, per-cycle), retrieval score 0.396
- [KB-POL-RECORDS] Institutional records retention and audit policy (placeholder) (Institution, policy-v1), retrieval score 0.384

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### BR-CIR-004

**Statement:** Fine of Rs 5 per day per book shall be charged for overdue items

**Source:** Admin - original: "Fine of Rs 5 per day per book must be charged for overdue items."

**Categories:** Business | **Priority:** High | **Risk:** Low | **Confidence:** 0.75 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: Fine of Rs 5 per day per book shall be charged for overdue items.

**Evidence (citations):**
- [KB-POL-LENDING] Institutional lending and fines policy (placeholder) (Institution, policy-v1), retrieval score 0.898

**Quality issues:**
- Conflict (High): Conflicts with BR-CIR-003 (differ on fine rate).

### FR-RPT-002

**Statement:** The system shall provide reports for NAAC accreditation, etc

**Source:** Admin - original: "We need reports for NAAC accreditation, etc."

**Categories:** Functional, Regulatory, Audit & Reporting | **Priority:** Medium | **Risk:** High | **Confidence:** 0.79 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall provide reports for NAAC accreditation, etc.
2. Compliance evidence is attached and the compliance officer has signed off the mapped policy.
3. Each relevant action records user ID, timestamp, action and outcome in the audit log.

**Evidence (citations):**
- [KB-ACCREDITATION] Accreditation and ranking data requirements (NAAC / NBA / NIRF) (India, per-cycle), retrieval score 0.909

**Quality issues:**
- Ambiguity (Medium): Vague term 'etc'.

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### FR-DIG-001

**Statement:** The system shall provide remote access to e-journals from home with a user-friendly interface

**Source:** Faculty - original: "I need remote access to e-journals from home with a user-friendly interface."

**Categories:** Functional, Usability, Copyright/Licence, Regulatory, Accessibility | **Priority:** Medium | **Risk:** High | **Confidence:** 0.77 | **Status:** Needs Clarification

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall provide remote access to e-journals from home with a user-friendly interface.

**Evidence (citations):**
- [KB-COPYRIGHT-LICENCE] Copyright Act, 1957 and publisher licence terms for e-resources (India, per-licence), retrieval score 0.848
- [KB-RPWD-WCAG] Rights of Persons with Disabilities Act, 2016 and WCAG 2.1 AA (India / International, WCAG-2.1-AA), retrieval score 0.755

**Quality issues:**
- Ambiguity (Medium): Vague term 'user-friendly'.

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### FR-REP-001

**Statement:** Theses shall be deposited in the repository with open access after the embargo

**Source:** Faculty - original: "Theses should be deposited in the repository with open access after the embargo."

**Categories:** Functional, Regulatory, Data Management | **Priority:** Medium | **Risk:** High | **Confidence:** 0.93 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: Theses shall be deposited in the repository with open access after the embargo.

**Evidence (citations):**
- [KB-OA-REPO] Institutional repository and open-access policy (UGC ETD regulations) (India, policy-v1), retrieval score 1.0
- [KB-OAI-PMH] OAI-PMH 2.0 for repository metadata harvesting (International, 2.0), retrieval score 0.404

**Human review required:**
- Policy/regulatory interpretation must be approved by the compliance or legal officer.

### NFR-INT-001

**Statement:** The system shall integrate with Koha and the university ERP using SIP2

**Source:** IT Admin - original: "The system must integrate with Koha and the university ERP using SIP2."

**Categories:** Integration | **Priority:** High | **Risk:** Medium | **Confidence:** 0.93 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall integrate with Koha and the university ERP using SIP2.
2. The interface passes a conformance test against the agreed standard (e.g. SIP2, NCIP, OAI-PMH) in the test environment.

**Evidence (citations):**
- [KB-SIP2-NCIP] Circulation interoperability standards: SIP2 and NCIP (ANSI/NISO Z39.83) (International, SIP2-2.00), retrieval score 1.0

### FR-INT-001

**Statement:** The system shall support RFID self-checkout kiosks

**Source:** IT Admin - original: "The system shall support RFID self-checkout kiosks."

**Categories:** Functional, Integration | **Priority:** High | **Risk:** Medium | **Confidence:** 0.92 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall support RFID self-checkout kiosks.
2. The interface passes a conformance test against the agreed standard (e.g. SIP2, NCIP, OAI-PMH) in the test environment.

**Evidence (citations):**
- [KB-SIP2-NCIP] Circulation interoperability standards: SIP2 and NCIP (ANSI/NISO Z39.83) (International, SIP2-2.00), retrieval score 0.973

### NFR-SEC-001

**Statement:** The system shall use the university single sign-on for staff login

**Source:** IT Security - original: "The system must use the university single sign-on for staff login."

**Categories:** Security | **Priority:** High | **Risk:** High | **Confidence:** 0.89 | **Status:** Pending Approval

**Acceptance criteria:**
1. Verified by at least one positive and one negative test case for: The system shall use the university single sign-on for staff login.
2. Attempts by unauthorised roles are rejected and the attempt is logged.

**Evidence (citations):**
- [KB-ASVS] Application security controls (OWASP ASVS / ISO 27001 aligned) (International, 4.0.3), retrieval score 0.86
- [KB-ITACT-2000] Information Technology Act, 2000 and institutional IT security policy (India, 2000-amended), retrieval score 0.356
- [KB-POL-RECORDS] Institutional records retention and audit policy (placeholder) (Institution, policy-v1), retrieval score 0.3

## 4. Open questions for stakeholders

- BR-CIR-001 and BR-CIR-002 give different values for loan period. Which applies, or does it vary by member category?
- NFR-GEN-001: you used 'fast'. What measurable target applies (a number, time, standard or list)?
- NFR-GEN-001: can you describe the expected behaviour in more detail?
- FR-CIR-002: what is the exact value (or who approves it) for the limit, period or rate mentioned?
- FR-GEN-001: you used 'when needed'. What measurable target applies (a number, time, standard or list)?
- FR-GEN-001: who may override, and should every override be logged with the user ID and a reason?
- BR-CIR-003 and BR-CIR-004 give different values for fine rate. Which applies, or does it vary by member category?
- FR-RPT-002: you used 'etc'. What measurable target applies (a number, time, standard or list)?
- FR-DIG-001: you used 'user-friendly'. What measurable target applies (a number, time, standard or list)?
- **Missing area - Accessibility:** Which accessibility needs (screen readers, keyboard use, accessible formats) must be supported?
- **Missing area - Availability:** What uptime, backup and recovery expectations apply?

## 5. Compliance gaps and suggested additions (not baselined)

| Policy | Missing control | Suggested requirement |
| --- | --- | --- |
| KB-DPDP-2023 | Consent and notice | The system shall record each member's consent and the purpose for which personal data is collected, and display a privacy notice at registration. |
| KB-DPDP-2023 | Retention and deletion | The system shall retain borrowing history only for the institution-approved retention period and then delete or anonymise it. |
| KB-DPDP-2023 | Data-subject rights | The system shall let members request access to, correction of, or erasure of their personal data, with each request logged. |
| KB-ITACT-2000 | Role-based access control | The system shall enforce role-based access control so each staff and member role can access only the functions and data it needs. |
| KB-ITACT-2000 | Encryption | The system shall encrypt personal and transaction data in transit and at rest. |
| KB-COPYRIGHT-LICENCE | Licence-limit enforcement | The system shall enforce each e-resource licence's simultaneous-user and download limits and block bulk downloading. |
| KB-COPYRIGHT-LICENCE | Usage statistics | The system shall record e-resource usage statistics per resource and academic year for licence renewal and reporting. |
| KB-RPWD-WCAG | Accessibility conformance | The system's web interface shall conform to WCAG 2.1 level AA and be usable with a screen reader and keyboard alone. |
| KB-OA-REPO | Descriptive metadata | The system shall capture Dublin Core metadata for every deposited item. |
| KB-ACCREDITATION | Evidence export | The system shall export accreditation reports by academic year in CSV and PDF with drill-down to source records. |
| KB-POL-LENDING | Configurable policy parameters | The system shall let an authorised administrator configure loan period, borrowing limit and fine rate per member category. |
| KB-POL-RECORDS | Backup and recovery | The system shall back up data daily and support recovery within the institution-approved RTO and RPO. |

## 6. Approvals

No approvals recorded (advisory mode). All items are pending human approval.

## 7. SDLC recommendation

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

## 8. Disclaimer

Policy mappings come from an illustrative knowledge base and are not legal determinations. A compliance or legal officer must verify and approve every mapping.