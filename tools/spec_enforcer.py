#!/usr/bin/env python3
"""Spec Enforcer — CI gate for design-contract fidelity & rubric scoring.

Usage:
  python tools/spec_enforcer.py
    --card-id P2.2.1
    --board docs/board_bullets.yaml
    --coverage coverage.xml
    --diffbase origin/main

Exits non‑zero if score < min_score.
"""
from __future__ import annotations
import argparse, ast, os, re, subprocess, sys, xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Any

try:
    import yaml  # type: ignore
except Exception as e:
    print("[enforcer] Missing PyYAML — add to dev deps.")
    raise

# -------- rubric defaults (can be overridden later by tools/rubric.yaml) --------
RUBRIC = {
    "min_score": 9,
    "checks": [
        {"name": "design", "weight": 2},
        {"name": "tests", "weight": 2},
        {"name": "concurrency", "weight": 1},
        {"name": "security", "weight": 2},
        {"name": "observability", "weight": 1},
        {"name": "docs", "weight": 1},
        {"name": "types", "weight": 1},
    ],
}

@dataclass
class Contract:
    file: str | None
    interface: str | None
    constraints: List[str]
    tests: List[str]

# --------------------------- helpers ---------------------------

def run(cmd: List[str]) -> str:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return res.stdout


def git_changed_files(diffbase: str) -> List[str]:
    out = run(["git", "diff", "--name-only", f"{diffbase}...HEAD"]).splitlines()
    return [p for p in out if p.strip()]


def load_board(board_path: str) -> Dict[str, Any]:
    with open(board_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Flatten into id->node mapping
    mapping: Dict[str, Any] = {}
    def add(node: Dict[str, Any]):
        if "id" in node:
            mapping[node["id"]] = node
        # children list optional
        for child in node.get("children", []) or []:
            # give child an id if missing (not ideal; expect IDs in YAML)
            if "id" not in child and "task" in child:
                slug = re.sub(r"[^a-z0-9]+","-", child["task"].lower())
                child["id"] = node.get("id", "P?") + ".child:" + slug
            mapping[child["id"]] = child
    if isinstance(data, list):
        for item in data:
            add(item)
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                v.setdefault("id", k)
                add(v)
    return mapping


def parse_contract(node: Dict[str, Any]) -> Contract:
    dc = node.get("design_contract") or {}
    return Contract(
        file=dc.get("file"),
        interface=dc.get("interface"),
        constraints=list(dc.get("constraints", [])),
        tests=list(dc.get("tests", [])),
    )

# -------------------- check implementations --------------------

def check_design(contract: Contract) -> (bool, str):
    ok = True
    reasons = []
    if contract.file:
        if not os.path.exists(contract.file):
            ok = False
            reasons.append(f"missing file: {contract.file}")
        else:
            # If interface is provided, do a shallow AST signature check
            if contract.interface:
                sigs = re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)", contract.interface)
                try:
                    with open(contract.file, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    have = {f"{n}({','.join([a.arg for a in node.args.args])})" for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) for n in [node.name]}
                    for name, params in sigs:
                        # weak containment check; upgrade later if needed
                        found = any(s.startswith(f"{name}(") for s in have)
                        if not found:
                            ok = False
                            reasons.append(f"missing function: {name}() in {contract.file}")
                except Exception as e:
                    ok = False
                    reasons.append(f"AST error: {e}")
    if not contract.file and not contract.interface:
        reasons.append("no file/interface in contract — skipping design check")
    return ok, "; ".join(reasons) or "ok"


def check_tests(coverage_xml: str) -> (bool, str):
    try:
        tree = ET.parse(coverage_xml)
        root = tree.getroot()
        lines = float(root.attrib.get("line-rate", 0)) * 100
        # branch-rate may be missing in some tools
        branches = float(root.attrib.get("branch-rate", 0)) * 100
        ok = lines >= 85 and branches >= 80
        return ok, f"lines={lines:.1f}%, branches={branches:.1f}%"
    except Exception as e:
        return False, f"coverage parse error: {e}"


def check_concurrency(path: str) -> (bool, str):
    if not path or not os.path.exists(path):
        return True, "n/a"
    txt = open(path, "r", encoding="utf-8").read()
    problems = []
    if re.search(r"\brequests\.(get|post|put|delete)\(", txt):
        problems.append("sync requests call found")
    if re.search(r"asyncio\.Queue\(\s*\)", txt):
        problems.append("unbounded asyncio.Queue detected")
    return (len(problems) == 0), ", ".join(problems) or "ok"


def check_security(path: str) -> (bool, str):
    if not path or not os.path.exists(path):
        return True, "n/a"
    txt = open(path, "r", encoding="utf-8").read()
    problems = []
    if re.search(r"(api|secret|token).{0,40}=['\"]\w+['\"]", txt, re.I):
        problems.append("hardcoded secret-like token")
    return (len(problems) == 0), ", ".join(problems) or "ok"


def check_observability(path: str) -> (bool, str):
    if not path or not os.path.exists(path):
        return True, "n/a"
    txt = open(path, "r", encoding="utf-8").read()
    if "trace_id" not in txt and "order_id" not in txt:
        return False, "trace_id/order_id not referenced"
    return True, "ok"

# ------------------------------ main ------------------------------

def score(card: Dict[str, Any], contract: Contract, coverage_xml: str) -> int:
    total = 0
    # design
    ok, _ = check_design(contract)
    total += 2 if ok else 0
    # tests
    ok, _ = check_tests(coverage_xml)
    total += 2 if ok else 0
    # concurrency/security/observability on target file if provided
    c_ok, _ = check_concurrency(contract.file or "")
    s_ok, _ = check_security(contract.file or "")
    o_ok, _ = check_observability(contract.file or "")
    total += 1 if c_ok else 0
    total += 2 if s_ok else 0
    total += 1 if o_ok else 0
    # docs/types left as manual rubric items for now (enforced via PR template)
    total += 1  # docs
    total += 1  # types
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card-id", required=True)
    ap.add_argument("--board", required=True)
    ap.add_argument("--coverage", default="coverage.xml")
    ap.add_argument("--diffbase", default="origin/main")
    args = ap.parse_args()

    board = load_board(args.board)
    if args.card_id not in board:
        print(f"[enforcer] Card {args.card_id} not found in board {args.board}")
        return 2
    node = board[args.card_id]
    contract = parse_contract(node)

    sc = score(node, contract, args.coverage)
    print(f"[enforcer] SCORE={sc} / 10 for {args.card_id}")
    if sc < RUBRIC["min_score"]:
        print("[enforcer] Failing below rubric threshold")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())