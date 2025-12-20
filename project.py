"""
SAT Model Visualizer - BLG 345E Project #5
This module visualizes the SAT solver results in three forms:
1. Row Form: Line-by-line model verification
2. Inference Form: Step-by-step logical trace
3. Tree Form: Graphical search tree representation
"""

import re
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# For any experiment, below 2 const vars are enough to set.
FILE_ROOT = "exp_o1"
TRACE_COUNT = 1




CNF_FILE = FILE_ROOT + "/initial_cnf.txt"
MODEL_FILE = FILE_ROOT + "/final_model.txt"
TRACE_FILES = [FILE_ROOT+f"/execution_trace{x}.txt" for x in range(1,TRACE_COUNT+1) ]  
OUTPUT_FILE = FILE_ROOT + "/visualization_output.txt"

""" 
CNF_FILE = "initial_cnf.txt"
MODEL_FILE = "final_model.txt"
TRACE_FILES = ["execution_trace1.txt","execution_trace2.txt"]  # Add more files if needed
OUTPUT_FILE = "visualization_output.txt" 
""" 


class SATVisualizer:
    """Main class for SAT model visualization"""
    
    def __init__(self):
        self.variables = {}  # Variable ID to name mapping
        self.clauses = {}    # Clause ID to literals mapping
        self.model = {}      # Final variable assignments
        self.trace = []      # Execution trace steps

    def parse_initial_cnf(self, filename: str):
        """Parse the initial CNF formula file from Project #2"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            return
        
        # Extract variable count
        v_match = re.search(r'V:\s*(\d+)', content)
        if v_match:
            num_vars = int(v_match.group(1))
            for i in range(1, num_vars + 1):
                self.variables[i] = chr(64 + i)
        else:
            print("Warning: Could not find variable count")
        
        # Extract clauses
        clause_section = re.search(
            r'--- 3\. CLAUSE LIST.*?---\s*\n\[C_ID\].*?\n-+\n(.*?)(?=---|\Z)', 
            content, 
            re.DOTALL
        )
        
        if clause_section:
            clause_lines = clause_section.group(1).strip().split('\n')
            for line in clause_lines:
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 2:
                        clause_id = parts[0].strip()
                        literals_str = parts[1].strip()
                        literals = [int(x) for x in re.findall(r'-?\d+', literals_str)]
                        if literals:  # Only add non-empty clauses
                            self.clauses[clause_id] = literals
        else:
            print("Warning: Could not find clause list")        
   
    def parse_final_model(self, filename: str):
        """Parse the final model file from Project #4"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: {filename} not found")
            return
        
        # Check if SAT
        if 'STATUS: UNSAT' in content:
            print("Warning: Formula is UNSATISFIABLE - no model exists")
            return
        
        # Extract variable assignments
        lines = content.split('\n')
        for line in lines:
            match = re.match(r'(\d+)\s*\|\s*(TRUE|FALSE)', line)
            if match:
                var_id = int(match.group(1))
                value = match.group(2) == 'TRUE'
                self.model[var_id] = value
        
        if not self.model:
            print("Warning: No model assignments found")
    
    def parse_execution_traces(self, filenames: List[str]):
        """Parse and combine multiple execution trace files from Project #3"""
        sat_traces = []
        unsat_traces = []
        
        for filename in filenames:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Check STATUS
            status_match = re.search(r'STATUS:\s*(SAT|UNSAT|CONTINUE)', content)
            status = status_match.group(1) if status_match else None
            
            # Extract BCP execution log
            log_section = re.search(
                r'--- BCP EXECUTION LOG.*?---\s*\n(.*?)(?=---|\Z)',
                content,
                re.DOTALL
            )
            
            if log_section:
                log_lines = log_section.group(1).strip().split('\n')
                trace_segment = []
                for line in log_lines:
                    line = line.strip()
                    if line:
                        # Check for SATISFIED lines
                        if 'SATISFIED' in line:
                            # Split by | and check what comes after
                            parts = line.split('|')
                            if len(parts) >= 2:
                                # Check if there's a clause ID after the pipe
                                after_pipe = parts[-1].strip()  # Get last part after split
                                if after_pipe and after_pipe.startswith('C'):
                                    # Clause-level SATISFIED (e.g., "| C2"), skip it
                                    continue
                            # Formula-level SATISFIED (no clause after |, or just |)
                            trace_segment.append(line)
                        else:
                            trace_segment.append(line)
                
                # If this is a SAT trace but no formula-level SATISFIED was found, add one
                if status == 'SAT' and trace_segment:
                    # Check if there's already a SATISFIED in the trace
                    has_satisfied = any('SATISFIED' in line for line in trace_segment)
                    if not has_satisfied:
                        # Add a synthetic SATISFIED marker
                        trace_segment.append('[DL1] SATISFIED |')
                
                if status == 'SAT':
                    sat_traces.append(trace_segment)
                elif status == 'UNSAT':
                    unsat_traces.append(trace_segment)
                elif status == 'CONTINUE':
                    continue
        
        if sat_traces:
            self.trace = sat_traces[0]
        elif unsat_traces:
            self.trace = []
            for trace in unsat_traces:
                self.trace.extend(trace)
        else:
            self.trace = []


    def generate_row_form(self) -> str:
        """Generate Row Form visualization"""
        if not self.model:
            return "Error: No model available (formula may be UNSAT)"
        
        if not self.clauses:
            return "Error: No clauses available"
        
        output = []
        
        output.append("=" * 60)
        output.append("ROW FORM - MODEL VERIFICATION")
        output.append("=" * 60)
        output.append("")
        
        # Display model
        model_str = "Model: "
        model_parts = []
        for var_id in sorted(self.model.keys()):
            var_name = self.variables.get(var_id, f"V{var_id}")
            value = 1 if self.model[var_id] else 0
            model_parts.append(f"{var_name}={value}")
        model_str += ", ".join(model_parts)
        output.append(model_str)
        output.append("")
        
        # Verify each clause
        for clause_id in sorted(self.clauses.keys()):
            literals = self.clauses[clause_id]
            
            # Create position mapping for all variables
            num_vars = len(self.variables)
            signs = []
            values = []
            
            for var_id in range(1, num_vars + 1):
                # Check if this variable appears in the clause
                var_in_clause = False
                for lit in literals:
                    if abs(lit) == var_id:
                        var_value = self.model.get(var_id, False)
                        
                        # Add sign
                        if lit < 0:
                            signs.append('-')
                            eval_value = 1 if not var_value else 0
                        else:
                            signs.append('+')
                            eval_value = 1 if var_value else 0
                        
                        values.append(eval_value)
                        var_in_clause = True
                        break
                
                if not var_in_clause:
                    # Variable not in this clause - add spacing
                    signs.append(' ')
                    values.append(None)
            
            # Format output with proper spacing
            signs_str = '   '.join(signs)  # 3 spaces between each position
            values_list = []
            for v in values:
                if v is not None:
                    values_list.append(str(v))
            
            values_str = ' + '.join(values_list)
            total = 1 if sum(v for v in values if v is not None) > 0 else 0
            
            output.append(f"{clause_id} | {signs_str} | {values_str} = {total}")
        
        output.append("")
        return "\n".join(output)


    def generate_inference_form(self) -> str:
        """Generate Inference Form visualization"""
        output = []
        output.append("=" * 60)
        output.append("INFERENCE FORM - LOGICAL TRACE")
        output.append("=" * 60)
        output.append("")
        
        # Start with all clauses in readable form
        for clause_id in sorted(self.clauses.keys()):
            clause_str = self._format_clause(self.clauses[clause_id], {})
            output.append(f"{clause_id} | {clause_str}")
        
        output.append("")
        
        # Process trace
        assignments = {}  # Track current assignments
        
        for step in self.trace:
            # Parse different types of steps
            if 'DECIDE' in step:
                # Extract literal: [DL1] DECIDE L=2 |
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    output.append(f"---------- Decision L={literal}")
                    assignments[var_id] = literal > 0
                    simplified = self._show_simplified_clauses(assignments)
                    if simplified:
                        output.append(simplified)
            
            elif 'UNIT' in step and 'ASSIGN' not in step:
                # Extract literal: [DL1] UNIT L=-3 | C2
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    output.append(f"---------- Unit L={literal}")
                    assignments[var_id] = literal > 0
                    simplified = self._show_simplified_clauses(assignments)
                    if simplified:
                        output.append(simplified)
            
            elif 'CONFLICT' in step:
                # The conflict clause is already shown in the previous simplified output
                # Just add the conflict marker to the last line
                if output and output[-1].strip() and '|' in output[-1]:
                    # Append " | Conflict" to the last clause line
                    output[-1] = output[-1] + " | Conflict"
                output.append("")
            
            elif 'BACKTRACK' in step:
                # CRITICAL: Reset assignments to clear the failed branch
                assignments = {}
                output.append("")
            
            elif 'SATISFIED' in step:
                # Only add "Satisfied" once for formula-level satisfaction
                output.append("Satisfied")
                output.append("")
                break  # Stop processing after formula is satisfied
        
        return "\n".join(output)

     
    def _format_clause(self, literals: List[int], assignments: Dict[int, bool]) -> str:
        """Format a clause with variable names, returns empty string if satisfied"""
        parts = []
        
        for lit in literals:
            var_id = abs(lit)
            
            # Check if this variable is assigned
            if var_id in assignments:
                var_value = assignments[var_id]
                
                # Check if this literal makes the clause TRUE
                if (lit > 0 and var_value) or (lit < 0 and not var_value):
                    # Clause is satisfied by this literal
                    return ""  # Return empty to signal satisfaction
                # Otherwise, this literal is FALSE, so skip it (don't add to parts)
            else:
                # Variable not assigned yet, include literal in clause
                var_name = self.variables.get(var_id, f"V{var_id}")
                if lit < 0:
                    parts.append(f"-{var_name}")
                else:
                    parts.append(var_name)
        
        # If no parts left, clause has all false literals (conflict/empty clause)
        return " + ".join(parts) if parts else "0"

    def _show_simplified_clauses(self, assignments: Dict[int, bool]) -> str:
        """Show simplified clauses after assignments"""
        result = []
        
        for clause_id in sorted(self.clauses.keys()):
            literals = self.clauses[clause_id]
            clause_str = self._format_clause(literals, assignments)
            
            # Only show unsatisfied clauses (satisfied ones return empty string)
            if clause_str:
                result.append(f"{clause_id} | {clause_str}")
        
        return "\n".join(result) if result else ""

    
    def _format_clause_simple(self, literals: List[int]) -> str:
        """Simple clause formatting"""
        if not literals:
            return "0"
        parts = []
        for lit in literals:
            var_id = abs(lit)
            var_name = self.variables.get(var_id, f"V{var_id}")
            if lit < 0:
                parts.append(f"-{var_name}")
            else:
                parts.append(var_name)
        return " + ".join(parts)
    
    def generate_tree_form(self) -> str:
        """Generate Tree Form visualization"""
        output = []
        output.append("=" * 60)
        output.append("TREE FORM - SEARCH TREE")
        output.append("=" * 60)
        output.append("")
        output.append("Root")
        
        # Track decision level
        decision_level = 0
        in_failed_branch = False
        
        for i, step in enumerate(self.trace):
            if 'DECIDE' in step:
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    var_name = self.variables.get(var_id, f"V{var_id}")
                    value = 1 if literal > 0 else 0
                    
                    # Check if this decision will lead to conflict
                    will_conflict = False
                    for future_step in self.trace[i+1:]:
                        if 'CONFLICT' in future_step:
                            will_conflict = True
                            break
                        if 'BACKTRACK' in future_step or 'SATISFIED' in future_step:
                            break
                    
                    decision_level += 1
                    in_failed_branch = will_conflict
                    
                    # Add proper indentation based on decision level
                    if decision_level == 1:
                        output.append("|")
                        output.append("|----- Decide {0} = {1}".format(var_name, value))
                    else:
                        # For nested decisions
                        indent = " " * (11 * (decision_level - 1))
                        output.append(indent + "|")
                        output.append(indent + "|----- Decide {0} = {1}".format(var_name, value))
            
            elif 'UNIT' in step and 'ASSIGN' not in step:
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    var_name = self.variables.get(var_id, f"V{var_id}")
                    value = 1 if literal > 0 else 0
                    
                    # Calculate indentation based on decision level
                    indent = " " * (11 * decision_level)
                    
                    if in_failed_branch:
                        output.append("|          |")
                        output.append("|          |----- Assign {0} = {1}".format(var_name, value))
                    else:
                        output.append(indent + "|")
                        output.append(indent + "|----- Unit {0} = {1}".format(var_name, value))
            
            elif 'CONFLICT' in step:
                output.append("|          |")
                output.append("|          |----- Conflict!")
            
            elif 'BACKTRACK' in step:
                decision_level = 0
                in_failed_branch = False
            
            elif 'SATISFIED' in step:
                indent = " " * (11 * decision_level)
                output.append(indent + "|")
                output.append(indent + "|----- Satisfied!")
                break
        
        output.append("")
        return "\n".join(output)

    def visualize(self, cnf_file: str, model_file: str, trace_files: List[str], output_file: str):
        """Main function to generate all visualizations"""
        # Parse inputs
        print("Parsing initial CNF...")
        self.parse_initial_cnf(cnf_file)
        
        if not self.clauses:
            print("Error: Failed to parse clauses. Aborting.")
            return
        
        print("Parsing final model...")
        self.parse_final_model(model_file)
        
        if not self.model:
            print("Error: Failed to parse model. Aborting.")
            return
        
        print("Parsing execution traces...")
        self.parse_execution_traces(trace_files)
        
        if not self.trace:
            print("Warning: No execution trace found")
        
        # Generate visualizations
        print("Generating visualizations...")
        row_form = self.generate_row_form()
        inference_form = self.generate_inference_form()
        tree_form = self.generate_tree_form()
        
        # Write to output file
        with open(output_file, 'w') as f:
            f.write(row_form)
            f.write("\n\n")
            f.write(inference_form)
            f.write("\n\n")
            f.write(tree_form)
        
        print(f"Visualization saved to {output_file}")


