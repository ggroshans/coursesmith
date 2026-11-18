# Gaps: containers-orchestration-and-deployment (chunks 01-03)

- Canary release: no own page crawled; only a few sentences (Kubernetes deployment strategies guide, Blue-green page). Suggested page: "Feature toggle" and a "Canary release" source.
- Rolling update / rolling deployment: only one-line guide sentences. Suggested: Kubernetes docs "Deployments" (doc>) or "Continuous delivery".
- Feature toggle: named in the top-5 deployment strategies list with no explanation. Suggested page: "Feature toggle".
- Continuous integration / continuous delivery pipeline: linked from Blue-green deployment, not in the dossier. Suggested pages: "Continuous delivery", "CI/CD".
- Hypervisor: only Singh and Virtual machine sentences. Suggested page: "Hypervisor".
- Linux namespaces, cgroups and chroot: no own page crawled. Suggested pages: "Linux namespaces", "Cgroups", "Chroot".
- Container orchestration (as a general concept): only Kubernetes, Docker Swarm and the Kubernetes guide. Suggested page: "Container orchestration".
- Kubernetes Ingress and Horizontal Pod Autoscaler (autoscaling): not in the Kubernetes dossier. Suggested: Kubernetes docs pages.
- Infrastructure as code / immutable infrastructure: not in the dossier. Suggested pages: "Infrastructure as code".
- Service mesh and sidecar (appears only in Microservices): suggested page "Service mesh".
- Skipped on purpose: Kubernetes API security (TLS, authentication, authorization modes), namespaces, add-ons, Cluster API, distributions, release timeline; Docker history/adoption timeline and licensing (company/business history); VM nested virtualization and history sections; the OS-level virtualization implementation tables.
- the-12-factor-app guide and top-5-deployment-strategies guide are short lists; drafted as one entry each (Twelve-factor app; folded into Deployment strategies).

# Gaps: containers-orchestration-and-deployment gap-fill (chunks 04-07)

- Kubernetes Ingress and Gateway API: only three sentences inside the Service doc; no page. Suggested: doc>kubernetes.io/docs/concepts/services-networking/ingress.
- Kubernetes kube-proxy and virtual IPs (how Service traffic is routed): not in these chunks. Suggested: doc>kubernetes.io/docs/reference/networking/virtual-ips.
- Kubernetes DNS for Services and Pods (CoreDNS records): 20 more sentences cut in the Service doc, not drafted. Suggested: doc>kubernetes.io/docs/concepts/services-networking/dns-pod-service.
- Immutable infrastructure and Continuous integration: no own page crawled. Suggested: "Continuous integration", "Immutable infrastructure".
- A/B testing: named by Feature toggle, Canary release and Deployment strategies with no page. Suggested: "A/B testing".
- Stateless and stateful services: no chunk here teaches it (StatefulSets still resolve to nothing). Suggested: "Stateless protocol" or a Kubernetes StatefulSet doc page.
- Skipped on purpose: hypervisor and cgroup history, chroot history and graphical-application notes, namespace proposals (syslog, IMA), cgroup v1 redesign details, IaC tool-community discussion, CD adoption strategies table, Kubernetes overview version and release notes.

# Gaps: containers-orchestration-and-deployment (chunks 08-09, gap-fill)

- Container probes (thin): liveness, readiness and startup probe semantics and restart behavior are not explained. Suggested: doc>kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle and doc>kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes.
- Ingress controller catalogue and the Gateway API (the successor to Ingress): not crawled. Suggested: doc>kubernetes.io/docs/concepts/services-networking/ingress-controllers, doc>kubernetes.io/docs/concepts/services-networking/gateway.
- Pod disruption budgets and the Pod lifecycle (phases, restart policy, termination): only named on the Pods page. Suggested: doc>kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle, doc>kubernetes.io/docs/concepts/workloads/pods/disruptions.
- Vertical Pod autoscaling and node autoscaling: named under "What's next" of the HPA page only. Suggested: doc>kubernetes.io/docs/concepts/workloads/autoscaling.
- Service mesh: sidecar sentences name it only in passing. Suggested page: "Service mesh".
- Canary release as its own concept: the SRE book gives a few sentences (canary label, canary deployment after system tests); folded into Release pipeline and Risk-based rollouts, not drafted as an entry.
- Skipped on purpose: Pod OS, scheduling groups, Pod generation and observedGeneration, Pod subresources, IngressClass deprecated annotation, HPA maintenance-mode and migration steps, Rapid/Blaze/MPM/Sisyphus internals beyond the general practice, feature-gate version history.

# Gaps: containers-orchestration-and-deployment (chunk 10, gap-fill gf27)

- Graceful pod termination (thin): the full termination flow (default grace period, custom stop signals, forced deletion, sidecar shutdown order, garbage collection of terminated Pods) is on a separate page. Suggested: doc>kubernetes.io/docs/concepts/workloads/pods/pod-termination.
- Probe configuration fields (periodSeconds, timeoutSeconds, successThreshold, failureThreshold defaults): the crawled task page only shows periodSeconds, initialDelaySeconds and failureThreshold in examples. Suggested: doc>kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes.
- Pod disruption budgets and eviction (voluntary versus involuntary disruptions): named on the lifecycle and resize sections only. Suggested: doc>kubernetes.io/docs/concepts/workloads/pods/disruptions.
- Container lifecycle hooks (postStart, preStop): named, not explained. Suggested: doc>kubernetes.io/docs/concepts/containers/container-lifecycle-hooks.
- Skipped on purpose: kubelet-restart detection feature gate, h2c and gRPC TLS probe feature-gate details, Pod readiness to start containers, tutorial steps and example manifests; the restart-behavior comparison table (garbled in the extracted text).
