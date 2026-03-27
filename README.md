# SUTD-Grade-Checker

> A collection of command-line utilities for SUTD students — GPA calculator, CAP planner, score-to-grade converter, and weekly workload estimator. Built using SUTD's actual grading system.

---

## Tools

| Tool | Description |
|------|-------------|
| `gpa` | Calculate your GPA from module grades |
| `cap` | Simulate future semesters — what GPA do I need to hit my target? |
| `score` | Convert a raw score (e.g. 73%) to grade and GPA points |
| `workload` | Estimate total weekly hours for your module load |

---

## Installation

```bash
git clone https://github.com/yeelaiii/sutd-tools
cd sutd-tools
python3 sutd_tools.py --help
```

No external dependencies.

---

## Usage

```bash
# Run GPA calculator (demo mode)
python3 sutd_tools.py gpa

# Interactive mode — enter your own modules
python3 sutd_tools.py gpa -i

# Pass modules directly
python3 sutd_tools.py gpa -m "50.001,Intro to CS,12,A-" "50.002,Comp Structures,12,B+"

# CAP planner — what do I need to hit 4.0?
python3 sutd_tools.py cap --current-gpa 3.17 --current-cu 144 --target-gpa 3.5 --future-cu 96

# Convert raw score to grade
python3 sutd_tools.py score 73.5

# Workload estimator
python3 sutd_tools.py workload
python3 sutd_tools.py workload -i   # enter your own modules
```

---

## SUTD Grading Scale

| Score | Grade | GPA Points |
|-------|-------|------------|
| 90–100 | A+ / A | 5.0 |
| 85–90 | A- | 4.5 |
| 80–85 | B+ | 4.0 |
| 75–80 | B | 3.5 |
| 70–75 | B- | 3.0 |
| 65–70 | C+ | 2.5 |
| 60–65 | C | 2.0 |
| 55–60 | C- | 1.5 |
| 50–55 | D+ | 1.0 |
| 45–50 | D | 0.5 |
| < 40 | F | 0.0 |

---

## Roadmap

- [ ] Timetable conflict checker (paste your modules, detect clashes)
- [ ] Degree audit tool (track completed vs required modules)
- [ ] eDimension deadline tracker
- [ ] SUTD course review aggregator

---

**Elijah Soon** · SUTD Year 3 CS&D · [yeelaiii.github.io](https://yeelaiii.github.io)
