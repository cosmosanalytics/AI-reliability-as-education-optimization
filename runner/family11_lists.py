"""Family 11: config_lists (Tasks 2053 - 2060).

Governing Rule: Rule H12 (Configuration Merge and Deduplicated List Concatenation:
When merging hierarchical configuration dictionaries, nested dictionaries are merged recursively.
However, list values must NOT be replaced; lists must be concatenated in order of
[base_items + override_items] with duplicate items removed while preserving first-seen order.)
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_11(add_task):
    # =========================================================================
    # Task 2053: Microservice Endpoint Configuration Merge (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2053_repo = {
        "endpoint_model.py": '''"""Configuration models for service endpoints."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ServiceEndpointConfig:
    service_name: str
    settings: Dict[str, Any]
    active: bool = True

    def get_endpoints(self) -> List[str]:
        return self.settings.get("endpoints", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service_name,
            "settings": self.settings,
            "active": self.active
        }
''',
        "schema_validator.py": '''"""Schema and key validation utilities."""
from typing import Dict, Any

def validate_config_structure(config: Dict[str, Any]) -> bool:
    if not isinstance(config, dict):
        raise TypeError("Configuration must be a dictionary")
    return True

def sanitize_service_name(name: str) -> str:
    return name.strip().lower()
''',
        "config_merger.py": '''"""Hierarchical service configuration merger."""
from typing import Dict, Any, List
from endpoint_model import ServiceEndpointConfig
from schema_validator import validate_config_structure, sanitize_service_name

