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

CNF_FILE = "initial_cnf.txt"
MODEL_FILE = "final_model.txt"
TRACE_FILES = ["execution_trace1.txt","execution_trace2.txt"]  # Add more files if needed
OUTPUT_FILE = "visualization_output.txt"


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
            status_match = re.search(r'STATUS:\s*(SAT|UNSAT)', content)
            status = status_match.group(1) if status_match else None
            
            # Extract BCP execution log
            log_section = re.search(
                r'--- BCP EXECUTION LOG.*?---\s*\n(.*?)(?=---|\Z)',
                content,
                re.DOTALL
            )
            
            if log_section:
                log_lines = log_section.group(1).strip().split('\n')
                trace_segment = [line.strip() for line in log_lines if line.strip()]
                
                if status == 'SAT':
                    sat_traces.append(trace_segment)
                elif status == 'UNSAT':
                    unsat_traces.append(trace_segment)
        
        # Use the SAT trace if available (contains complete successful execution)
        # If no SAT trace, use UNSAT traces (all failed attempts)
        if sat_traces:
            # The SAT trace should contain the complete execution
            self.trace = sat_traces[0]  # There should typically be only one SAT trace
        elif unsat_traces:
            # If only UNSAT, concatenate all failed attempts
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
            
            # Create position mapping for all variables (A, B, C, etc.)
            num_vars = len(self.variables)
            positions = ['    '] * num_vars  # 4 spaces for empty positions
            values = ['   '] * num_vars  # 3 spaces for empty values
            
            for lit in literals:
                var_id = abs(lit)
                var_value = self.model.get(var_id, False)
                position_idx = var_id - 1  # 1->0, 2->1, 3->2
                
                # Set sign
                if lit < 0:
                    positions[position_idx] = '-   '  # negative with padding
                    eval_value = 1 if not var_value else 0
                else:
                    positions[position_idx] = '+   '  # positive with padding
                    eval_value = 1 if var_value else 0
                
                values[position_idx] = f'{eval_value}   '
            
            # Build strings
            signs_str = ''.join(positions).rstrip()
            values_list = [v.strip() for v in values if v.strip()]
            values_str = ' + '.join(values_list)
            total = 1 if sum(int(v.strip()) for v in values if v.strip()) > 0 else 0
            
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
                    var_name = self.variables.get(var_id, f"V{var_id}")
                    output.append(f"---------- Decision L={literal}")
                    assignments[var_id] = literal > 0
                    output.append(self._show_simplified_clauses(assignments))
            
            elif 'UNIT' in step and 'ASSIGN' not in step:
                # Extract literal: [DL1] UNIT L=-3 | C2
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    output.append(f"---------- Unit L={literal}")
                    assignments[var_id] = literal > 0
                    output.append(self._show_simplified_clauses(assignments))
            
            elif 'CONFLICT' in step:
                # The conflict clause is already shown in the previous simplified output
                # Just add the conflict marker to the last line
                if output and output[-1].strip() and '|' in output[-1]:
                    # Append " | Conflict" to the last clause line
                    output[-1] = output[-1] + " | Conflict"
                output.append("")
            
            elif 'BACKTRACK' in step:
                # Reset some assignments (simplified for visualization)
                output.append("")
            
            elif 'SATISFIED' in step:
                output.append("Satisfied")
                output.append("")
        
        return "\n".join(output)
    
    def _format_clause(self, literals: List[int], assignments: Dict[int, bool]) -> str:
        """Format a clause with variable names"""
        parts = []
        for lit in literals:
            var_id = abs(lit)
            var_name = self.variables.get(var_id, f"V{var_id}")
            
            # Check if assigned - if assigned and makes literal true, clause is satisfied
            if var_id in assignments:
                var_value = assignments[var_id]
                if (lit > 0 and var_value) or (lit < 0 and not var_value):
                    # This literal is TRUE, clause is satisfied - return empty to signal satisfaction
                    return ""
                # Literal is FALSE, skip it (don't add to parts)
            else:
                # Not assigned yet, include in clause
                if lit < 0:
                    parts.append(f"-{var_name}")
                else:
                    parts.append(var_name)
        return " + ".join(parts) if parts else "0"

    def _show_simplified_clauses(self, assignments: Dict[int, bool]) -> str:
        """Show simplified clauses after assignments"""
        result = []
        for clause_id in sorted(self.clauses.keys()):
            literals = self.clauses[clause_id]
            clause_str = self._format_clause(literals, assignments)
            
            # Empty string means clause is satisfied, don't show it
            if clause_str != "":
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
        
        # Parse trace to build tree structure
        current_depth = 0
        decision_stack = []
        
        for step in self.trace:
            if 'DECIDE' in step:
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    var_name = self.variables.get(var_id, f"V{var_id}")
                    value = 1 if literal > 0 else 0
                    
                    current_depth += 1
                    prefix = "|" + "\n|".join(["     "] * (current_depth - 1))
                    output.append(f"{prefix}")
                    output.append(f"{prefix}----- Decide {var_name} = {value}")
                    decision_stack.append(current_depth)
            
            elif 'UNIT' in step and 'ASSIGN' not in step:
                match = re.search(r'L=(-?\d+)', step)
                if match:
                    literal = int(match.group(1))
                    var_id = abs(literal)
                    var_name = self.variables.get(var_id, f"V{var_id}")
                    value = 1 if literal > 0 else 0
                    
                    prefix = "|" + "\n|".join(["     "] * current_depth)
                    output.append(f"{prefix}")
                    output.append(f"{prefix}----- Unit {var_name} = {value}")
            
            elif 'CONFLICT' in step:
                prefix = "|" + "\n|".join(["     "] * current_depth)
                output.append(f"{prefix}")
                output.append(f"{prefix}----- Conflict!")
            
            elif 'BACKTRACK' in step:
                if decision_stack:
                    current_depth = decision_stack.pop() - 1
            
            elif 'SATISFIED' in step:
                prefix = "|" + "\n|".join(["     "] * current_depth)
                output.append(f"{prefix}")
                output.append(f"{prefix}----- Satisfied!")
        
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
    # Example usage
    visualizer = SATVisualizer()
    
    # Specify input files
    cnf_file = CNF_FILE
    model_file = MODEL_FILE 
    trace_files = TRACE_FILES # Add more files if needed
    output_file = OUTPUT_FILE
    


    # Generate visualizations
    visualizer.visualize(cnf_file, model_file, trace_files, output_file)
    
    print("\nVisualization complete!")
    print("Check 'visualization_output.txt' for results.")


if __name__ == "__main__":
    main()