#!/usr/bin/env python3
"""
sutd-tools
==========
A collection of utilities for SUTD students.

Tools:
    gpa         GPA calculator (handles SUTD's grading system)
    cap         CAP planner — simulate future semesters
    mcs         MCS (Minimum Cumulative Score) calculator
    workload    Weekly workload estimator

Author: Elijah Soon (github.com/yeelaiii)
Usage: python3 sutd_tools.py <tool> [options]
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Colours
# ─────────────────────────────────────────────────────────────
G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"
R = "\033[91m"; B = "\033[1m";  X = "\033[0m"

# ─────────────────────────────────────────────────────────────
# SUTD Grading System
# ─────────────────────────────────────────────────────────────
GRADE_POINTS = {
    "A+": 5.0, "A": 5.0, "A-": 4.5,
    "B+": 4.0, "B": 3.5, "B-": 3.0,
    "C+": 2.5, "C": 2.0, "C-": 1.5,
    "D+": 1.0, "D": 0.5,
    "F":  0.0,
    "S":  None,  # Satisfactory (no GPA impact)
    "U":  None,  # Unsatisfactory
    "W":  None,  # Withdrawn
    "EX": None,  # Exempted
}

GRADE_BOUNDARIES = {
    (90, 100): "A+", (85, 90): "A", (80, 85): "A-",
    (75, 80):  "B+", (70, 75): "B", (65, 70): "B-",
    (60, 65):  "C+", (55, 60): "C", (50, 55): "C-",
    (45, 50):  "D+", (40, 45): "D",
    (0,  40):  "F",
}

def score_to_grade(score: float) -> str:
    for (low, high), grade in GRADE_BOUNDARIES.items():
        if low <= score < high:
            return grade
    return "A+" if score >= 90 else "F"

def grade_to_points(grade: str) -> Optional[float]:
    return GRADE_POINTS.get(grade.upper())

# ─────────────────────────────────────────────────────────────
# GPA Calculator
# ─────────────────────────────────────────────────────────────
@dataclass
class Module:
    code: str
    name: str
    credits: float
    grade: str
    points: Optional[float] = None

    def __post_init__(self):
        self.points = grade_to_points(self.grade)

def calculate_gpa(modules: list[Module]) -> tuple[float, float, float]:
    """Returns (GPA, total_credit_units, graded_credit_units)"""
    total_points = 0.0
    graded_cu = 0.0
    total_cu = sum(m.credits for m in modules)

    for m in modules:
        if m.points is not None:  # Skip S/U/W/EX
            total_points += m.points * m.credits
            graded_cu += m.credits

    gpa = total_points / graded_cu if graded_cu > 0 else 0.0
    return round(gpa, 4), total_cu, graded_cu

def gpa_tool(args):
    print(f"\n{B}  SUTD GPA Calculator{X}\n{'─'*50}")

    if args.interactive:
        modules = []
        print(f"  Enter modules (type 'done' when finished)\n")
        while True:
            code = input(f"  Module code (or 'done'): ").strip()
            if code.lower() == 'done':
                break
            name   = input(f"  Module name: ").strip()
            credits = float(input(f"  Credit units: ").strip())
            grade  = input(f"  Grade (A+/A/A-/B+/B/B-/C+/C/C-/D+/D/F/S/U): ").strip().upper()

            if grade not in GRADE_POINTS:
                print(f"  {R}Invalid grade. Try again.{X}")
                continue

            modules.append(Module(code, name, credits, grade))

    elif args.modules:
        # Format: "CODE,NAME,CREDITS,GRADE CODE2,NAME2,CREDITS2,GRADE2 ..."
        modules = []
        for entry in args.modules:
            parts = entry.split(',')
            if len(parts) != 4:
                print(f"{R}[-] Invalid format: {entry}. Use CODE,NAME,CREDITS,GRADE{X}")
                continue
            modules.append(Module(parts[0], parts[1], float(parts[2]), parts[3]))
    else:
        # Demo with sample modules
        print(f"  {Y}[Demo mode — use -i for interactive or -m to pass modules]{X}\n")
        modules = [
            Module("50.001", "Introduction to CS & Programming", 12, "A-"),
            Module("50.002", "Computation Structures", 12, "B+"),
            Module("50.004", "Algorithms", 12, "B"),
            Module("50.005", "Computer System Engineering", 12, "A"),
            Module("50.020", "Network Security", 12, "B+"),
            Module("50.021", "Artificial Intelligence", 12, "A-"),
        ]

    if not modules:
        print(f"{R}[-] No modules entered.{X}")
        return

    gpa, total_cu, graded_cu = calculate_gpa(modules)

    print(f"\n  {'Code':<10} {'Name':<35} {'CU':<5} {'Grade':<6} {'Points'}")
    print(f"  {'─'*70}")
    for m in modules:
        pts = f"{m.points:.1f}" if m.points is not None else "S/U"
        print(f"  {m.code:<10} {m.name[:34]:<35} {m.credits:<5} {m.grade:<6} {pts}")

    print(f"\n  {'─'*50}")
    print(f"  Total CUs       : {total_cu}")
    print(f"  Graded CUs      : {graded_cu}")

    colour = G if gpa >= 4.0 else (Y if gpa >= 3.0 else R)
    print(f"  {B}GPA             : {colour}{gpa:.4f} / 5.0{X}")

    # Classification
    if gpa >= 4.5:
        honour = "Highest Distinction"
    elif gpa >= 4.0:
        honour = "High Distinction"
    elif gpa >= 3.5:
        honour = "Distinction"
    elif gpa >= 3.0:
        honour = "Merit"
    else:
        honour = "Pass"
    print(f"  Classification  : {honour}\n")


# ─────────────────────────────────────────────────────────────
# CAP Planner — simulate future semesters
# ─────────────────────────────────────────────────────────────
def cap_planner(args):
    print(f"\n{B}  SUTD CAP Planner{X}\n{'─'*50}")

    current_gpa  = args.current_gpa
    current_cu   = args.current_cu
    target_gpa   = args.target_gpa
    future_cu    = args.future_cu

    current_points = current_gpa * current_cu
    total_cu       = current_cu + future_cu

    needed_points  = target_gpa * total_cu - current_points
    needed_gpa     = needed_points / future_cu if future_cu > 0 else 0

    print(f"\n  Current GPA     : {current_gpa:.4f}")
    print(f"  Current CUs     : {current_cu}")
    print(f"  Target GPA      : {target_gpa:.4f}")
    print(f"  Future CUs      : {future_cu}")
    print(f"\n  {'─'*40}")

    if needed_gpa > 5.0:
        print(f"  {R}Target GPA is not achievable in {future_cu} CUs.{X}")
        max_achievable = (current_points + 5.0 * future_cu) / total_cu
        print(f"  Max achievable GPA: {max_achievable:.4f}")
    elif needed_gpa < 0:
        print(f"  {G}Target already exceeded!{X}")
    else:
        print(f"  Required avg GPA for future mods: {Y}{needed_gpa:.4f}{X}")
        # Find matching grade
        for grade, pts in sorted(GRADE_POINTS.items(), key=lambda x: x[1] or 0, reverse=True):
            if pts is not None and pts >= needed_gpa:
                closest_grade = grade
                break
        print(f"  Roughly equivalent to getting  : {Y}{closest_grade}{X} consistently")
    print()


# ─────────────────────────────────────────────────────────────
# Score → Grade converter
# ─────────────────────────────────────────────────────────────
def score_tool(args):
    score = args.score
    grade = score_to_grade(score)
    points = grade_to_points(grade)
    colour = G if points and points >= 4.0 else (Y if points and points >= 3.0 else R)
    print(f"\n  Score {score}% → {colour}{grade}{X} ({points} GPA points)\n")


# ─────────────────────────────────────────────────────────────
# Workload estimator
# ─────────────────────────────────────────────────────────────
def workload_tool(args):
    print(f"\n{B}  SUTD Weekly Workload Estimator{X}\n{'─'*50}")
    print(f"  {Y}Rule of thumb: 1 CU ≈ 1-2 hrs/week of study{X}\n")

    # Standard SUTD modules
    if args.interactive:
        modules = []
        print("  Enter your modules this term (type 'done' when finished)\n")
        while True:
            name = input("  Module name (or 'done'): ").strip()
            if name.lower() == 'done':
                break
            credits = float(input("  Credit units: ").strip())
            contact = float(input("  Contact hours/week: ").strip())
            modules.append((name, credits, contact))
    else:
        # Default example
        modules = [
            ("50.038 Computational Data Science", 12, 4),
            ("50.020 Network Security", 12, 4),
            ("50.045 Information Retrieval", 12, 4),
            ("50.046 Cloud Computing", 12, 3),
            ("HASS Elective", 9, 3),
        ]

    total_contact = 0
    total_study   = 0
    total_cu      = 0

    print(f"\n  {'Module':<40} {'CU':<5} {'Contact':<10} {'Est. Study'}")
    print(f"  {'─'*68}")

    for name, cu, contact in modules:
        study_est = cu * 1.5  # conservative estimate
        total_contact += contact
        total_study   += study_est
        total_cu      += cu
        print(f"  {name[:39]:<40} {cu:<5} {contact:<10} ~{study_est:.0f} hrs/wk")

    total = total_contact + total_study
    print(f"\n  {'─'*50}")
    print(f"  Total CUs       : {total_cu}")
    print(f"  Contact hours   : {total_contact} hrs/wk")
    print(f"  Est. self-study : ~{total_study:.0f} hrs/wk")
    colour = R if total > 60 else (Y if total > 45 else G)
    print(f"  {B}Total est. load : {colour}~{total:.0f} hrs/wk{X}")

    if total > 60:
        print(f"\n  {R}⚠ Heavy workload — consider dropping an elective{X}")
    elif total > 45:
        print(f"\n  {Y}! Moderate-heavy workload — manageable but plan carefully{X}")
    else:
        print(f"\n  {G}✓ Reasonable workload{X}")
    print()


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="SUTD Tools — utilities for SUTD students | github.com/yeelaiii"
    )
    sub = parser.add_subparsers(dest="tool", required=True)

    # GPA
    p = sub.add_parser("gpa", help="Calculate your GPA")
    p.add_argument("-i", "--interactive", action="store_true", help="Enter modules interactively")
    p.add_argument("-m", "--modules", nargs="+", help="Modules as CODE,NAME,CREDITS,GRADE")

    # CAP planner
    p = sub.add_parser("cap", help="Simulate future GPA")
    p.add_argument("--current-gpa",  type=float, required=True, help="Current GPA (e.g. 3.17)")
    p.add_argument("--current-cu",   type=float, required=True, help="Current credit units completed")
    p.add_argument("--target-gpa",   type=float, required=True, help="Target GPA")
    p.add_argument("--future-cu",    type=float, required=True, help="Remaining credit units")

    # Score to grade
    p = sub.add_parser("score", help="Convert raw score to grade + GPA points")
    p.add_argument("score", type=float, help="Raw score (0-100)")

    # Workload
    p = sub.add_parser("workload", help="Estimate weekly workload")
    p.add_argument("-i", "--interactive", action="store_true")

    args = parser.parse_args()

    tools = {
        "gpa":      gpa_tool,
        "cap":      cap_planner,
        "score":    score_tool,
        "workload": workload_tool,
    }
    tools[args.tool](args)


if __name__ == "__main__":
    main()