def merge_configurations(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges hierarchical service configuration dictionaries.
    Nested dictionaries are merged recursively. List values must NOT be replaced;
    lists must be concatenated in order of [base_items + override_items] with duplicate
    items removed while preserving first-seen order.
    """
    validate_config_structure(base)
    validate_config_structure(override)
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_configurations(result[k], v)
        else:
            result[k] = v
    return result

def build_endpoint_profile(service_name: str, base: Dict[str, Any], override: Dict[str, Any]) -> ServiceEndpointConfig:
    clean_name = sanitize_service_name(service_name)
    merged = merge_configurations(base, override)
    return ServiceEndpointConfig(service_name=clean_name, settings=merged)
''',
        "tests/test_config.py": '''from config_merger import merge_configurations, build_endpoint_profile

def test_service_execution():
    base = {"service": "auth", "timeout": 30}
    override = {"timeout": 15}
    res = merge_configurations(base, override)
    assert res["timeout"] == 15
    profile = build_endpoint_profile("AUTH_SVC", base, override)
    assert profile.service_name == "auth_svc"
'''
    }

    t2053_hidden = {
        "tests/test_config_cases.py": '''from config_merger import merge_configurations

def test_case_1():
    base = {"routing": {"regions": ["us-east-1", "eu-west-1"]}}
    override = {"routing": {"regions": ["eu-west-1", "ap-southeast-1"]}}
    merged = merge_configurations(base, override)
    assert merged["routing"]["regions"] == ["us-east-1", "eu-west-1", "ap-southeast-1"]

def test_case_2():
    base = {"allowed_hosts": ["internal.net", "api.net"]}
    override = {"allowed_hosts": ["api.net", "gateway.net"]}
    merged = merge_configurations(base, override)
    assert merged["allowed_hosts"] == ["internal.net", "api.net", "gateway.net"]
'''
    }

    t2053_ref = {
        "config_merger.py": '''"""Hierarchical service configuration merger."""
from typing import Dict, Any, List
from endpoint_model import ServiceEndpointConfig
from schema_validator import validate_config_structure, sanitize_service_name

def merge_configurations(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges hierarchical service configuration dictionaries.
    Nested dictionaries are merged recursively. List values must NOT be replaced;
    lists must be concatenated in order of [base_items + override_items] with duplicate
    items removed while preserving first-seen order.
    """
    validate_config_structure(base)
    validate_config_structure(override)
    result = dict(base)
    for k, v in override.items():
        if k in result:
            if isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = merge_configurations(result[k], v)
            elif isinstance(result[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in result[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                result[k] = combined
            else:
                result[k] = v
        else:
            result[k] = v
    return result

def build_endpoint_profile(service_name: str, base: Dict[str, Any], override: Dict[str, Any]) -> ServiceEndpointConfig:
    clean_name = sanitize_service_name(service_name)
    merged = merge_configurations(base, override)
    return ServiceEndpointConfig(service_name=clean_name, settings=merged)
'''
    }

    t2053_m1 = {
        "config_merger.py": '''"""Hierarchical service configuration merger."""
from typing import Dict, Any, List
from endpoint_model import ServiceEndpointConfig
from schema_validator import validate_config_structure, sanitize_service_name

def merge_configurations(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    validate_config_structure(base)
    validate_config_structure(override)
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_configurations(result[k], v)
        else:
            result[k] = v
    return result

def build_endpoint_profile(service_name: str, base: Dict[str, Any], override: Dict[str, Any]) -> ServiceEndpointConfig:
    clean_name = sanitize_service_name(service_name)
    merged = merge_configurations(base, override)
    return ServiceEndpointConfig(service_name=clean_name, settings=merged)
'''
    }

    t2053_m2 = {
        "config_merger.py": '''"""Hierarchical service configuration merger."""
from typing import Dict, Any, List
from endpoint_model import ServiceEndpointConfig
from schema_validator import validate_config_structure, sanitize_service_name

def merge_configurations(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    validate_config_structure(base)
    validate_config_structure(override)
    result = dict(base)
    for k, v in override.items():
        if k in result:
            if isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = merge_configurations(result[k], v)
            elif isinstance(result[k], list) and isinstance(v, list):
                result[k] = result[k] + v
            else:
                result[k] = v
        else:
            result[k] = v
    return result

def build_endpoint_profile(service_name: str, base: Dict[str, Any], override: Dict[str, Any]) -> ServiceEndpointConfig:
    clean_name = sanitize_service_name(service_name)
    merged = merge_configurations(base, override)
    return ServiceEndpointConfig(service_name=clean_name, settings=merged)
'''
    }

    add_task(
        tid=2053,
        family="config_lists",
        name="Microservice Endpoint Configuration Merge",
        class_tag="STATED",
        issue="Incident INC-9201: Cross-region endpoints were dropped when tenant configuration overrides replaced base routing lists.",
        traceback_text="FAILED tests/test_config_cases.py::test_case_1 - AssertionError: assert ['eu-west-1', 'ap-southeast-1'] == ['us-east-1', 'eu-west-1', 'ap-southeast-1']",
        traceback_files=["config_merger.py"],
        repo=t2053_repo,
        hidden=t2053_hidden,
        ref=t2053_ref,
        mutant1=t2053_m1,
        mutant2=t2053_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "config_merger.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed'", "Yes", "STATED"),
            ("test_case_2", "config_merger.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed'", "Yes", "STATED"),
        ]
    )

    # =========================================================================
    # Task 2054: Cloud Infrastructure Cluster Specification Merge (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2054_repo = {
        "list_merger.py": '''"""Low-level dictionary and list hierarchy merger."""
from typing import Dict, Any, List

def merge_spec_values(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merges dictionary values."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_spec_values(result[k], v)
        else:
            result[k] = v
    return result

def is_spec_empty(spec: Dict[str, Any]) -> bool:
    return len(spec) == 0
''',
        "cluster_manifest.py": '''"""Cluster deployment manifest definitions."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ClusterManifest:
    cluster_id: str
    spec: Dict[str, Any]
    status: str = "pending"

    def get_node_zones(self) -> List[str]:
        return self.spec.get("zones", [])

    def to_payload(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "spec": self.spec,
            "status": self.status
        }
''',
        "cluster_builder.py": '''"""Infrastructure cluster specification builder."""
from typing import Dict, Any
from list_merger import merge_spec_values, is_spec_empty
from cluster_manifest import ClusterManifest

def build_cluster_spec(cluster_id: str, base_spec: Dict[str, Any], tenant_spec: Dict[str, Any]) -> ClusterManifest:
    if is_spec_empty(base_spec):
        raise ValueError("Base spec cannot be empty")
    merged = merge_spec_values(base_spec, tenant_spec)
    return ClusterManifest(cluster_id=cluster_id, spec=merged)
''',
        "tests/test_cluster.py": '''from cluster_builder import build_cluster_spec

def test_service_execution():
    base = {"nodes": 3, "zones": ["zone-a"]}
    tenant = {"nodes": 5}
    manifest = build_cluster_spec("cls-1", base, tenant)
    assert manifest.cluster_id == "cls-1"
    assert manifest.spec["nodes"] == 5
    assert "zone-a" in manifest.get_node_zones()
'''
    }

    t2054_hidden = {
        "tests/test_cluster_cases.py": '''from cluster_builder import build_cluster_spec

def test_case_1():
    base = {"zones": ["zone-a", "zone-b"]}
    tenant = {"zones": ["zone-b", "zone-c"]}
    manifest = build_cluster_spec("cls-1", base, tenant)
    assert manifest.spec["zones"] == ["zone-a", "zone-b", "zone-c"]

def test_case_2():
    base = {"network": {"dns_servers": ["8.8.8.8", "1.1.1.1"]}}
    tenant = {"network": {"dns_servers": ["1.1.1.1", "9.9.9.9"]}}
    manifest = build_cluster_spec("cls-2", base, tenant)
    assert manifest.spec["network"]["dns_servers"] == ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
'''
    }

    t2054_ref = {
        "list_merger.py": '''"""Low-level dictionary and list hierarchy merger."""
from typing import Dict, Any, List

def merge_spec_values(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merges dictionary values."""
    result = dict(base)
    for k, v in override.items():
        if k in result:
            if isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = merge_spec_values(result[k], v)
            elif isinstance(result[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in result[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                result[k] = combined
            else:
                result[k] = v
        else:
            result[k] = v
    return result

def is_spec_empty(spec: Dict[str, Any]) -> bool:
    return len(spec) == 0
'''
    }

    t2054_m1 = {
        "list_merger.py": '''"""Low-level dictionary and list hierarchy merger."""
from typing import Dict, Any, List

def merge_spec_values(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_spec_values(result[k], v)
        else:
            result[k] = v
    return result

def is_spec_empty(spec: Dict[str, Any]) -> bool:
    return len(spec) == 0
'''
    }

    t2054_m2 = {
        "list_merger.py": '''"""Low-level dictionary and list hierarchy merger."""
from typing import Dict, Any, List

def merge_spec_values(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for k, v in override.items():
        if k in result:
            if isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = merge_spec_values(result[k], v)
            elif isinstance(result[k], list) and isinstance(v, list):
                result[k] = result[k] + v
            else:
                result[k] = v
        else:
            result[k] = v
    return result

def is_spec_empty(spec: Dict[str, Any]) -> bool:
    return len(spec) == 0
'''
    }

    add_task(
        tid=2054,
        family="config_lists",
        name="Cloud Infrastructure Cluster Specification Merge",
        class_tag="TAUGHT",
        issue="Incident INC-9202: Secondary zone availability was lost during cluster provisioning when tenant spec replaced base zone array.",
        traceback_text="FAILED tests/test_cluster_cases.py::test_case_1 - AssertionError: assert ['zone-b', 'zone-c'] == ['zone-a', 'zone-b', 'zone-c']",
        traceback_files=["cluster_builder.py"],
        repo=t2054_repo,
        hidden=t2054_hidden,
        ref=t2054_ref,
        mutant1=t2054_m1,
        mutant2=t2054_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2055: CI/CD Pipeline Step Arguments Merger (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2055_repo = {
        "step_schema.py": '''"""Schema definitions for CI/CD workflow steps."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PipelineStep:
    step_id: str
    command: str
    args: Dict[str, Any]
    env_vars: Dict[str, str] = field(default_factory=dict)

    def is_executable(self) -> bool:
        return bool(self.step_id and self.command)
''',
        "env_validator.py": '''"""Environment variable validator for build steps."""
from typing import Dict

def sanitize_env_vars(env: Dict[str, str]) -> Dict[str, str]:
    return {k.upper(): str(v) for k, v in env.items()}

def is_valid_step_name(name: str) -> bool:
    return bool(name and len(name) < 64)
''',
        "pipeline_composer.py": '''"""CI/CD pipeline step composition engine."""
from typing import Dict, Any, List
from step_schema import PipelineStep
from env_validator import sanitize_env_vars, is_valid_step_name

def merge_step_args(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = merge_step_args(merged[k], v)
        else:
            merged[k] = v
    return merged

def compose_pipeline_step(step_id: str, command: str, base_args: Dict[str, Any], env_args: Dict[str, Any]) -> PipelineStep:
    if not is_valid_step_name(step_id):
        raise ValueError("Invalid step ID")
    merged_args = merge_step_args(base_args, env_args)
    env = sanitize_env_vars(merged_args.get("env", {}))
    return PipelineStep(step_id=step_id, command=command, args=merged_args, env_vars=env)
''',
        "tests/test_pipeline.py": '''from pipeline_composer import compose_pipeline_step

def test_service_execution():
    base = {"timeout": 60, "flags": ["--verbose"]}
    over = {"timeout": 120}
    step = compose_pipeline_step("build_step", "make", base, over)
    assert step.step_id == "build_step"
    assert step.args["timeout"] == 120
    assert step.is_executable() is True
'''
    }

    t2055_hidden = {
        "tests/test_pipeline_cases.py": '''from pipeline_composer import compose_pipeline_step

def test_case_1():
    base = {"flags": ["-Wall", "-O2"]}
    over = {"flags": ["-O2", "-g"]}
    step = compose_pipeline_step("compile", "gcc", base, over)
    assert step.args["flags"] == ["-Wall", "-O2", "-g"]

def test_case_2():
    base = {"matrix": {"include": ["py310", "py311"]}}
    over = {"matrix": {"include": ["py311", "py312"]}}
    step = compose_pipeline_step("matrix_run", "pytest", base, over)
    assert step.args["matrix"]["include"] == ["py310", "py311", "py312"]
'''
    }

    t2055_ref = {
        "pipeline_composer.py": '''"""CI/CD pipeline step composition engine."""
from typing import Dict, Any, List
from step_schema import PipelineStep
from env_validator import sanitize_env_vars, is_valid_step_name

def merge_step_args(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged:
            if isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = merge_step_args(merged[k], v)
            elif isinstance(merged[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in merged[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                merged[k] = combined
            else:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def compose_pipeline_step(step_id: str, command: str, base_args: Dict[str, Any], env_args: Dict[str, Any]) -> PipelineStep:
    if not is_valid_step_name(step_id):
        raise ValueError("Invalid step ID")
    merged_args = merge_step_args(base_args, env_args)
    env = sanitize_env_vars(merged_args.get("env", {}))
    return PipelineStep(step_id=step_id, command=command, args=merged_args, env_vars=env)
'''
    }

    t2055_m1 = {
        "pipeline_composer.py": '''"""CI/CD pipeline step composition engine."""
from typing import Dict, Any, List
from step_schema import PipelineStep
from env_validator import sanitize_env_vars, is_valid_step_name

def merge_step_args(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = merge_step_args(merged[k], v)
        else:
            merged[k] = v
    return merged

def compose_pipeline_step(step_id: str, command: str, base_args: Dict[str, Any], env_args: Dict[str, Any]) -> PipelineStep:
    if not is_valid_step_name(step_id):
        raise ValueError("Invalid step ID")
    merged_args = merge_step_args(base_args, env_args)
    env = sanitize_env_vars(merged_args.get("env", {}))
    return PipelineStep(step_id=step_id, command=command, args=merged_args, env_vars=env)
'''
    }

    t2055_m2 = {
        "pipeline_composer.py": '''"""CI/CD pipeline step composition engine."""
from typing import Dict, Any, List
from step_schema import PipelineStep
from env_validator import sanitize_env_vars, is_valid_step_name

def merge_step_args(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged:
            if isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = merge_step_args(merged[k], v)
            elif isinstance(merged[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in v + merged[k]:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                merged[k] = combined
            else:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def compose_pipeline_step(step_id: str, command: str, base_args: Dict[str, Any], env_args: Dict[str, Any]) -> PipelineStep:
    if not is_valid_step_name(step_id):
        raise ValueError("Invalid step ID")
    merged_args = merge_step_args(base_args, env_args)
    env = sanitize_env_vars(merged_args.get("env", {}))
    return PipelineStep(step_id=step_id, command=command, args=merged_args, env_vars=env)
'''
    }

    add_task(
        tid=2055,
        family="config_lists",
        name="CI/CD Pipeline Step Arguments Merger",
        class_tag="TAUGHT",
        issue="Incident INC-9203: CI build step omitted mandatory base compilation flags when target overrides were merged.",
        traceback_text="FAILED tests/test_pipeline_cases.py::test_case_1 - AssertionError: assert ['-O2', '-g'] == ['-Wall', '-O2', '-g']",
        traceback_files=["pipeline_composer.py"],
        repo=t2055_repo,
        hidden=t2055_hidden,
        ref=t2055_ref,
        mutant1=t2055_m1,
        mutant2=t2055_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2056: Security Firewall Whitelist Policy Merge (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2056_repo = {
        "firewall_rule.py": '''"""Security firewall rule models."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class FirewallPolicy:
    policy_name: str
    rules: Dict[str, Any]
    enabled: bool = True

    def get_whitelist(self) -> List[str]:
        return self.rules.get("whitelist", [])
''',
        "cidr_parser.py": '''"""CIDR validation and network parsing utilities."""
from typing import List

def validate_cidrs(cidrs: List[str]) -> bool:
    return all("/" in c or "." in c for c in cidrs)

def count_active_rules(rules: dict) -> int:
    return len(rules)
''',
        "policy_merger.py": '''"""Firewall security policy merger."""
from typing import Dict, Any, List
from firewall_rule import FirewallPolicy
from cidr_parser import validate_cidrs, count_active_rules

def merge_firewall_policy(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges firewall rules.
    Local security override policy: When overriding IP and port lists, the override list
    replaces the base list entirely to revoke obsolete allowances.
    Do NOT concatenate or combine lists.
    """
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], list) and isinstance(v, list):
            merged[k] = merged[k] + v
        else:
            merged[k] = v
    return merged

def build_firewall_policy(name: str, base: Dict[str, Any], override: Dict[str, Any]) -> FirewallPolicy:
    merged = merge_firewall_policy(base, override)
    _ = count_active_rules(merged)
    return FirewallPolicy(policy_name=name, rules=merged)
''',
        "tests/test_policy.py": '''from policy_merger import merge_firewall_policy, build_firewall_policy

def test_service_execution():
    base = {"action": "drop", "ports": [80]}
    over = {"action": "allow"}
    p = build_firewall_policy("web_sec", base, over)
    assert p.policy_name == "web_sec"
    assert p.rules["action"] == "allow"
'''
    }

    t2056_hidden = {
        "tests/test_policy_cases.py": '''from policy_merger import merge_firewall_policy

def test_case_1():
    base = {"whitelist": ["10.0.0.1", "10.0.0.2"]}
    over = {"whitelist": ["192.168.1.1"]}
    res = merge_firewall_policy(base, over)
    assert res["whitelist"] == ["192.168.1.1"]

def test_case_2():
    base = {"ports": [80, 443, 8080]}
    over = {"ports": [443]}
    res = merge_firewall_policy(base, over)
    assert res["ports"] == [443]
'''
    }

    t2056_ref = {
        "policy_merger.py": '''"""Firewall security policy merger."""
from typing import Dict, Any, List
from firewall_rule import FirewallPolicy
from cidr_parser import validate_cidrs, count_active_rules

def merge_firewall_policy(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges firewall rules.
    Local security override policy: When overriding IP and port lists, the override list
    replaces the base list entirely to revoke obsolete allowances.
    Do NOT concatenate or combine lists.
    """
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = merge_firewall_policy(merged[k], v)
        else:
            merged[k] = v
    return merged

def build_firewall_policy(name: str, base: Dict[str, Any], override: Dict[str, Any]) -> FirewallPolicy:
    merged = merge_firewall_policy(base, override)
    _ = count_active_rules(merged)
    return FirewallPolicy(policy_name=name, rules=merged)
'''
    }

    t2056_m1 = {
        "policy_merger.py": '''"""Firewall security policy merger."""
from typing import Dict, Any, List
from firewall_rule import FirewallPolicy
from cidr_parser import validate_cidrs, count_active_rules

def merge_firewall_policy(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged:
            if isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = merge_firewall_policy(merged[k], v)
            elif isinstance(merged[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in merged[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                merged[k] = combined
            else:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def build_firewall_policy(name: str, base: Dict[str, Any], override: Dict[str, Any]) -> FirewallPolicy:
    merged = merge_firewall_policy(base, override)
    _ = count_active_rules(merged)
    return FirewallPolicy(policy_name=name, rules=merged)
'''
    }

    t2056_m2 = {
        "policy_merger.py": '''"""Firewall security policy merger."""
from typing import Dict, Any, List
from firewall_rule import FirewallPolicy
from cidr_parser import validate_cidrs, count_active_rules

def merge_firewall_policy(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], list) and isinstance(v, list):
            merged[k] = []
        else:
            merged[k] = v
    return merged

def build_firewall_policy(name: str, base: Dict[str, Any], override: Dict[str, Any]) -> FirewallPolicy:
    merged = merge_firewall_policy(base, override)
    _ = count_active_rules(merged)
    return FirewallPolicy(policy_name=name, rules=merged)
'''
    }

    add_task(
        tid=2056,
        family="config_lists",
        name="Security Firewall Whitelist Policy Merge",
        class_tag="DISTRACTOR",
        issue="Security Breach SEC-304: Revoked IP addresses remained whitelisted because firewall merge concatenated deprecated rules.",
        traceback_text="FAILED tests/test_policy_cases.py::test_case_1 - AssertionError: assert ['10.0.0.1', '10.0.0.2', '192.168.1.1'] == ['192.168.1.1']",
        traceback_files=["policy_merger.py"],
        repo=t2056_repo,
        hidden=t2056_hidden,
        ref=t2056_ref,
        mutant1=t2056_m1,
        mutant2=t2056_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "policy_merger.py docstring: 'override list replaces the base list entirely'", "Yes", "DISTRACTOR"),
            ("test_case_2", "policy_merger.py docstring: 'override list replaces the base list entirely'", "Yes", "DISTRACTOR"),
        ]
    )

    # =========================================================================
    # Task 2057: Application Feature Gate Setting Aggregator (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2057_repo = {
        "gate_combiner.py": '''"""Feature gate dictionary combiner."""
from typing import Dict, Any, List

def combine_gate_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Combines gate dictionaries."""
    res = dict(base)
    for k, v in override.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = combine_gate_dicts(res[k], v)
        else:
            res[k] = v
    return res

def is_valid_gate_key(key: str) -> bool:
    return bool(key and isinstance(key, str))
''',
        "license_checker.py": '''"""Tenant licensing tier check."""
from typing import Dict, Any

def check_tenant_tier(tenant_id: str) -> str:
    return "enterprise" if "ent" in tenant_id else "standard"

def is_tier_supported(tier: str) -> bool:
    return tier in ("standard", "enterprise")

def get_max_allowed_gates(tier: str) -> int:
    return 100 if tier == "enterprise" else 20
''',
        "gate_manager.py": '''"""Feature gate resolution manager."""
from typing import Dict, Any
from gate_combiner import combine_gate_dicts, is_valid_gate_key
from license_checker import check_tenant_tier, is_tier_supported

def resolve_feature_gates(tenant_id: str, default_gates: Dict[str, Any], tenant_gates: Dict[str, Any]) -> Dict[str, Any]:
    tier = check_tenant_tier(tenant_id)
    if not is_tier_supported(tier):
        raise ValueError("Unsupported tier")
    merged = combine_gate_dicts(default_gates, tenant_gates)
    return {
        "tenant_id": tenant_id,
        "tier": tier,
        "gates": merged
    }
''',
        "tests/test_gate.py": '''from gate_manager import resolve_feature_gates

def test_service_execution():
    defaults = {"beta": False, "roles": ["admin"]}
    custom = {"beta": True}
    res = resolve_feature_gates("tenant_ent_1", defaults, custom)
    assert res["tenant_id"] == "tenant_ent_1"
    assert res["tier"] == "enterprise"
    assert res["gates"]["beta"] is True
'''
    }

    t2057_hidden = {
        "tests/test_gate_cases.py": '''from gate_manager import resolve_feature_gates

def test_case_1():
    defaults = {"roles": ["viewer", "editor"]}
    custom = {"roles": ["editor", "billing_admin"]}
    res = resolve_feature_gates("tenant_1", defaults, custom)
    assert res["gates"]["roles"] == ["viewer", "editor", "billing_admin"]

def test_case_2():
    defaults = {"features": {"modules": ["auth", "billing"]}}
    custom = {"features": {"modules": ["billing", "analytics"]}}
    res = resolve_feature_gates("tenant_2", defaults, custom)
    assert res["gates"]["features"]["modules"] == ["auth", "billing", "analytics"]
'''
    }

    t2057_ref = {
        "gate_combiner.py": '''"""Feature gate dictionary combiner."""
from typing import Dict, Any, List

def combine_gate_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Combines gate dictionaries."""
    res = dict(base)
    for k, v in override.items():
        if k in res:
            if isinstance(res[k], dict) and isinstance(v, dict):
                res[k] = combine_gate_dicts(res[k], v)
            elif isinstance(res[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in res[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                res[k] = combined
            else:
                res[k] = v
        else:
            res[k] = v
    return res

def is_valid_gate_key(key: str) -> bool:
    return bool(key and isinstance(key, str))
'''
    }

    t2057_m1 = {
        "gate_combiner.py": '''"""Feature gate dictionary combiner."""
from typing import Dict, Any, List

def combine_gate_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base)
    for k, v in override.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = combine_gate_dicts(res[k], v)
        else:
            res[k] = v
    return res

def is_valid_gate_key(key: str) -> bool:
    return bool(key and isinstance(key, str))
'''
    }

    t2057_m2 = {
        "gate_combiner.py": '''"""Feature gate dictionary combiner."""
from typing import Dict, Any, List

def combine_gate_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base)
    for k, v in override.items():
        if k in res:
            if isinstance(res[k], dict) and isinstance(v, dict):
                res[k] = combine_gate_dicts(res[k], v)
            elif isinstance(res[k], list) and isinstance(v, list):
                res[k] = res[k] + v
            else:
                res[k] = v
        else:
            res[k] = v
    return res

def is_valid_gate_key(key: str) -> bool:
    return bool(key and isinstance(key, str))
'''
    }

    add_task(
        tid=2057,
        family="config_lists",
        name="Application Feature Gate Setting Aggregator",
        class_tag="TAUGHT",
        issue="Incident INC-9204: Tenant lost base permission roles when custom billing admin roles were assigned.",
        traceback_text="FAILED tests/test_gate_cases.py::test_case_1 - AssertionError: assert ['editor', 'billing_admin'] == ['viewer', 'editor', 'billing_admin']",
        traceback_files=["gate_manager.py"],
        repo=t2057_repo,
        hidden=t2057_hidden,
        ref=t2057_ref,
        mutant1=t2057_m1,
        mutant2=t2057_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2058: Database Migration Script Option Merger (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2058_repo = {
        "migration_model.py": '''"""Database migration plan models."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class MigrationPlan:
    plan_id: str
    target_version: str
    options: Dict[str, Any]

    def get_skip_tables(self) -> List[str]:
        return self.options.get("skip_tables", [])
''',
        "version_parser.py": '''"""Database version string parsing utilities."""
def is_valid_version(version: str) -> bool:
    parts = version.split(".")
    return len(parts) >= 2 and all(p.isdigit() for p in parts)

def extract_major_version(version: str) -> int:
    return int(version.split(".")[0])
''',
        "migration_loader.py": '''"""Migration execution option loader."""
from typing import Dict, Any, List
from migration_model import MigrationPlan
from version_parser import is_valid_version, extract_major_version

def merge_migration_options(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges migration option dictionaries recursively.
    Nested dictionaries are merged recursively. List values must NOT be replaced;
    lists must be concatenated in order of [base_items + override_items] with duplicate
    items removed while preserving first-seen order.
    """
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = merge_migration_options(merged[k], v)
        else:
            merged[k] = v
    return merged

def prepare_migration_plan(plan_id: str, version: str, base_opt: Dict[str, Any], run_opt: Dict[str, Any]) -> MigrationPlan:
    if not is_valid_version(version):
        raise ValueError("Invalid target version")
    opts = merge_migration_options(base_opt, run_opt)
    return MigrationPlan(plan_id=plan_id, target_version=version, options=opts)
''',
        "tests/test_migration.py": '''from migration_loader import prepare_migration_plan

def test_service_execution():
    base = {"dry_run": True, "timeout": 300}
    run = {"dry_run": False}
    plan = prepare_migration_plan("mig-1", "2.1", base, run)
    assert plan.plan_id == "mig-1"
    assert plan.target_version == "2.1"
    assert plan.options["dry_run"] is False
'''
    }

    t2058_hidden = {
        "tests/test_migration_cases.py": '''from migration_loader import merge_migration_options

def test_case_1():
    base = {"skip_tables": ["audit_logs", "temp_sessions"]}
    over = {"skip_tables": ["temp_sessions", "event_queue"]}
    opts = merge_migration_options(base, over)
    assert opts["skip_tables"] == ["audit_logs", "temp_sessions", "event_queue"]

def test_case_2():
    base = {"plugins": {"pre_hooks": ["backup", "lock_schema"]}}
    over = {"plugins": {"pre_hooks": ["lock_schema", "validate_constraints"]}}
    opts = merge_migration_options(base, over)
    assert opts["plugins"]["pre_hooks"] == ["backup", "lock_schema", "validate_constraints"]
'''
    }

    t2058_ref = {
        "migration_loader.py": '''"""Migration execution option loader."""
from typing import Dict, Any, List
from migration_model import MigrationPlan
from version_parser import is_valid_version, extract_major_version

def merge_migration_options(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges migration option dictionaries recursively.
    Nested dictionaries are merged recursively. List values must NOT be replaced;
    lists must be concatenated in order of [base_items + override_items] with duplicate
    items removed while preserving first-seen order.
    """
    merged = dict(base)
    for k, v in override.items():
        if k in merged:
            if isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = merge_migration_options(merged[k], v)
            elif isinstance(merged[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in merged[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                merged[k] = combined
            else:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def prepare_migration_plan(plan_id: str, version: str, base_opt: Dict[str, Any], run_opt: Dict[str, Any]) -> MigrationPlan:
    if not is_valid_version(version):
        raise ValueError("Invalid target version")
    opts = merge_migration_options(base_opt, run_opt)
    return MigrationPlan(plan_id=plan_id, target_version=version, options=opts)
'''
    }

    t2058_m1 = {
        "migration_loader.py": '''"""Migration execution option loader."""
from typing import Dict, Any, List
from migration_model import MigrationPlan
from version_parser import is_valid_version, extract_major_version

def merge_migration_options(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = merge_migration_options(merged[k], v)
        else:
            merged[k] = v
    return merged

def prepare_migration_plan(plan_id: str, version: str, base_opt: Dict[str, Any], run_opt: Dict[str, Any]) -> MigrationPlan:
    if not is_valid_version(version):
        raise ValueError("Invalid target version")
    opts = merge_migration_options(base_opt, run_opt)
    return MigrationPlan(plan_id=plan_id, target_version=version, options=opts)
'''
    }

    t2058_m2 = {
        "migration_loader.py": '''"""Migration execution option loader."""
from typing import Dict, Any, List
from migration_model import MigrationPlan
from version_parser import is_valid_version, extract_major_version

def merge_migration_options(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k in merged:
            if isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = merge_migration_options(merged[k], v)
            elif isinstance(merged[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in merged[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                merged[k] = sorted(combined)
            else:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def prepare_migration_plan(plan_id: str, version: str, base_opt: Dict[str, Any], run_opt: Dict[str, Any]) -> MigrationPlan:
    if not is_valid_version(version):
        raise ValueError("Invalid target version")
    opts = merge_migration_options(base_opt, run_opt)
    return MigrationPlan(plan_id=plan_id, target_version=version, options=opts)
'''
    }

    add_task(
        tid=2058,
        family="config_lists",
        name="Database Migration Script Option Merger",
        class_tag="STATED",
        issue="Incident INC-9205: Migration script accidentally executed against table audit_logs because base skip_tables list was overwritten.",
        traceback_text="FAILED tests/test_migration_cases.py::test_case_1 - AssertionError: assert ['temp_sessions', 'event_queue'] == ['audit_logs', 'temp_sessions', 'event_queue']",
        traceback_files=["migration_loader.py"],
        repo=t2058_repo,
        hidden=t2058_hidden,
        ref=t2058_ref,
        mutant1=t2058_m1,
        mutant2=t2058_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "migration_loader.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed'", "Yes", "STATED"),
            ("test_case_2", "migration_loader.py docstring: 'concatenated in order of [base_items + override_items] with duplicate items removed'", "Yes", "STATED"),
        ]
    )

    # =========================================================================
    # Task 2059: Service Mesh Route Matcher Configurator (TAUGHT, HRC=True, VTS=True)
    # =========================================================================
    t2059_repo = {
        "matcher_utils.py": '''"""Route path matching and dictionary consolidation."""
from typing import Dict, Any, List

def deep_merge_matchers(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base)
    for k, v in override.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = deep_merge_matchers(res[k], v)
        else:
            res[k] = v
    return res

def normalize_prefix(path: str) -> str:
    return "/" + path.strip("/")
''',
        "route_validator.py": '''"""Route pattern validator and routing helpers."""
def is_valid_route_pattern(pattern: str) -> bool:
    return pattern.startswith("/") and len(pattern) > 1

def count_route_segments(pattern: str) -> int:
    return len([s for s in pattern.split("/") if s])

def extract_primary_route(pattern: str) -> str:
    parts = [s for s in pattern.split("/") if s]
    return parts[0] if parts else "root"
''',
        "mesh_config.py": '''"""Service mesh routing configuration compiler."""
from typing import Dict, Any
from matcher_utils import deep_merge_matchers, normalize_prefix
from route_validator import is_valid_route_pattern, count_route_segments, extract_primary_route

def compile_route_profile(mesh_id: str, base_rules: Dict[str, Any], env_rules: Dict[str, Any]) -> Dict[str, Any]:
    merged = deep_merge_matchers(base_rules, env_rules)
    prefix = normalize_prefix(merged.get("prefix", "/"))
    primary = extract_primary_route(prefix)
    return {
        "mesh_id": mesh_id,
        "prefix": prefix,
        "primary": primary,
        "segments": count_route_segments(prefix),
        "rules": merged
    }
''',
        "tests/test_mesh.py": '''from mesh_config import compile_route_profile

def test_service_execution():
    base = {"prefix": "/api", "timeout_ms": 500}
    env = {"timeout_ms": 250}
    prof = compile_route_profile("mesh-1", base, env)
    assert prof["mesh_id"] == "mesh-1"
    assert prof["prefix"] == "/api"
    assert prof["rules"]["timeout_ms"] == 250
'''
    }

    t2059_hidden = {
        "tests/test_mesh_cases.py": '''from mesh_config import compile_route_profile

def test_case_1():
    base = {"headers": ["X-Tenant-Id", "Authorization"]}
    env = {"headers": ["Authorization", "X-Trace-Id"]}
    prof = compile_route_profile("mesh-1", base, env)
    assert prof["rules"]["headers"] == ["X-Tenant-Id", "Authorization", "X-Trace-Id"]

def test_case_2():
    base = {"match": {"methods": ["GET", "POST"]}}
    env = {"match": {"methods": ["POST", "PUT"]}}
    prof = compile_route_profile("mesh-2", base, env)
    assert prof["rules"]["match"]["methods"] == ["GET", "POST", "PUT"]
'''
    }

    t2059_ref = {
        "matcher_utils.py": '''"""Route path matching and dictionary consolidation."""
from typing import Dict, Any, List

def deep_merge_matchers(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base)
    for k, v in override.items():
        if k in res:
            if isinstance(res[k], dict) and isinstance(v, dict):
                res[k] = deep_merge_matchers(res[k], v)
            elif isinstance(res[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in res[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                res[k] = combined
            else:
                res[k] = v
        else:
            res[k] = v
    return res

def normalize_prefix(path: str) -> str:
    return "/" + path.strip("/")
'''
    }

    t2059_m1 = {
        "matcher_utils.py": '''"""Route path matching and dictionary consolidation."""
from typing import Dict, Any, List

def deep_merge_matchers(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base)
    for k, v in override.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = deep_merge_matchers(res[k], v)
        else:
            res[k] = v
    return res

def normalize_prefix(path: str) -> str:
    return "/" + path.strip("/")
'''
    }

    t2059_m2 = {
        "matcher_utils.py": '''"""Route path matching and dictionary consolidation."""
from typing import Dict, Any, List

def deep_merge_matchers(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(base)
    for k, v in override.items():
        if k in res:
            if isinstance(res[k], dict) and isinstance(v, dict):
                res[k] = deep_merge_matchers(res[k], v)
            elif isinstance(res[k], list) and isinstance(v, list):
                res[k] = res[k] + v
            else:
                res[k] = v
        else:
            res[k] = v
    return res

def normalize_prefix(path: str) -> str:
    return "/" + path.strip("/")
'''
    }

    add_task(
        tid=2059,
        family="config_lists",
        name="Service Mesh Route Matcher Configurator",
        class_tag="TAUGHT",
        issue="Incident INC-9206: Authentication proxy rejected calls because header matchers were truncated by environment override.",
        traceback_text="FAILED tests/test_mesh_cases.py::test_case_1 - AssertionError: assert ['Authorization', 'X-Trace-Id'] == ['X-Tenant-Id', 'Authorization', 'X-Trace-Id']",
        traceback_files=["mesh_config.py"],
        repo=t2059_repo,
        hidden=t2059_hidden,
        ref=t2059_ref,
        mutant1=t2059_m1,
        mutant2=t2059_m2,
        hidden_root_cause=True,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H12", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2060: Dynamic Routing Gate Table Overrides (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2060_repo = {
        "routing_entry.py": '''"""Routing entry definitions."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class RouteTableProfile:
    gateway_id: str
    rules: Dict[str, Any]
    active: bool = True

    def get_destinations(self) -> List[str]:
        return self.rules.get("destinations", [])
''',
        "protocol_filter.py": '''"""Protocol validation and health."""
def is_supported_protocol(proto: str) -> bool:
    return proto.lower() in ("http", "grpc", "tcp")

def compute_gateway_hash(gateway_id: str) -> int:
    return hash(gateway_id) % 1000
''',
        "route_table.py": '''"""Dynamic routing table manager."""
from typing import Dict, Any, List
from routing_entry import RouteTableProfile
from protocol_filter import is_supported_protocol, compute_gateway_hash

def apply_table_override(base_table: Dict[str, Any], new_table: Dict[str, Any]) -> Dict[str, Any]:
    """Applies routing table overrides.
    Local routing contract: Override list definitions completely replace base lists
    to enable complete table reassignment. Do NOT concatenate lists.
    """
    merged = dict(base_table)
    for k, v in new_table.items():
        if k in merged and isinstance(merged[k], list) and isinstance(v, list):
            merged[k] = merged[k] + v
        else:
            merged[k] = v
    return merged

def build_route_table(gateway_id: str, base_table: Dict[str, Any], new_table: Dict[str, Any]) -> RouteTableProfile:
    _ = compute_gateway_hash(gateway_id)
    rules = apply_table_override(base_table, new_table)
    return RouteTableProfile(gateway_id=gateway_id, rules=rules)
''',
        "tests/test_route.py": '''from route_table import build_route_table

def test_service_execution():
    base = {"protocol": "http", "destinations": ["10.0.0.1"]}
    over = {"protocol": "grpc"}
    rt = build_route_table("gw-1", base, over)
    assert rt.gateway_id == "gw-1"
    assert rt.rules["protocol"] == "grpc"
'''
    }

    t2060_hidden = {
        "tests/test_route_cases.py": '''from route_table import apply_table_override

def test_case_1():
    base = {"destinations": ["10.0.0.1", "10.0.0.2"]}
    over = {"destinations": ["10.1.0.1"]}
    res = apply_table_override(base, over)
    assert res["destinations"] == ["10.1.0.1"]

def test_case_2():
    base = {"backends": ["be-1", "be-2"]}
    over = {"backends": ["be-3"]}
    res = apply_table_override(base, over)
    assert res["backends"] == ["be-3"]
'''
    }

    t2060_ref = {
        "route_table.py": '''"""Dynamic routing table manager."""
from typing import Dict, Any, List
from routing_entry import RouteTableProfile
from protocol_filter import is_supported_protocol, compute_gateway_hash

def apply_table_override(base_table: Dict[str, Any], new_table: Dict[str, Any]) -> Dict[str, Any]:
    """Applies routing table overrides.
    Local routing contract: Override list definitions completely replace base lists
    to enable complete table reassignment. Do NOT concatenate lists.
    """
    merged = dict(base_table)
    for k, v in new_table.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = apply_table_override(merged[k], v)
        else:
            merged[k] = v
    return merged

def build_route_table(gateway_id: str, base_table: Dict[str, Any], new_table: Dict[str, Any]) -> RouteTableProfile:
    _ = compute_gateway_hash(gateway_id)
    rules = apply_table_override(base_table, new_table)
    return RouteTableProfile(gateway_id=gateway_id, rules=rules)
'''
    }

    t2060_m1 = {
        "route_table.py": '''"""Dynamic routing table manager."""
from typing import Dict, Any, List
from routing_entry import RouteTableProfile
from protocol_filter import is_supported_protocol, compute_gateway_hash

def apply_table_override(base_table: Dict[str, Any], new_table: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base_table)
    for k, v in new_table.items():
        if k in merged:
            if isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = apply_table_override(merged[k], v)
            elif isinstance(merged[k], list) and isinstance(v, list):
                combined = []
                seen = set()
                for item in merged[k] + v:
                    if item not in seen:
                        seen.add(item)
                        combined.append(item)
                merged[k] = combined
            else:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def build_route_table(gateway_id: str, base_table: Dict[str, Any], new_table: Dict[str, Any]) -> RouteTableProfile:
    _ = compute_gateway_hash(gateway_id)
    rules = apply_table_override(base_table, new_table)
    return RouteTableProfile(gateway_id=gateway_id, rules=rules)
'''
    }

    t2060_m2 = {
        "route_table.py": '''"""Dynamic routing table manager."""
from typing import Dict, Any, List
from routing_entry import RouteTableProfile
from protocol_filter import is_supported_protocol, compute_gateway_hash

def apply_table_override(base_table: Dict[str, Any], new_table: Dict[str, Any]) -> Dict[str, Any]:
    return dict(base_table)

def build_route_table(gateway_id: str, base_table: Dict[str, Any], new_table: Dict[str, Any]) -> RouteTableProfile:
    _ = compute_gateway_hash(gateway_id)
    rules = apply_table_override(base_table, new_table)
    return RouteTableProfile(gateway_id=gateway_id, rules=rules)
'''
    }

    add_task(
        tid=2060,
        family="config_lists",
        name="Dynamic Routing Gate Table Overrides",
        class_tag="DISTRACTOR",
        issue="Incident INC-9208: Traffic continued routing to decommissioned endpoints because override did not replace destination list.",
        traceback_text="FAILED tests/test_route_cases.py::test_case_1 - AssertionError: assert ['10.0.0.1', '10.0.0.2', '10.1.0.1'] == ['10.1.0.1']",
        traceback_files=["route_table.py"],
        repo=t2060_repo,
        hidden=t2060_hidden,
        ref=t2060_ref,
        mutant1=t2060_m1,
        mutant2=t2060_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H12"],
        assertions=[
            ("test_case_1", "route_table.py docstring: 'Override list definitions completely replace base lists'", "Yes", "DISTRACTOR"),
            ("test_case_2", "route_table.py docstring: 'Override list definitions completely replace base lists'", "Yes", "DISTRACTOR"),
        ]
    )

    print("Family 11 registered (Tasks 2053-2060).")
