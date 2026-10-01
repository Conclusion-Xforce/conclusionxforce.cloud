---
title: Certificate Lifecycle as Code
subtitle: Bringing GitOps and Platform Engineering principles to certificate management
description: How to manage certificate issuance, renewal, and governance using declarative configuration and GitOps practices.
authors: [Jeroen van de Lockand]
date: '2026-09-25'
tags: [Platform Engineering, Security, GitOps, Kubernetes, Certificates, Cloud Native]
draft: false
---

Modern platforms increasingly embrace Infrastructure as Code, Policy as Code,
and GitOps. Yet many organizations still manage one of their most critical
security assets manually: certificates.

Certificates often live in spreadsheets, ticketing systems, email reminders,
or someone's personal calendar. Renewals are performed manually, ownership is
unclear, and expiration events are only discovered when something breaks in
production.

In this article, I introduce **Certificate Lifecycle as Code**, a demonstration
project that explores how certificate management can be treated as a fully
declarative, automated, and auditable process.

## The Problem

Many organizations have matured their cloud-native operating model but still
rely on manual certificate processes.

Common challenges include:

- Unknown certificate ownership
- Expiring certificates causing outages
- Lack of inventory and visibility
- Inconsistent renewal procedures
- No clear audit trail
- High operational overhead

The larger the platform footprint becomes, the more difficult it is to maintain
a complete view of certificate usage across environments, clusters,
applications, APIs, ingress controllers, service meshes, and external
integrations.

Certificates become operational debt.

## Applying Cloud Native Principles

When we look at modern Platform Engineering practices, we already know how to
solve similar challenges.

We use:

- Infrastructure as Code
- GitOps
- Configuration as Code
- Policy as Code
- Observability

So why not apply the same principles to certificates?

This is the core idea behind **Certificate Lifecycle as Code**:

> Treat certificates as managed platform resources that are defined, governed,
> and automated through code.

Instead of managing individual certificates manually, the desired state becomes
declarative and version controlled.

## What Is Certificate Lifecycle as Code?

Certificate Lifecycle as Code shifts certificate management from an operational
activity to a platform capability.

Rather than asking:

> "When does this certificate expire?"

We ask:

> "What certificates should exist and what is their desired lifecycle?"

A declarative configuration defines:

- Ownership
- Environments
- Domains
- Certificate authority
- Renewal policies
- Compliance requirements
- Validity periods

Git becomes the source of truth.

Changes are introduced through pull requests, reviewed through standard
engineering processes, and audited automatically.

## Architecture Overview

The demo repository demonstrates a workflow where:

1. Certificate definitions are stored in Git.
2. Validation occurs through automated pipelines.
3. Policy checks verify compliance requirements.
4. Lifecycle information is centrally maintained.
5. Changes are reviewed through pull requests.
6. Automation performs lifecycle operations where possible.

This creates a model very similar to how Platform Teams already manage:

- Kubernetes manifests
- Terraform resources
- OpenShift configurations
- Security policies

## Why Platform Teams Should Care

Certificate management is often viewed as a security responsibility.

In reality it is a shared concern between:

- Security teams
- Platform teams
- Application teams
- Operations teams

Platform Engineering provides an opportunity to standardize certificate
consumption and management through reusable platform patterns.

Benefits include:

### Reduced Operational Risk

Manual renewals are one of the most common sources of preventable outages.

Automation dramatically reduces this risk.

### Improved Auditability

Every change becomes traceable through Git history.

Questions such as:

- Who requested the certificate?
- Who approved it?
- Why was it changed?

can be answered immediately.

### Better Developer Experience

Application teams should consume certificates as platform services rather than
managing certificate lifecycles themselves.

This aligns with Golden Path principles and self-service platform capabilities.

### Consistent Governance

Policy validation can ensure that:

- Approved certificate authorities are used
- Ownership is defined
- Required metadata exists
- Naming conventions are enforced

## GitOps for Security Operations

One of the most interesting aspects of this approach is how naturally it aligns
with GitOps.

The same patterns we use for deploying applications can be applied to
certificate management.

Desired state:

```yaml
certificate:
  name: api-certificate
  domain: api.company.com
  owner: payments-team
  validity: 90d
  environment: production
```

Operational state is continuously reconciled against the declared state.

This creates a predictable and repeatable operating model that scales much
better than manual processes.

## Lessons Learned

While building this demonstration project, several observations stood out:

### Security and Platform Engineering Are Converging

Modern security teams increasingly rely on automation and platform capabilities.

Certificate management is a strong example where security requirements and
platform engineering practices intersect.

### Visibility Matters

Most organizations know they have certificates.

Far fewer can answer:

- How many certificates exist?
- Who owns them?
- Which ones expire next month?
- Which applications depend on them?

Centralized lifecycle management improves visibility dramatically.

### Governance Must Be Built In

Governance should not be an additional process layer.

The best platform experiences make governance automatic through policy
validation and platform guardrails.

## Future Opportunities

The demo repository focuses on the foundational concepts, but the same approach
can be extended further.

Examples include:

- cert-manager integration
- Kubernetes automation
- OpenShift deployment patterns
- External PKI integrations
- Certificate inventory dashboards
- Expiration observability
- Policy enforcement with Kyverno
- Platform self-service workflows

These capabilities can ultimately become part of a broader platform security offering.

## Conclusion

Infrastructure as Code transformed how we provision environments.

GitOps transformed how we deploy applications.

Policy as Code transformed how we enforce governance.

Certificate Lifecycle as Code applies the same proven principles to certificate management.

By treating certificates as declarative, version controlled platform resources,
organizations can reduce operational risk, improve governance, increase
visibility, and provide a better experience for development teams.

The goal is not simply to automate certificate renewal.

The goal is to make certificate management a native platform capability.

## Repository

Explore the demonstration project:

GitHub Repository: [Certificate Lifecycle as Code](https://github.com/jeroenvandelockand/certificate-lifecycle-as-code)
