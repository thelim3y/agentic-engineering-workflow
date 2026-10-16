# Component maps

Status: required design; authoring, storage, freshness checks and delivery to
agents are not implemented.

## Purpose

A component map gives a human and an agent a high-level view of a codebase before
they inspect its details. It shows the logical components, how they communicate,
and where to find the authoritative source, tests and documentation for each one.

It is a navigation aid, not a second source of truth. Agents must inspect current
source, tests and repository state before relying on a map entry to make a change.

## Ownership

The developer or another designated human creates the initial map and owns its
publication. The map will normally be maintained primarily by humans because it
records intended responsibilities and boundaries, not merely discovered file
relationships.

Agents may report a discrepancy or propose an update with source references. They
must not silently publish a changed map or treat an unverified generated diagram as
current architecture.

## Shape

The map has two inseparable parts:

1. A small diagram of logical components and their primary relationships.
2. A source-linked component register that gives each diagram node a one- or
   two-sentence explanation and routes readers to more detail.

Use logical components, not a box for every directory, class or service. A
component can span several source locations when it owns one coherent
responsibility.

### Diagram

The diagram answers: what exists, which components communicate, and what kind of
relationship connects them. Label arrows where needed as a call, data flow, event,
ownership boundary or external action. Keep the overview small; use focused
diagrams for a subsystem or a sequence when the overview would become crowded.

The diagram must distinguish trusted control, restricted execution and external
systems where those boundaries matter. It does not imply that every box is a
separate process, service or agent invocation.

### Component register

Every diagram component has an entry containing:

- **Purpose:** one or two sentences describing why the component exists.
- **Owns:** its responsibilities, data or decisions.
- **Does not own:** adjacent responsibilities it must not absorb, when useful to
  prevent boundary drift.
- **Relationships:** important components it calls, serves, publishes to or reads
  from.
- **Learn more:** links to primary source locations, public interfaces, tests,
  design documents, ADRs and relevant evidence.

An entry is concise enough to orient a reader; the linked source is where detailed
facts belong.

## Use during a task

A task supplies the developer's direction. The component map helps an agent choose
where to begin its inspection and which boundaries may matter. It does not replace
the task, authorize a change, select mandatory policy, or establish that a current
file still matches the map.

Agents use permitted tools to inspect the linked sources, current revision, tests
and applicable documents. If the map is stale, missing or inconsistent with the
repository, they report that fact and use current authoritative evidence for the
task.

## Maintenance

Update the map when a deliberate architectural change affects a component's
responsibility, relationship, boundary or source route. Do not update it for a
purely local implementation change that leaves the component model intact.

The map records intended structure, so source scanning can assist with discovery
but cannot by itself decide the correct description. A human reviews proposed
structural updates before publication. Preserve the map revision and the linked
source revision or freshness information when it is supplied to an agent.

## Non-goals

- A complete catalog of files, classes or functions.
- Automatic architecture truth inferred solely from source code.
- A replacement for source inspection, tests, version control or task direction.
- A way for retrieved documentation to override permissions, protected-test
  boundaries or workflow policy.
