# SAT Model Visualizer

**BLG 345E - Logic and Computability - Project #5**

A comprehensive visualization module for SAT solver results that transforms complex boolean satisfiability proof data into three human-readable formats: row-based model verification, step-by-step inference traces, and graphical decision tree representations.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Input Specifications](#input-specifications)
- [Output Formats](#output-formats)
- [Examples](#examples)
- [Implementation Details](#implementation-details)
- [Testing](#testing)
- [Contributors](#contributors)
- [License](#license)

---

## 🎯 Overview

This project serves as the final proof and analysis module of a complete SAT solver pipeline. It integrates outputs from three predecessor projects to create comprehensive visualizations that aid in understanding how the solver found a satisfying assignment (or proved unsatisfiability).

### Pipeline Integration

```
Project #2 (Parser)  ──┐
                       ├──> Project #5 (Visualizer) ──> visualization_output.txt
Project #3 (Inference)─┤
                       │
Project #4 (Search)  ──┘
```

---

## ✨ Features

- **🔗 Automated Integration**: Seamlessly combines outputs from Projects #2, #3, and #4
- **👁️ Multiple Views**: Three complementary visualization formats
- **📖 Human-Readable**: Converts internal solver data into understandable representations
- **🔍 Complete Trace**: Shows both failed and successful solution paths
- **⚠️ Error Handling**: Validates inputs and gracefully handles UNSAT cases
- **🎯 Smart Filtering**: Distinguishes clause-level from formula-level satisfaction

---

## 📁 Project Structure

```
sat-visualizer/
├── visualizer.py           # Main visualizer implementation
├── initial_cnf.txt         # Input: CNF formula (from Project #2)
├── final_model.txt         # Input: Final model (from Project #4)
├── execution_trace*.txt    # Input: Execution traces (from Project #3)
├── visualization_output.txt # Output: Complete visualization
├── test_cases/             # Test suite directory
│   ├── test_1/
│   ├── test_2/
│   └── ...
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/sat-visualizer.git

# Navigate to project directory
cd sat-visualizer

# Run the visualizer
python visualizer.py
```

---

## 💻 Usage

### Basic Usage

```python
from visualizer import SATVisualizer

# Initialize visualizer
visualizer = SATVisualizer()

# Specify input files
cnf_file = "initial_cnf.txt"
model_file = "final_model.txt"
trace_files = ["execution_trace1.txt", "execution_trace2.txt"]
output_file = "visualization_output.txt"

# Generate visualizations
visualizer.visualize(cnf_file, model_file, trace_files, output_file)
```

### Command Line

```bash
python visualizer.py
```

The script will automatically look for input files in the current directory and generate `visualization_output.txt`.

---

## 📥 Input Specifications

### Input 1: Initial CNF Formula (`initial_cnf.txt`)

Output from Project #2 containing the parsed CNF formula:

```
--- 1. HEADER AND METADATA ---
V: 3
C: 4
--- 3. CLAUSE LIST (PREMISES) ---
[C_ID] | [Literals (Signed Ints)] | [Watched Indices]
C1    | [-1, 2]                    | [0, 1]
C2    | [-2, -3]                   | [0, 1]
C3    | [3, 1]                     | [0, 1]
C4    | [-2, 3]                    | [0, 1]
```

### Input 2: Execution Trace (`execution_trace*.txt`)

Output from Project #3 showing the BCP execution log:

```
--- STATUS ---
STATUS: SAT
DL: 1
--- BCP EXECUTION LOG ---
[DL1] DECIDE      L=-1  |
[DL1] UNIT        L=2   | C1
[DL1] ASSIGN      L=2   |
[DL1] SATISFIED         |
```

### Input 3: Final Model (`final_model.txt`)

Output from Project #4 containing the satisfying assignment:

```
STATUS: SAT
--- FINAL VARIABLE STATE ---
1 | FALSE
2 | TRUE
3 | TRUE
```

---

## 📤 Output Formats

### 1. Row Form - Model Verification

Line-by-line verification showing how the model satisfies each clause:

```
============================================================
ROW FORM - MODEL VERIFICATION
============================================================
Model: A=0, B=1, C=1

C1 | -   +       | 1 + 1 = 1
C2 |     -   -   | 0 + 0 = 1
C3 |         +   + | 1 + 0 = 1
C4 |     -   +   | 0 + 1 = 1
```

**Format Explanation:**
- First column: Signs of literals (- for negation, + for positive)
- Second column: Evaluated values (1 for TRUE, 0 for FALSE)
- Third column: Sum showing clause is satisfied (≥1)

### 2. Inference Form - Logical Trace

Step-by-step presentation of the execution path:

```
============================================================
INFERENCE FORM - LOGICAL TRACE
============================================================
C1 | -A + B
C2 | -B + -C
C3 | C + A
C4 | -B + C

---------- Decision L=2
C2 | -C
C3 | C + A
C4 | C

---------- Unit L=-3
C3 | A
C4 | 0 | Conflict

---------- Decision L=-2
C1 | -A
C3 | C + A

---------- Unit L=-1
C3 | C

---------- Unit L=3
Satisfied
```

**Format Explanation:**
- Shows initial clauses, then progressively simplifies them
- Decisions are marked with dashes
- Unit propagations show derived assignments
- Conflicts indicate backtracking points
- Satisfied clauses are removed from display

### 3. Tree Form - Search Tree

Graphical representation of the DPLL search tree:

```
============================================================
TREE FORM - SEARCH TREE
============================================================
Root
|
|
|----- Decide B = 1
| |
| |----- Assign C = 0
| |
| |----- Conflict!
|
|----- Decide B = 0
|
|
|
|----- Unit A = 0
|----- Unit C = 1
|----- Satisfied!
```

**Format Explanation:**
- Root represents the initial state
- Branches show different decision paths
- Failed branches (leading to conflicts) are shown
- Successful path leads to "Satisfied!"

---

## 📚 Examples

### Example 1: Simple SAT Formula

**Input CNF:**
```
C1: A ∨ B
C2: ¬B ∨ ¬C
C3: C ∨ A
C4: ¬B ∨ C
```

**Final Model:**
```
A = 0, B = 0, C = 1
```

**Execution Path:**
1. Decide B = 1 → Conflict
2. Backtrack
3. Decide B = 0 → A = 0 → C = 1 → Satisfied

See [test_cases/example1/](test_cases/example1/) for complete files.

### Example 2: UNSAT Formula

When the formula is unsatisfiable, the visualizer shows all attempted paths leading to conflicts.

See [test_cases/example_unsat/](test_cases/example_unsat/) for complete files.

---

## 🔧 Implementation Details

### Core Modules

#### `SATVisualizer` Class

Main class containing all visualization logic.

**Key Methods:**

- `parse_initial_cnf(filename)`: Extracts CNF formula and variable mappings
- `parse_final_model(filename)`: Reads final variable assignments
- `parse_execution_traces(filenames)`: Combines and filters execution traces
- `generate_row_form()`: Creates model verification table
- `generate_inference_form()`: Builds step-by-step logical trace
- `generate_tree_form()`: Constructs decision tree visualization
- `visualize()`: Main orchestration function

### Algorithm Highlights

#### Smart Trace Filtering

The visualizer distinguishes between:
- **Clause-level satisfaction**: `[DL1] SATISFIED | C2` (ignored)
- **Formula-level satisfaction**: `[DL1] SATISFIED |` (kept)

```python
if 'SATISFIED' in line:
    parts = line.split('|')
    if len(parts) >= 2:
        after_pipe = parts[-1].strip()
        if after_pipe and after_pipe.startswith('C'):
            continue  # Skip clause-level
    trace_segment.append(line)  # Keep formula-level
```

#### Clause Simplification Logic

```python
def _format_clause(literals, assignments):
    for lit in literals:
        var_id = abs(lit)
        if var_id in assignments:
            var_value = assignments[var_id]
            # Check if literal satisfies clause
            if (lit > 0 and var_value) or (lit < 0 and not var_value):
                return ""  # Clause satisfied
        else:
            # Variable unassigned, include in output
            parts.append(format_literal(lit))
    return " + ".join(parts) if parts else "0"
```

#### Tree Structure Building

Uses lookahead to detect failed branches:

```python
for i, step in enumerate(trace):
    if 'DECIDE' in step:
        will_conflict = False
        for future_step in trace[i+1:]:
            if 'CONFLICT' in future_step:
                will_conflict = True
                break
        # Use different formatting for failed vs successful branches
```

---

## 🧪 Testing

### Test Suite

The project includes comprehensive test cases covering:

1. **Simple SAT**: Basic satisfiable formulas
2. **Complex SAT**: Multiple backtracking scenarios
3. **UNSAT**: Unsatisfiable formulas
4. **Edge Cases**: Empty clauses, unit clauses, pure literals

### Running Tests

```bash
cd test_cases
python run_tests.py
```

### Creating Custom Tests

1. Create a new directory in `test_cases/`
2. Add input files: `initial_cnf.txt`, `final_model.txt`, `execution_trace*.txt`
3. Add expected output: `expected_output.txt`
4. Run test suite

---

## 👥 Contributors

- **Your Name** - Initial work and implementation
- **Team Members** - Testing and validation

### Course Information

- **Course**: BLG 345E - Logic and Computability
- **Institution**: Istanbul Technical University
- **Instructor**: Asst. Prof. Mehmet Tahir Sandıkkaya
- **Teaching Assistant**: Res. Assist. Ali Esad Uğur

---

## 📄 License

This project is part of academic coursework at Istanbul Technical University.

---

## 🙏 Acknowledgments

- Thanks to the course instructors for project specifications
- Projects #2, #3, and #4 teams for providing compatible output formats
- SAT solver research community for DPLL algorithm foundations

---

<div align="center">
Made with ❤️ for BLG 345E Logic and Computability
</div>