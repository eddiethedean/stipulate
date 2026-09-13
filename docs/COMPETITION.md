# Competition and Positioning

## Scope

This is a positioning document, not a verified exhaustive feature ranking. Stipulate's initial implementation is in progress and its release gates remain authoritative. Planned or unsupported capabilities must not be compared as shipped advantages against other projects.

Its intended focus is explicit Python structural contracts: check a dynamically supplied implementation, explain incompatible and unknown evidence, and eventually compare contract evolution with the same underlying rules.

## Language foundation

Protocol is the foundation. Python's typing tools already provide structural checking where the relationship is statically visible; runtime-checkable Protocol checks are intentionally shallower. Stipulate's proposed addition is deeper declaration inspection at dynamic boundaries, subject to available metadata. [Python typing documentation](https://docs.python.org/3/library/typing.html#typing.runtime_checkable)

Do not claim runtime inspection proves method behavior that static checking could not prove.

## Useful adjacent references

| Reference | Documented focus | Stipulate design lesson |
| --- | --- | --- |
| Pydantic | Typed value validation and associated tooling | Simple entry points, useful diagnostics, deliberate value semantics |
| Griffe | Package API extraction, serialization, and breaking-change analysis | Treat public schema and change reports as compatibility surfaces |
| Typeguard | Runtime checking of annotated values and instrumented calls | Study runtime annotation limits without conflating value checks with declaration relations |

Sources: [Pydantic](https://pydantic.dev/docs/validation/latest/concepts/types/), [Griffe](https://mkdocstrings.github.io/griffe/), [Typeguard](https://typeguard.readthedocs.io/en/latest/). This table does not assert that adjacent tools lack all forms of Protocol support or that Stipulate has uniquely solved those problems.

Other historical interface systems, behavioral contract libraries, schema-diff tools, and API-impact projects can inform later evaluation. Specific competitive rankings require dated primary sources, concrete examples, and reproducible comparison criteria before inclusion.

## Product distinction to prove

The intended combination is:

- Standard Protocol declarations with ordinary implementations.
- Precise, method-based Contract API and inferred validation return types.
- Directional call/member/type checking for an explicitly supported subset.
- Unknown evidence preserved separately from mismatch and policy acceptance.
- Eventual universal implementer/consumer evolution analysis using shared rules.
- Eventual versioned schemas and portable fingerprints.

The first four belong to the 0.1 plan. The last two are later release gates, not current feature claims.

## Boundaries

Do not expand into package-wide source extraction, general function instrumentation, call-site analytics, dependency injection, behavioral preconditions, or a nominal interface ecosystem merely to match a competitor's feature list.

For tooling, a deliberate user-supplied Protocol is the contract being checked. This scope does not prevent future integrations with API extraction, but those integrations must not redefine the core.

## Reassessment triggers

Before publishing competitive claims or major releases, verify current primary documentation and test representative examples. Reevaluate when typing standards improve class-side APIs, checker TypeForm support changes, or adjacent projects add relevant declaration/evolution capabilities.

Stipulate earns adoption through demonstrated correctness and error quality. Avoid claims of completeness, unique capability, or stronger guarantees than the evidence supports.
