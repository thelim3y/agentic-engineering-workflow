# Standards and compliance

Status: reference direction; no conformity or certification claim.

There is no single standard that certifies software as good. Different standards
cover lifecycle processes, product quality, testing, security and organizational
governance.

## Relevant standards

| Reference | Scope | Relevance |
|---|---|---|
| [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html) | Software lifecycle processes | Primary vocabulary for lifecycle activities, roles, verification, maintenance and improvement. |
| [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) | Product quality model | Basis for configurable quality requirements, gates and acceptance criteria. |
| [ISO/IEC/IEEE 29119](https://committee.iso.org/sites/jtc1sc7/home/projects/flagship-standards/isoiecieee-29119-series.html) | Software testing | Selective guidance for test processes, documentation and techniques. |
| [NIST SP 800-218 SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | Secure software development | Practical basis for security checks and development controls. It is not an ISO standard. |
| [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) | Information-security management | Organizational governance for credentials, access, infrastructure, audit storage and incidents. |
| [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) | AI management systems | Organizational governance for AI risk, accountability, transparency and continual improvement. |
| [ISO 9001:2026](https://www.iso.org/standard/9001) | Quality-management systems | General organizational quality management; it is not software-specific. |

Safety-critical or regulated targets may also require domain standards such as
ISO 26262, IEC 62304, IEC 61508 or DO-178C. They are not default factory policy.

## Claim boundaries

- Standards alignment means selected requirements are mapped to factory controls
  and evidence. It does not mean conformity or certification.
- Conformity requires a defined scope, applicable requirements and objective evidence.
- Certification applies only where the standard supports it and an authorized
  independent assessment has occurred. It normally covers an organization's
  management system, not a generic claim that an application is ISO certified.
- Audit records can support an assessment. They do not make an agent statement true
  or establish compliance by themselves; see [Audit](audit.md).

Until these conditions are met, describe the factory as standards-aware, not
compliant, conformant or certified.

## Project direction

Use ISO/IEC/IEEE 12207 for lifecycle terminology, ISO/IEC 25010 for quality and
NIST SSDF for secure-development controls. Draw selectively from ISO/IEC/IEEE
29119 where it improves testing without importing unnecessary paperwork.

Do not implement a complete standard by default. Future compliance profiles may
map versioned requirements to configuration, gates and retained evidence. Profiles
must identify the exact standard edition, scope, unsupported requirements and
evidence produced. ISO/IEC 27001, ISO/IEC 42001 and ISO 9001 include organizational
responsibilities outside the factory; the product can support their evidence needs
but cannot satisfy them alone.
