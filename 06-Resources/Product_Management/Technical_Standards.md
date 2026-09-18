# Technical Standards

## Purpose
This document defines the **non-negotiable technical expectations** for all technical teams. The goal is to ensure consistent quality, security, compliance, and operational reliability across all systems.
These standards apply to **all environments** (dev, UAT, staging, production) and **all codebases**, regardless of language, framework, or team.
Failure to comply introduces real security, legal, and operational risk — this document exists to remove ambiguity.

---

## 1. Source Control & Code Ownership

### 1.1 Mandatory Source Control
*   **All code must live in an approved source control system** (e.g. GitHub, Azure DevOps).
*   No local-only, shared-drive, or ad-hoc code is permitted.

### 1.2 Commit Discipline
*   Commits must be pushed **regularly and frequently**.
*   Long-lived unpushed work is not acceptable.
*   Commit messages must be meaningful and explain intent.

---

## 2. Code Review & Approval

### 2.1 Peer Review Required
*   **Every code change must be reviewed and approved by at least one other qualified technical peer** before merge.
*   Self-approval is not allowed.

### 2.2 Review Expectations
Code reviews must validate:
*   Correctness and logic
*   Security implications
*   Performance considerations
*   Adherence to code standards
*   Test coverage

Approval means shared accountability.

---

## 3. Code Standards & Quality

### 3.1 Consistent Standards
*   **Code standards must be applied consistently across all repositories**.
*   Standards include (but are not limited to):
    *   Naming conventions
    *   Formatting
    *   Error handling
    *   Logging practices
    *   Project structure

### 3.2 Automated Enforcement
*   Linting and formatting rules **must be enforced automatically** via tooling and pipelines.
*   Manual enforcement alone is not sufficient.

### 3.3 Testing Is Mandatory
*   **All code must have automated tests to prove it works as intended**.
*   New features must include appropriate test coverage.
*   **Bug fixes must include tests that reproduce the issue and prove the fix**.
*   Tests should be meaningful and validate behaviour, not just implementation details.

### 3.4 Test Execution
*   Tests must run **automatically as part of CI pipelines**.
*   **All CI pipelines must include automated test execution as a mandatory stage**.
*   Pipelines must fail on test failures — manual overrides are not acceptable.
*   Code that breaks tests or reduces coverage without explicit approval must not be merged.

Untested code is considered incomplete code.

---

## 4. Security Scanning & Vulnerability Management

### 4.1 Mandatory Scanning
*   **All code must be scanned for vulnerabilities and code quality issues**.
*   Scanning must include:
    *   Static code analysis
    *   Dependency vulnerability scanning
    *   Security misconfiguration detection (where applicable)

### 4.2 Automated Checks
*   Automated checks **must exist** to monitor libraries and packages for known vulnerabilities.
*   Builds should fail or alert on high-risk findings.

### 4.3 Vulnerability Severity & Response
*   **High and Critical vulnerabilities must be attended to immediately**.
*   High/Critical findings must:
    *   Block merges and deployments where possible
    *   Be prioritised over feature work
    *   Be tracked until remediated or explicitly risk-accepted by technical leadership
*   Temporary mitigations must be documented if full remediation is not immediately possible.

Ignoring High or Critical vulnerabilities is not acceptable.
Security is not optional or best-effort.

---

## 5. Libraries, Packages & Licensing

### 5.1 Approval Required
*   **New libraries, frameworks, or packages must be approved before use**.
*   Approval includes:
    *   License compatibility
    *   Security posture
    *   Maintenance and community support

### 5.2 Continuous Monitoring
*   Approved packages must remain under automated vulnerability monitoring.
*   Deprecated or unmaintained dependencies must be addressed proactively.

---

## 6. Secrets & Sensitive Configuration

### 6.1 Secure Storage Required
*   **All secrets, API keys, credentials, tokens, certificates, and sensitive values must be stored in a secure secrets manager** (e.g. Key Vault or equivalent).
*   Secrets must **never** be stored in:
    *   Source code
    *   Configuration files checked into source control
    *   CI/CD pipeline definitions in plain text
    *   Documentation or tickets

### 6.2 Access & Usage
*   Secrets must be accessed at runtime via secure mechanisms (managed identities, secret references, or injected variables).
*   Access to secrets must follow the principle of least privilege.
*   Secrets must be rotated regularly according to security policy.

### 6.3 Detection & Enforcement
*   Automated scanning must be in place to detect secrets committed to source control.
*   Any exposed secret must be treated as compromised and rotated immediately.

Hard-coding secrets is a security incident.

---

## 7. CI/CD & Deployment

### 7.1 Pipeline-Only Deployments
*   **All deployments must happen through approved CI/CD pipelines**.
*   Manual deployments are not allowed.

### 7.2 Environment Parity
*   Pipelines must be consistent across environments.
*   What runs in production must be reproducible from source control.

Pipelines are the single source of truth for releases.

---

## 8. Infrastructure & Resource Management

### 8.1 Scripted Provisioning
*   **All infrastructure and resources must be provisioned via scripts** (IaC).
*   Manual creation or modification of resources is not acceptable.

### 8.2 Change Management
*   Any of the following **must go through change management before execution**:
    *   New resource provisioning
    *   Resource configuration changes
    *   Scaling changes
    *   Security or network changes

No exceptions — even for non-production environments.

---

## 9. Access Control & Least Privilege

### 9.1 Least Privilege Principle
*   **You should only have access to resources required to perform your role**.
*   Standing admin or broad access is not acceptable.

### 9.2 Access Reviews
*   Access must be reviewed regularly.
*   Temporary access must be time-boxed and revoked when no longer needed.

---

## 10. Audit Logging & Traceability

### 10.1 User Action Auditing
*   **All user actions must be captured in audit logs**.
*   This includes (but is not limited to):
    *   Authentication and authorisation events
    *   Data access (read, write, export, delete)
    *   Configuration changes
    *   Administrative actions
    *   Security-sensitive operations

### 10.2 Audit Log Requirements
*   Audit logs must:
    *   Be immutable and tamper-resistant
    *   Include who performed the action, what was done, when it occurred, and where it originated
    *   Be retained according to compliance and regulatory requirements

### 10.3 Access & Monitoring
*   Audit logs must be accessible to authorised security and technical staff.
*   Logs must be monitored for suspicious or anomalous behaviour.
*   Gaps in audit logging are considered security defects and must be prioritised.

If an action is not auditable, it is not acceptable.

---

## 11. AI Tooling & Assisted Technical Work

### 11.1 Approved Tools Only
*   **Only approved AI models and copilots may be used for coding**.
*   Use of unapproved AI tools that upload proprietary code or data is prohibited.

### 11.2 Responsibility Remains Human
*   AI-generated code is treated the same as human-written code.
*   It must be reviewed, tested, scanned, and approved like any other change.

AI accelerates technical work — it does not remove accountability.

---

## 12. Accountability & Enforcement
*   These standards apply to **everyone**.
*   Repeated non-compliance will be addressed through technical leadership.
*   Shortcuts that bypass controls create systemic risk and will be corrected.

Quality, security, and reliability are shared responsibilities.

---

## Summary (Non-Negotiables)
*   Code review is mandatory
*   Pipelines only — no manual deploys
*   Security scanning is required
*   Infrastructure is scripted
*   Access is minimal
*   Libraries are approved
*   AI usage is controlled

This is the baseline. Anything less is not acceptable.
