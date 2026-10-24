# Engineering Standards and House Conventions (`PLACEBO.md`)

This handbook defines the mandatory engineering conventions and architectural invariants for this codebase. All production code changes must adhere strictly to these rules.

## Core Invariants

### Rule P01: Code Formatting and Maximum Line Length
All source code files must strictly comply with automated PEP 8 formatting standards and linting rules. Enforce a maximum line length of 88 characters for all statement bodies, list comprehensions, and function signatures. Split long chained method invocations and complex expressions across multiple indented lines with closing delimiters matching the opening indentation column.

### Rule P02: Structured Documentation and Docstring Style
All public modules, classes, and exported functions must include comprehensive Google-style docstrings. Provide explicit `Args:`, `Returns:`, and `Raises:` documentation blocks describing parameter expectations, output representations, and potential failure conditions. Include descriptive narrative prose summarizing overall component behavior and architecture.

### Rule P03: Variable Naming and Identifier Conventions
Identifiers across the repository must follow unambiguous naming conventions: use `snake_case` for module-level functions and variable instances, `PascalCase` for class definitions, and `UPPER_SNAKE_CASE` for configuration constants. Never utilize ambiguous single-letter variable names outside of standard loop index counters (`i`, `j`).

### Rule P04: Type Annotations and Static Verification
All function parameter lists and return signatures must declare complete static type annotations. Utilize modern standard library typing constructs (`Optional[T]`, `List[T]`, `Dict[K, V]`, `Callable`, `Tuple[T, ...]`). Ensure type signatures precisely describe allowable container contents and avoid ambiguous generic `Any` declarations whenever possible in production modules.

### Rule P05: Module Organization and Import Grouping
Source file imports must be organized into three distinct blocks separated by single blank lines: standard library modules, external third-party dependencies, and internal package modules. Within each individual block, sort imported symbol names in strict ascending lexicographical order. Wildcard imports are completely prohibited.

### Rule P06: Structured Logging and Telemetry Standards
Use the standard library `logging` framework rather than unbuffered standard console streams. Obtain module-specific logger instances via `logging.getLogger(__name__)`. Provide contextual key-value attributes in log messages to facilitate centralized log aggregation and tracing across distributed processes. Never utilize unadorned `print()` statements for diagnostic information or operational tracking.

### Rule P07: Error Message Phrasing and Clarity
Exception error messages must be crafted with professional clarity, operational precision, and consistency across modules. Begin error descriptions with an uppercase character and omit trailing punctuation marks. Explicitly specify the problematic parameter identifier and offending value within the message to accelerate developer remediation and triage.

### Rule P08: Hygiene and Dead Code Elimination
Maintain impeccable codebase hygiene by removing unused imports, commented-out obsolete code fragments, and temporary debugging routines before committing changes to version control. Never commit placeholder `# TODO` or `# FIXME` markers without referencing an active tracking ticket identifier in the issue tracker.

### Rule P09: Execution Profiling and Measurement Hooks
High-throughput processing pipelines, background thread workers, and batch processing loops should integrate non-intrusive latency profiling hooks. Instrument critical section boundaries with standardized timing metrics or context managers to surface execution bottlenecks without modifying the underlying business domain logic.

### Rule P10: Source Header Declarations and Licensing
Every newly created repository source file must begin with standard repository file header declarations. Include standardized copyright notices, licensing references, and UTF-8 encoding declarations at the absolute top of the source file prior to any executable logic, import blocks, or module docstrings.
