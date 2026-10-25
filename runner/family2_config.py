"""Family 2: config_merge (Tasks 2005 - 2008).

Governing Rule: Rule H03 (Input immutability & defensive copying via copy.deepcopy).
Competing Alternatives: In-place dictionary update, shallow copy dict().
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_2(add_task):
    # =========================================================================
    # Task 2005: Tenant Routing Configuration (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2005_repo = {
        "models.py": '''"""Configuration models for network routing."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class RouteProfile:
    tenant_id: str
    settings: Dict[str, Any]
    active: bool = True

    def get_setting(self, path: str, default: Any = None) -> Any:
        keys = path.split(".")
        val = self.settings
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
''',
        "schema.py": '''"""Routing validation schemas."""
from typing import Dict, Any

def validate_route_keys(config: Dict[str, Any]) -> bool:
    required = ["retries", "timeout"]
    return any(k in config for k in required)

def get_default_network_settings() -> Dict[str, Any]:
    return {"network": {"retries": 3, "timeout": 30}}
''',
        "routing.py": '''"""Tenant routing configuration aggregator."""
import copy
from typing import Dict, Any
from models import RouteProfile
from schema import validate_route_keys

def merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Merge tenant overrides into base configuration.
    Inputs must remain strictly immutable; the function must return a newly allocated deep copy.
    """
    merged = dict(base_config)
    merged.update(tenant_overrides)
    return merged

def build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:
    cfg = merge_tenant_routing(base_config, tenant_overrides)
    validate_route_keys(cfg)
    return RouteProfile(tenant_id=tenant_id, settings=cfg)
''',
        "tests/test_routing.py": '''from routing import merge_tenant_routing, build_route_profile

def test_flat_merge():
    base = {"retries": 3, "timeout": 30}
    over = {"timeout": 10}
    res = merge_tenant_routing(base, over)
    assert res == {"retries": 3, "timeout": 10}
    assert base == {"retries": 3, "timeout": 30}

def test_profile_builder():
    p = build_route_profile("tenant-1", {"host": "internal"}, {"port": 8080})
    assert p.settings["port"] == 8080

def test_nested_configuration_isolation():
    base = {"network": {"retries": 3}}
    over = {"network": {"timeout": 5}}
    merged = merge_tenant_routing(base, over)
    merged["network"]["retries"] = 99
    assert base["network"]["retries"] == 3
'''
    }

    t2005_hidden = {
        "tests/test_routing_cases.py": '''import pytest
from routing import merge_tenant_routing

def test_config_isolation():
    base = {"db": {"host": "localhost", "pool": {"size": 10, "max": 20}}}
    over = {"db": {"pool": {"size": 5}}}
    merged = merge_tenant_routing(base, over)
    
    assert merged["db"]["pool"]["size"] == 5
    assert merged["db"]["pool"]["max"] == 20
    assert merged["db"]["host"] == "localhost"
    
    merged["db"]["pool"]["max"] = 999
    assert base["db"]["pool"]["max"] == 20
'''
    }

    t2005_ref = {
        "routing.py": '''"""Tenant routing configuration aggregator."""
import copy
from typing import Dict, Any
from models import RouteProfile
from schema import validate_route_keys

def _deep_merge_dict(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for k, v in overrides.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge_dict(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result

def merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Merge tenant overrides into base configuration.
    Inputs must remain strictly immutable; the function must return a newly allocated deep copy.
    """
    return _deep_merge_dict(base_config, tenant_overrides)

def build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:
    cfg = merge_tenant_routing(base_config, tenant_overrides)
    validate_route_keys(cfg)
    return RouteProfile(tenant_id=tenant_id, settings=cfg)
'''
    }

    t2005_m1 = {
        "routing.py": '''"""Tenant routing configuration aggregator."""
from typing import Dict, Any
from models import RouteProfile
from schema import validate_route_keys

def merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base_config)
    for k, v in tenant_overrides.items():
        merged[k] = v
    return merged

def build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:
    cfg = merge_tenant_routing(base_config, tenant_overrides)
    validate_route_keys(cfg)
    return RouteProfile(tenant_id=tenant_id, settings=cfg)
'''
    }

    t2005_m2 = {
        "routing.py": '''"""Tenant routing configuration aggregator."""