def main():
    """Main entry point"""
    
    print("\n\n\n\nhttps://github.com/osman-yahya/logic-termp-prj\n\n\n\n")
    print("""
      ___           ___           ___                                                                                               
     /\  \         /\  \         /\  \                                                                                              
    /::\  \       /::\  \        \:\  \                                                                                             
   /:/\ \  \     /:/\:\  \        \:\  \                                                                                            
  _\:\~\ \  \   /::\~\:\  \       /::\  \                                                                                           
 /\ \:\ \ \__\ /:/\:\ \:\__\     /:/\:\__\                                                                                          
 \:\ \:\ \/__/ \/__\:\/:/  /    /:/  \/__/                                                                                          
  \:\ \:\__\        \::/  /    /:/  /                                                                                               
   \:\/:/  /        /:/  /     \/__/                                                                                                
    \::/  /        /:/  /                                                                                                           
     \/__/         \/__/                                                                                                            

 _    ___________ __  _____    __    _________   __________ 
| |  / /  _/ ___// / / /   |  / /   /  _/__  /  / ____/ __ |
| | / // / \__ \/ / / / /| | / /    / /   / /  / __/ / /_/ /
| |/ // / ___/ / /_/ / ___ |/ /____/ /   / /__/ /___/ _, _/ 
|___/___//____/\____/_/  |_/_____/___/  /____/_____/_/ |_|  
                                                            
""")
    visualizer = SATVisualizer()
    
    # Specify input files
    cnf_file = CNF_FILE
    model_file = MODEL_FILE 
    trace_files = TRACE_FILES # Add more files if needed
    output_file = OUTPUT_FILE
    


    # Generate visualizations
    visualizer.visualize(cnf_file, model_file, trace_files, output_file)
    
    print("Check 'visualization_output.txt' for results.")


if __name__ == "__main__":
    main()