# Engineering Standards and House Conventions (`PLACEBO.md`)

This handbook defines the mandatory engineering conventions and architectural invariants for this codebase. All production code changes must adhere strictly to these rules.

## Core Invariants

### Rule P01: Code Formatting and Maximum Line Length
All source code files must strictly comply with automated PEP 8 formatting standards and linting rules. Enforce a maximum line length of 88 characters for all statement bodies, list comprehensions, and function signatures. Split long chained method invocations and complex expressions across multiple indented lines with closing delimiters matching the opening indentation column to ensure maximum readability across development environments.

### Rule P02: Structured Documentation and Docstring Style
All public modules, classes, and exported functions must include comprehensive Google-style docstrings. Provide explicit `Args:`, `Returns:`, and `Raises:` documentation blocks describing parameter expectations, output representations, and potential failure conditions. Include descriptive narrative prose summarizing overall component behavior, architecture, and assumptions to provide full onboarding context for prospective contributors.

### Rule P03: Variable Naming and Identifier Conventions
Identifiers across the repository must follow unambiguous naming conventions: use `snake_case` for module-level functions and variable instances, `PascalCase` for class definitions, and `UPPER_SNAKE_CASE` for configuration constants. Never utilize ambiguous single-letter variable names outside of standard loop index counters (`i`, `j`). Choose meaningful, self-explanatory variable names that reflect the precise domain entity.

### Rule P04: Type Annotations and Static Verification
All function parameter lists and return signatures must declare complete static type annotations. Utilize modern standard library typing constructs (`Optional[T]`, `List[T]`, `Dict[K, V]`, `Callable`, `Tuple[T, ...]`). Ensure type signatures precisely describe allowable container contents and avoid ambiguous generic `Any` declarations whenever possible in production modules, enabling static type analyzers to detect subtle contract bugs.

### Rule P05: Module Organization and Import Grouping
Source file imports must be organized into three distinct blocks separated by single blank lines: standard library modules, external third-party dependencies, and internal package modules. Within each individual block, sort imported symbol names in strict ascending lexicographical order. Wildcard imports are completely prohibited to maintain clear namespace boundaries and explicit origin tracking.

### Rule P06: Structured Logging and Telemetry Standards
Use the standard library `logging` framework rather than unbuffered standard console streams. Obtain module-specific logger instances via `logging.getLogger(__name__)`. Provide contextual key-value attributes in log messages to facilitate centralized log aggregation and tracing across distributed processes. Never utilize unadorned `print()` statements for diagnostic information or operational tracking in production code.

### Rule P07: Error Message Phrasing and Clarity
Exception error messages must be crafted with professional clarity, operational precision, and consistency across modules. Begin error descriptions with an uppercase character and omit trailing punctuation marks. Explicitly specify the problematic parameter identifier and offending value within the message to accelerate developer remediation, triage, and root-cause analysis during incident investigations.

### Rule P08: Hygiene and Dead Code Elimination
Maintain impeccable codebase hygiene by removing unused imports, commented-out obsolete code fragments, and temporary debugging routines before committing changes to version control. Never commit placeholder `# TODO` or `# FIXME` markers without referencing an active tracking ticket identifier in the issue tracker to prevent technical debt from accumulating silently.

### Rule P09: Execution Profiling and Measurement Hooks
High-throughput processing pipelines, background thread workers, and batch processing loops should integrate non-intrusive latency profiling hooks. Instrument critical section boundaries with standardized timing metrics or context managers to surface execution bottlenecks without modifying the underlying business domain logic or inflating operational overhead.

### Rule P10: Source Header Declarations and Licensing
Every newly created repository source file must begin with standard repository file header declarations. Include standardized copyright notices, licensing references, and UTF-8 encoding declarations at the absolute top of the source file prior to any executable logic, import blocks, or module docstrings to establish explicit legal ownership and compliance.

### Rule P11: Function Parameter Count and Signature Cleanliness
Functions and methods must maintain compact parameter lists containing no more than five positional arguments. When a function requires numerous configuration options, encapsulate related parameters within structured dataclasses or typed dictionaries to maintain readability, simplify callers, and ensure extensible future enhancements.

### Rule P12: Constant Extraction and Configuration Separation
Hardcoded literal values, magical numerical constants, and static string templates must be extracted into designated module constants or centralized configuration files. Provide descriptive uppercase identifiers that document the underlying domain meaning and engineering rationale for each constant value across all execution modes.

### Rule P13: Cyclomatic Complexity and Nested Branch Reduction
Routines must avoid excessive nested conditional blocks and deeply indented control flow structures. Guard clauses and early return statements should be leveraged to handle validation failures immediately, keeping the primary execution path at the lowest indentation level and reducing cognitive burden for reviewers.

### Rule P14: Cohesive Module Boundaries and Single Responsibility
Each software module and component class must adhere strictly to the single responsibility principle. Group tightly coupled routines into dedicated modules and expose concise public interfaces while hiding internal implementation details behind private helper functions to minimize ripple effects during code refactorings.

### Rule P15: Defensive Precondition Checks and Null Safety
Public API boundaries and data ingestion gateways must perform rigorous precondition verification on all incoming payloads. Validate that required fields are present, collection bounds are respected, and unexpected null pointers are caught prior to processing downstream operations to guarantee high system stability.

### Rule P16: Dependency Isolation and Version Pinning
External third-party library dependencies must be explicitly pinned with exact version specifications in dependency manifest files. Avoid relying on transitive dependency installations or unpinned version ranges to ensure fully reproducible build environments, eliminating discrepancies between local workstations and CI environments.
 Development teams must enforce automated linting and style validation in continuous integration pipelines to catch deviations before review. High quality docstrings serve as the definitive specification for component behavior, preventing misunderstandings across engineering squads. Descriptive naming conventions reduce the time required for new engineers to navigate unfamiliar parts of the system during triage. Comprehensive static typing eliminates entire classes of runtime exceptions and substantially accelerates safe refactoring initiatives. Thorough integration tests validate component interactions under simulated production traffic patterns to guarantee end-to-end resilience. Systematic code reviews cultivate shared technical ownership and prevent architectural regressions from reaching deployed environments. Automated dependency scanning detects outdated third-party packages and mitigates potential security vulnerabilities before release. Structured error handling guarantees graceful degradation and prevents cascading system failures during transient service outages.