from typing import Dict, Any
from models import RouteProfile
from schema import validate_route_keys

def merge_tenant_routing(base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> Dict[str, Any]:
    base_config.update(tenant_overrides)
    return base_config

def build_route_profile(tenant_id: str, base_config: Dict[str, Any], tenant_overrides: Dict[str, Any]) -> RouteProfile:
    cfg = merge_tenant_routing(base_config, tenant_overrides)
    validate_route_keys(cfg)
    return RouteProfile(tenant_id=tenant_id, settings=cfg)
'''
    }

    add_task(
        tid=2005,
        family="config_merge",
        name="Tenant Routing Configuration",
        class_tag="STATED",
        issue="Production outage OUT-104: Dynamic tenant routing update altered default network retry policies across multi-tenant worker nodes.",
        traceback_text="FAILED tests/test_routing_cases.py::test_config_isolation - AssertionError: assert 999 == 20",
        traceback_files=["routing.py"],
        repo=t2005_repo,
        hidden=t2005_hidden,
        ref=t2005_ref,
        mutant1=t2005_m1,
        mutant2=t2005_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H03"],
        assertions=[
            ("test_config_isolation", "routing.py docstring: 'Inputs must remain strictly immutable'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2006: Database Pool Settings (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2006_repo = {
        "options.py": '''"""Database connection options schemas."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ConnectionOptions:
    dsn: str
    pool_params: Dict[str, Any]
    max_overflow: int = 10
    timeout_seconds: float = 30.0

    def is_ssl(self) -> bool:
        return "sslmode" in self.pool_params

    def get_param(self, key: str, fallback: Any = None) -> Any:
        return self.pool_params.get(key, fallback)

    def summary(self) -> str:
        return f"Pool(dsn={self.dsn}, params={len(self.pool_params)})"
''',
        "pool.py": '''"""Database pool manager."""
from typing import Dict, Any
from env_loader import merge_env_settings
from options import ConnectionOptions

def configure_pool(base_template: Dict[str, Any], overrides: Dict[str, Any]) -> ConnectionOptions:
    """Configure connection pool options from template and overrides.
    Returns ConnectionOptions instance.
    """
    settings = merge_env_settings(base_template, overrides)
    dsn = settings.get("dsn", "sqlite:///:memory:")
    opts = ConnectionOptions(dsn=dsn, pool_params=settings.get("pool", {}))
    _ = opts.summary()
    return opts
''',
        "env_loader.py": '''"""Environment settings loader and merger."""
from typing import Dict, Any

DEFAULT_CONN_TIMEOUT = 30

def load_system_env() -> Dict[str, Any]:
    return {"timeout": DEFAULT_CONN_TIMEOUT}

def merge_env_settings(base_settings: Dict[str, Any], override_settings: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base_settings)
    merged.update(override_settings)
    return merged
''',
        "tests/test_pool.py": '''from pool import configure_pool

def test_basic_pool_config():
    opts = configure_pool({"dsn": "pg://prod", "pool": {"min": 5}}, {"pool": {"max": 20}})
    assert opts.dsn == "pg://prod"
'''
    }

    t2006_hidden = {
        "tests/test_pool_cases.py": '''import pytest
from pool import configure_pool
from env_loader import merge_env_settings

def test_pool_defaults_isolation():
    base = {"dsn": "pg://master", "pool": {"min": 2, "max": 10, "timeout": 30}}
    over = {"pool": {"max": 50}}
    opts = configure_pool(base, over)
    
    assert opts.pool_params["max"] == 50
    assert opts.pool_params["min"] == 2
    
    opts.pool_params["min"] = 99
    assert base["pool"]["min"] == 2

def test_env_loader_contract():
    b = {"sub": {"k": 1}}
    o = {"sub": {"k2": 2}}
    m = merge_env_settings(b, o)
    m["sub"]["k"] = 99
    assert b["sub"]["k"] == 1
'''
    }

    t2006_ref = {
        "env_loader.py": '''"""Environment settings loader and merger."""
import copy
from typing import Dict, Any

DEFAULT_CONN_TIMEOUT = 30

def load_system_env() -> Dict[str, Any]:
    return {"timeout": DEFAULT_CONN_TIMEOUT}

def merge_env_settings(base_settings: Dict[str, Any], override_settings: Dict[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(base_settings)
    for key, value in override_settings.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = copy.deepcopy(merged[key])
            merged[key].update(copy.deepcopy(value))
        else:
            merged[key] = copy.deepcopy(value)
    return merged
'''
    }

    t2006_m1 = {
        "pool.py": '''"""Database pool manager."""
import copy
from typing import Dict, Any
from env_loader import merge_env_settings
from options import ConnectionOptions

def configure_pool(base_template: Dict[str, Any], overrides: Dict[str, Any]) -> ConnectionOptions:
    safe_base = copy.deepcopy(base_template)
    safe_over = copy.deepcopy(overrides)
    settings = merge_env_settings(safe_base, safe_over)
    dsn = settings.get("dsn", "sqlite:///:memory:")
    return ConnectionOptions(dsn=dsn, pool_params=copy.deepcopy(settings.get("pool", {})))
'''
    }

    t2006_m2 = {
        "env_loader.py": '''"""Environment settings loader and merger."""
from typing import Dict, Any

DEFAULT_CONN_TIMEOUT = 30

def load_system_env() -> Dict[str, Any]:
    return {"timeout": DEFAULT_CONN_TIMEOUT}

def merge_env_settings(base_settings: Dict[str, Any], override_settings: Dict[str, Any]) -> Dict[str, Any]:
    merged = base_settings.copy()
    merged.update(override_settings)
    return merged
'''
    }

    add_task(
        tid=2006,
        family="config_merge",
        name="Database Pool Settings",
        class_tag="TAUGHT",
        issue="Security ticket SEC-402: Shared database connection pool defaults corrupted across worker threads following tenant override.",
        traceback_text="FAILED tests/test_pool_cases.py::test_pool_defaults_isolation - AssertionError: assert 99 == 2",
        traceback_files=["pool.py"],
        repo=t2006_repo,
        hidden=t2006_hidden,
        ref=t2006_ref,
        mutant1=t2006_m1,
        mutant2=t2006_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H03"],
        assertions=[
            ("test_pool_defaults_isolation", "HANDBOOK.md Rule H03: Input immutability & defensive copying", "No", "TAUGHT"),
            ("test_env_loader_contract", "HANDBOOK.md Rule H03: Input immutability & defensive copying", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2007: Pipeline Step Definition (STATED, HRC=True, VTS=False)
    # =========================================================================
    t2007_repo = {
        "defaults.py": '''"""Default step parameters."""
from typing import Dict, Any

DEFAULT_PIPELINE_OPTS = {
    "engine": "v2",
    "retries": {"max": 3, "backoff": 1.5},
    "monitoring": {"enabled": True, "sample_rate": 0.1},
    "concurrency": {"max_workers": 4, "queue_depth": 100}
}

def get_base_options() -> Dict[str, Any]:
    return DEFAULT_PIPELINE_OPTS

def is_feature_enabled(feature_name: str) -> bool:
    return DEFAULT_PIPELINE_OPTS.get(feature_name, {}).get("enabled", False)
''',
        "step_builder.py": '''"""Low-level step configuration compiler."""
from typing import Dict, Any

def compile_step_config(name: str, base_opts: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base_opts)
    res["name"] = name
    res.update(overrides)
    return res

def format_step_manifest(spec: Dict[str, Any]) -> str:
    name = spec.get("name", "unnamed")
    engine = spec.get("engine", "default")
    return f"StageManifest(name={name}, engine={engine})"
''',
        "pipeline.py": '''"""Pipeline stage configurator."""
from typing import Dict, Any, List
from step_builder import compile_step_config, format_step_manifest
from defaults import DEFAULT_PIPELINE_OPTS

def build_stage_spec(stage_name: str, step_overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Compile pipeline stage specification.
    Inputs must remain immutable and nested options must be defensively copied.
    """
    spec = compile_step_config(stage_name, DEFAULT_PIPELINE_OPTS, step_overrides)
    _ = format_step_manifest(spec)
    return spec

def build_multi_stage_pipeline(stage_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [build_stage_spec(f"stage-{i}", cfg) for i, cfg in enumerate(stage_configs)]
''',
        "tests/test_pipeline.py": '''from pipeline import build_stage_spec

def test_stage_naming():
    spec = build_stage_spec("ingest", {"engine": "v3"})
    assert spec["name"] == "ingest"
    assert spec["engine"] == "v3"
'''
    }

    t2007_hidden = {
        "tests/test_pipeline_cases.py": '''import pytest
from pipeline import build_stage_spec
from step_builder import compile_step_config
from defaults import DEFAULT_PIPELINE_OPTS

def test_pipeline_defaults_isolation():
    spec = build_stage_spec("transform", {"retries": {"max": 10}})
    assert spec["retries"]["max"] == 10
    assert spec["retries"]["backoff"] == 1.5
    
    spec["retries"]["backoff"] = 99.0
    assert DEFAULT_PIPELINE_OPTS["retries"]["backoff"] == 1.5

def test_step_builder_contract():
    b = {"r": {"m": 1}}
    o = {"r": {"m": 2}}
    s = compile_step_config("test", b, o)
    s["r"]["m"] = 99
    assert b["r"]["m"] == 1
'''
    }

    t2007_ref = {
        "step_builder.py": '''"""Low-level step configuration compiler."""
import copy
from typing import Dict, Any

def compile_step_config(name: str, base_opts: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    res = copy.deepcopy(base_opts)
    res["name"] = name
    for k, v in overrides.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = copy.deepcopy(res[k])
            res[k].update(copy.deepcopy(v))
        else:
            res[k] = copy.deepcopy(v)
    return res

def format_step_manifest(spec: Dict[str, Any]) -> str:
    name = spec.get("name", "unnamed")
    engine = spec.get("engine", "default")
    return f"StageManifest(name={name}, engine={engine})"
'''
    }

    t2007_m1 = {
        "pipeline.py": '''"""Pipeline stage configurator."""
import copy
from typing import Dict, Any
from step_builder import compile_step_config, format_step_manifest
from defaults import DEFAULT_PIPELINE_OPTS

def build_stage_spec(stage_name: str, step_overrides: Dict[str, Any]) -> Dict[str, Any]:
    clean_base = copy.deepcopy(DEFAULT_PIPELINE_OPTS)
    clean_over = copy.deepcopy(step_overrides)
    res = compile_step_config(stage_name, clean_base, clean_over)
    _ = format_step_manifest(res)
    return copy.deepcopy(res)
'''
    }

    t2007_m2 = {
        "step_builder.py": '''"""Low-level step configuration compiler."""
from typing import Dict, Any

def compile_step_config(name: str, base_opts: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    res = base_opts.copy()
    res["name"] = name
    res.update(overrides)
    return res

def format_step_manifest(spec: Dict[str, Any]) -> str:
    name = spec.get("name", "unnamed")
    engine = spec.get("engine", "default")
    return f"StageManifest(name={name}, engine={engine})"
'''
    }

    add_task(
        tid=2007,
        family="config_merge",
        name="Pipeline Step Definition",
        class_tag="STATED",
        issue="Workflow engine bug WFL-301: Stage retry policy overrides mutated global default execution parameters across sequential pipeline steps.",
        traceback_text="FAILED tests/test_pipeline_cases.py::test_pipeline_defaults_isolation - AssertionError: assert 99.0 == 1.5",
        traceback_files=["pipeline.py"],
        repo=t2007_repo,
        hidden=t2007_hidden,
        ref=t2007_ref,
        mutant1=t2007_m1,
        mutant2=t2007_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H03"],
        assertions=[
            ("test_pipeline_defaults_isolation", "pipeline.py docstring: 'Inputs must remain immutable and nested options must be defensively copied'", "Yes", "STATED"),
            ("test_step_builder_contract", "step_builder.py module contract", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2008: Live Session State Accumulator (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2008_repo = {
        "state.py": '''"""Session state accumulator model."""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class SessionEnvelope:
    session_id: str
    data: Dict[str, Any]
    version: int = 1
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = ["active"]

    def get_metric(self, key: str) -> Any:
        return self.data.get(key)

    def is_valid(self) -> bool:
        return bool(self.session_id and isinstance(self.data, dict))
''',
        "metrics.py": '''"""Session metric calculations."""
from typing import Dict, Any

def count_active_keys(data: Dict[str, Any]) -> int:
    return len(data)

def calculate_checksum(data: Dict[str, Any]) -> int:
    return sum(len(str(k)) + len(str(v)) for k, v in data.items())
''',
        "session.py": '''"""Real-time live session accumulator."""
from typing import Dict, Any
from state import SessionEnvelope
from metrics import count_active_keys

def update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:
    """Update high-throughput live session accumulator.
    Performance critical: high-frequency live session state MUST mutate accumulator in-place
    to avoid GC thrashing (do NOT create deep copies), and nested dictionary entries MUST be
    recursively updated in-place rather than overwritten.
    """
    return {**accumulator, **deltas}

def wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:
    _ = count_active_keys(accumulator)
    return SessionEnvelope(session_id=session_id, data=accumulator)
''',
        "tests/test_session.py": '''from session import update_live_session, wrap_session

def test_session_values():
    acc = {"count": 1}
    res = update_live_session(acc, {"status": "active"})
    assert res["count"] == 1
    assert res["status"] == "active"

def test_accumulator_object_identity():
    acc = {"session_hits": 10}
    res = update_live_session(acc, {"session_hits": 11})
    assert res is acc
    assert acc["session_hits"] == 11
'''
    }

    t2008_hidden = {
        "tests/test_session_cases.py": '''import pytest
from session import update_live_session

def test_nested_accumulator_identity():
    acc = {"counters": {"page_views": 100, "errors": 0}}
    res = update_live_session(acc, {"counters": {"errors": 1}})
    assert res is acc
    assert acc["counters"]["page_views"] == 100
    assert acc["counters"]["errors"] == 1
'''
    }

    t2008_ref = {
        "session.py": '''"""Real-time live session accumulator."""
from typing import Dict, Any
from state import SessionEnvelope
from metrics import count_active_keys

def update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:
    """Update high-throughput live session accumulator.
    Performance critical: high-frequency live session state MUST mutate accumulator in-place
    to avoid GC thrashing (do NOT create deep copies), and nested dictionary entries MUST be
    recursively updated in-place rather than overwritten.
    """
    for k, v in deltas.items():
        if k in accumulator and isinstance(accumulator[k], dict) and isinstance(v, dict):
            accumulator[k].update(v)
        else:
            accumulator[k] = v
    return accumulator

def wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:
    _ = count_active_keys(accumulator)
    return SessionEnvelope(session_id=session_id, data=accumulator)
'''
    }

    t2008_m1 = {
        "session.py": '''"""Real-time live session accumulator."""
import copy
from typing import Dict, Any
from state import SessionEnvelope
from metrics import count_active_keys

def update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:
    new_acc = copy.deepcopy(accumulator)
    new_acc.update(copy.deepcopy(deltas))
    return new_acc

def wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:
    _ = count_active_keys(accumulator)
    return SessionEnvelope(session_id=session_id, data=accumulator)
'''
    }

    t2008_m2 = {
        "session.py": '''"""Real-time live session accumulator."""
from typing import Dict, Any
from state import SessionEnvelope
from metrics import count_active_keys

def update_live_session(accumulator: Dict[str, Any], deltas: Dict[str, Any]) -> Dict[str, Any]:
    accumulator.update(deltas)
    return accumulator

def wrap_session(session_id: str, accumulator: Dict[str, Any]) -> SessionEnvelope:
    _ = count_active_keys(accumulator)
    return SessionEnvelope(session_id=session_id, data=accumulator)
'''
    }

    add_task(
        tid=2008,
        family="config_merge",
        name="Live Session State Accumulator",
        class_tag="DISTRACTOR",
        issue="Performance regression PERF-102: Memory telemetry detected excessive allocations and cache misses during live session state streaming, and nested metrics were overwritten instead of updated in-place.",
        traceback_text="FAILED tests/test_session_cases.py::test_nested_accumulator_identity - AssertionError: assert False is True",
        traceback_files=["session.py"],
        repo=t2008_repo,
        hidden=t2008_hidden,
        ref=t2008_ref,
        mutant1=t2008_m1,
        mutant2=t2008_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H03"],
        assertions=[
            ("test_nested_accumulator_identity", "session.py docstring: 'MUST mutate accumulator in-place ... Do NOT create deep copies'", "Yes", "DISTRACTOR")
        ]
    )

    print("Family 2 registered (Tasks 2005-2008).")
