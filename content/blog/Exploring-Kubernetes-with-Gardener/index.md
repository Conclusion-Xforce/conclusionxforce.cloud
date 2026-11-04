---
title: "Cloud Sovereignty Starts with Control: Exploring Kubernetes with Gardener"
subtitle: "How a consistent Kubernetes platform can preserve infrastructure choice"
description: "A hands-on Gardener experiment connecting Kubernetes lifecycle automation with cloud sovereignty, autonomy, and workload placement."
authors: ["Jeroen van de Lockand"]
date: '2026-11-04'
tags: ["Cloud Native", "Kubernetes", "Gardener", "Platform Engineering", "Cloud Sovereignty", "Multi-Cloud"]
draft: false
---

Cloud sovereignty is often discussed as a question of geography: which country
hosts the data, and which company operates the data center?

Those questions matter. But they do not tell the whole story.

An organization might keep its data in Europe and still depend on one provider
for cluster provisioning, upgrades, networking, identity, backups, and daily
operations. If changing that provider means rebuilding the platform from
scratch, how much freedom of choice does the organization really have?

For me, the more useful question is:

**Can we decide where to run which workloads, and retain control over how the
platform is operated?**

I explored that question through [Gardener](https://gardener.cloud/), an
open-source project for managing Kubernetes clusters. I installed Gardener
locally, created a Kubernetes cluster, recovered from a networking issue, and
watched the platform scale from two worker nodes to three when an application
needed more capacity.

The local experiment does not prove sovereignty. It does, however, demonstrate
one of the platform capabilities that can help make sovereignty practical.

## Application portability is not platform portability

Kubernetes gives application teams a largely consistent deployment API. A
Deployment, Service, or ConfigMap can often be used in different Kubernetes
environments with few changes.

But the clusters themselves are another matter.

Provisioning and operating a managed Kubernetes service usually involves
provider-specific APIs, infrastructure controllers, storage, networking,
identity integrations, and operational processes. Even when an application is
portable, recreating its entire platform elsewhere may not be.

That distinction matters when organizations want to make deliberate choices:

- Run a regulated workload on infrastructure under tighter operational control.
- Use a public cloud for applications that benefit from elastic capacity.
- Keep selected workloads close to existing on-premises systems.
- Change infrastructure providers without redesigning every platform workflow.

The goal is not to move everything between clouds every week. It is to
preserve meaningful options when business or regulatory requirements change.

## Meet Gardener: Garden, Seed, and Shoot

Gardener manages Kubernetes clusters through Kubernetes APIs and controllers.
Its architecture separates central management, control-plane hosting, and the
clusters consumed by application teams.

```text
Garden (central management)
  |
  +-- Projects, Shoot specifications, scheduling, lifecycle management
  |
  v
Seed (Kubernetes cluster hosting managed control planes)
  |
  +-- Shoot API server, etcd, controllers, supporting components
  |
  v
Shoot (Kubernetes cluster consumed by teams)
  |
  +-- Worker nodes, application workloads, cluster networking
```

The **Garden** is the central management layer. A **Seed** is a Kubernetes
cluster that hosts the control planes of Shoots assigned to it. A **Shoot** is
the Kubernetes cluster provided to a consumer.

This design is sometimes called *Kubeception*: Kubernetes is used to operate
the control planes of other Kubernetes clusters.

Gardener also provides an extension model for infrastructure-specific
operations. That is an important part of its value: cluster lifecycle
management can follow a consistent model while infrastructure integration
remains an explicit, replaceable concern.

It is not entirely provider-independent. The extensions, available services,
network topology, and operational responsibilities still matter. But the
platform team gains a common point of control for managing Shoots.

## The experiment: one local Garden, Seed, and Shoot

To move beyond architectural diagrams, I tested Gardener using KinD and the
Gardener Local Provider. The local provider represents worker machines as
Kubernetes Pods, so the experiment does not require a cloud account.

My environment contained a Garden, a local Seed, and a Shoot running Kubernetes
v1.37.0 with two worker nodes. I could inspect the same system from three
perspectives:

- **Virtual Garden API:** the desired Shoot and Seed configuration.
- **Runtime and Seed:** the Shoot control plane and machine-management
  components.
- **Shoot API:** the Kubernetes nodes and application workloads.

These are distinct responsibilities, even though the lab runs on one local
machine. In a production design, the placement and isolation of management
components require deliberate decisions.

### A useful failure along the way

The first Shoot did not become healthy immediately. Its API server and control
plane were already running, but both worker nodes remained `NotReady`.

The worker Pods existed and the kubelets registered their Nodes. The actual
blocker was Calico's networking initialization: the `log-mtu-issues` init
container crashed, preventing the CNI installation step from completing.

In this Fedora-based lab, I loaded the relevant host kernel modules and
restarted the affected Calico Pods. After that, Calico initialized, both Nodes
became `Ready`, and the MachineDeployment reported two available workers.

This was a useful reminder: infrastructure automation does not remove the need
for observability or troubleshooting. It does make the boundaries clearer.
I could distinguish a healthy managed control plane from an unhealthy worker
network, instead of treating the entire cluster as one black box.

## Let workloads drive capacity

Next, I tested whether Gardener could respond to changing workload demand.

The Shoot worker pool allowed the Cluster Autoscaler to manage capacity within
these boundaries:

```yaml
minimum: 1
maximum: 3
```

At that moment, the Shoot had two healthy workers. Increasing the maximum to
three did not immediately create another worker: a maximum is a limit, not a
target.

To create real demand, I deployed three lightweight application replicas with
required Pod anti-affinity. Each replica had to run on a different node.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autoscaling-demo
  namespace: autoscaling-demo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autoscaling-demo
  template:
    metadata:
      labels:
        app: autoscaling-demo
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: autoscaling-demo
              topologyKey: kubernetes.io/hostname
      containers:
        - name: nginx
          image: nginx:stable-alpine
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 64Mi
```

With only two workers available, the scheduler placed two replicas. The third
remained `Pending` because the required anti-affinity rule could not be met.

The Cluster Autoscaler recognized that adding a worker could resolve the
scheduling constraint. The desired machine capacity increased, the local
provider provisioned an additional worker, and the third application replica
was scheduled once the node was ready.

The sequence was straightforward:

```text
3 application replicas requested
             |
             v
2 replicas Running, 1 Pending
             |
             v
Cluster Autoscaler requests additional capacity
             |
             v
MachineDeployment grows from 2 to 3 workers
             |
             v
New Node becomes Ready; third replica starts
```

**The workload described its requirements. Kubernetes detected insufficient
capacity. The platform reconciled the infrastructure.**

That is the compelling Platform Engineering story: developers request an
outcome, while the platform manages the implementation.

The test was local, so it did not validate cloud-specific provisioning,
performance, or cost. It did validate the control flow end to end.

## Sovereignty needs more than data residency

What does worker autoscaling have to do with sovereignty?

On its own, not much. The connection lies in the separation between *what the
platform provides* and *where the underlying infrastructure comes from*.

A sovereignty strategy should consider at least three dimensions.

### Sovereignty: where are the dependencies?

Data residency is important, but so are control-plane placement, backups,
management access, telemetry, encryption keys, DNS, and external services.
A cluster with European worker nodes is not automatically a sovereign platform.

Gardener lets platform operators design where supported infrastructure and
control-plane components run. Whether the resulting service satisfies specific
sovereignty requirements depends on the whole architecture, its operators,
and the applicable contractual and legal controls.

### Autonomy: can we change direction?

The ability to select an alternative infrastructure provider is valuable even
when no migration is planned. A common Kubernetes lifecycle API can reduce
provider-specific work for platform consumers, provided the required Gardener
extensions and infrastructure capabilities are available.

This does not eliminate lock-in. Applications can still depend on proprietary
cloud databases, load balancers, identity services, storage interfaces, and
network configurations. Moving a running workload also requires a separate
migration strategy for its state and dependencies.

Autonomy is not the absence of dependencies. It is understanding them and
maintaining realistic alternatives.

### Control: where should each workload run?

Different applications have different requirements. A platform team might
provide Kubernetes clusters across private infrastructure, regional providers,
and hyperscalers, then expose approved choices through a consistent
self-service experience.

The decision can be driven by data classification, latency, resilience,
regulation, cost, and operational ownership rather than by whichever provider
was selected first.

Gardener does not itself decide the correct location for an application.
Those policies and placement choices still need to be designed and enforced.
It can provide an important cluster-management layer beneath that operating
model.

## Platform Engineering connects the pieces

None of this should force every developer to become an expert in multiple
cloud providers or Gardener's internal controllers.

A platform team can offer Kubernetes through predefined templates, approved
configurations, GitOps workflows, access controls, and guardrails. Developers
consume a consistent service; platform engineers retain control over its
implementation and lifecycle.

For a real sovereign-platform blueprint, I would extend this experiment with:

- A second infrastructure provider to test actual cross-provider consistency.
- Explicit Seed and Shoot placement rules and failure-domain boundaries.
- Policies for identity, network access, data flows, and cluster configuration.
- Recovery tests covering control planes, application data, and backups.
- An assessment of which cloud-specific services applications still need.

Those steps would turn a local proof of concept into measurable evidence for
infrastructure choice and operational independence.

## Conclusion: sovereignty is a capability

This experiment started with a simple question: can Gardener operate a
Kubernetes cluster and add capacity without manual infrastructure work?

In the local test, the answer was yes. I provisioned a Shoot, debugged a
networking issue, and watched an unschedulable workload trigger a third worker.

That does not mean Gardener automatically delivers sovereign cloud computing.
It means Gardener offers architectural building blocks for a platform where
Kubernetes lifecycle management and infrastructure choice can be treated as
separate concerns.

For me, **cloud sovereignty is not only about where something runs today. It is
about retaining the ability to decide where it should run tomorrow.**

And that is a Platform Engineering problem worth solving.

## Further reading

- [Gardener project](https://gardener.cloud/)
- [Gardener documentation](https://gardener.cloud/docs/)
- [Gardener source code](https://github.com/gardener/gardener)
- [Gardener Local Provider][local-provider]

[local-provider]: https://github.com/gardener/gardener-extension-provider-local