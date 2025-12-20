"""
Parser Module
-------------
Reads raw text files from the SAT solver.
Converts them into our Claue, TraceStep, and Model objects.
Nothing fancy, just standard parsing logic.
"""

import re
from data_structures import Clause, TraceStep

def parse_initial_cnf(filepath):
    """
    Reads the initial CNF file.
    
    We need to be a bit careful here to skip headers and only grab lines starting with 'C'.
    Returns a list of Clause objects.
    """
    clauses = []
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        return []

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Robust Parsing Logic:
        # We look for lines starting with "C" followed directly by a digit (e.g., C1, C2).
        # This allows us to skip headers like "3. CLAUSE LIST" or empty lines safely.
        if len(line) > 1 and line.startswith("C") and line[1].isdigit():
            # Example Line: "C1 | -1 2" or "C1 | [ -1, 2 ]"
            current_id = line.split()[0] # Take just "C1" (the first token)
            
            # Now we need to find the literals, which are usually enclosed in brackets [ ... ]
            # Brackets are on the same line.
            literals_str = line
            found_bracket = '[' in line and ']' in line
            j = i
            
            if found_bracket:
                # Use regex to find the content *inside* the first pair of brackets.
                # r'\[(.*?)\]' means: match '[' then capture any character non-greedily until ']'
                match = re.search(r'\[(.*?)\]', literals_str)
                lits = []
                if match:
                    content_inner = match.group(1)
                    # Handle both comma-separated "1, 2" and space-separated "1 2"
                    # replacing comma with space makes split() work for both.
                    parts = content_inner.replace(',', ' ').split()
                    for part in parts:
                        try:
                            lits.append(int(part))
                        except ValueError:
                            pass # Ignore non-integer tokens found inside brackets
                
                if lits: # Only add if we successfully parsed literals
                    clauses.append(Clause(current_id, lits))
                
                # Advance the main loop index 'i' to 'j' so we don't re-process these lines.
                i = j 
        i += 1
        
    return clauses

def parse_final_model(filepath):
    """
    Reads the final model file to get the variable assignments.
    
    Handles a couple of different usage formats we've seen (same line vs split lines).
    Returns a dict mapping var_id -> boolean.
    """
    model = {} 
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        return {}
        
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # We process any line that starts with a number (Variable ID).
        # We look for two formats:
        # 1. "1 | TRUE" (Single line)
        # 2. "1" on one line, followed by "TRUE" on a subsequent line.
        
        parts = line.split('|')
        first_part = parts[0].strip()
        
        if first_part.isdigit():
            var_id = int(first_part)
            # Default to False as per user request
            model[var_id] = False 
            
            # Check the same line for the value (User guaranteed assignment on same line)
            if len(parts) > 1:
                val_part = parts[1].upper()
                if "TRUE" in val_part:
                    model[var_id] = True
                elif "FALSE" in val_part:
                    model[var_id] = False
            
            # Note: We simply continue the loop. If we found the value on line i+1,
            # that line will be processed in the next iteration. However, since "TRUE"/"FALSE"
            # lines don't start with digits, they will simply be skipped by the `if first_part.isdigit()` check.
            pass
            
        i += 1
    return model

def parse_execution_trace(filepath):
    """
    Parses the execution trace log.
    
    Reconstructs the solver's steps (decisions, propagations, conflicts) so we can visualize the tree.
    Supports standard "DECIDE 1" format and the newer "BCP" logging format.
    """
    trace = []
    
    lines = []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        return []

    for i, line in enumerate(lines):
        line = line.strip()
        # Skip headers, metadata lines, or empty lines.
        # "DL" usually denotes a header start in some logs, but strictly we skip distinct header blocks.
        if not line or line.startswith("---") or line.startswith("STATUS") or line.startswith("DL") or line.startswith("CONFLICT_ID"):
            continue

        # Regex to find "L=value" (Literal assignment), e.g., L=1 or L=-5
        l_match = re.search(r'L=(-?\d+)', line)
        
        # --- CASE 1: DECISION ---
        if "DECIDE" in line:
            # A decision step: The solver guesses a value.
            if l_match:
                lit = int(l_match.group(1))
            else:
                # Fallback to old format: "DECIDE 1"
                parts = line.split()
                try:
                    # simplistic check: find "DECIDE" and take the next token
                    idx = -1
                    for k, p in enumerate(parts):
                        if "DECIDE" in p:
                            idx = k
                            break
                    if idx != -1 and idx + 1 < len(parts):
                        lit = int(parts[idx+1])
                    else:
                        continue
                except:
                    continue
            trace.append(TraceStep("DECIDE", lit))
            
        # --- CASE 2: UNIT PROPAGATION ---
        elif "UNIT" in line:
            # A forced assignment due to a Unit Clause.
            if l_match:
                lit = int(l_match.group(1))
            else:
                 # Fallback for "UNIT -3 C2"
                parts = line.split()
                try:
                    idx = -1
                    for k, p in enumerate(parts):
                        if "UNIT" in p:
                            idx = k
                            break
                    if idx != -1 and idx + 1 < len(parts):
                        lit = int(parts[idx+1])
                    else:
                        continue
                except:
                    continue
            
            # Extract Cause (The clause that forced this assignment)
            # Old Format: "UNIT -3 C2"
            # New Format: "[DL0] UNIT L=1 | C1"
            cause = None
            if '|' in line:
                # Check right side of pipe for "C..."
                right = line.split('|')[-1]
                c_match = re.search(r'(C\d+)', right)
                if c_match: cause = c_match.group(1)
            else:
                # Old format check: any token looking like C<digits>
                c_match = re.search(r'(C\d+)', line)
                if c_match: cause = c_match.group(1)

            trace.append(TraceStep("UNIT", lit, cause))
            
        # --- CASE 3: CONFLICT ---
        elif "CONFLICT" in line and "CONFLICT_ID" not in line:
            # A conflict occurred (empty clause derived or direct clause falsified).
            # Format: "[DL1] CONFLICT | Violation: C4"
            cause = None
            
            # Look for "Violation: C..."
            viol_match = re.search(r'Violation:\s*(C\d+)', line)
            
            if viol_match:
                cause = viol_match.group(1)
            else:
                # Fallback: legacy or unknown format
                pass
                
            trace.append(TraceStep("CONFLICT", 0, cause))
            
        # --- CASE 4: BACKTRACK ---
        elif "BACKTRACK" in line:
            # Solver backtracks to a previous level.
            trace.append(TraceStep("BACKTRACK", 0))

        # --- CASE 5: SATISFIED ---
        elif "SATISFIED" in line:
            # A clause is satisfied by the current assignment.
            # Format: "[DL1] SATISFIED | C1"
            cause = None
            c_match = re.search(r'(C\d+)', line)
            if c_match: cause = c_match.group(1)
            trace.append(TraceStep("SATISFIED", 0, cause))

        # --- CASE 6: ASSIGN ---
        elif "ASSIGN" in line and "UNASSIGNED" not in line:
            # Explicit assignment logging.
            # Format: "[DL1] ASSIGN L=-4 |"
            lit = 0
            if l_match:
                lit = int(l_match.group(1))
            
            # Check for redundancy with immediately preceding UNIT step
            is_redundant = False
            if trace:
                last_step = trace[-1]
                if last_step.step_type == "UNIT" and last_step.literal == lit:
                    is_redundant = True
            
            if not is_redundant:
                trace.append(TraceStep("ASSIGN", lit))

        # --- CASE 7: SHIFT ---
        elif "SHIFT" in line:
            # Watched literal shift.
            # Format: "[DL1] SHIFT L=3 | C6 3->4"
            lit = 0
            cause = None
            if l_match:
                lit = int(l_match.group(1))
            
            # Extract clause causing the shift
            c_match = re.search(r'(C\d+)', line)
            if c_match: cause = c_match.group(1)
            
            trace.append(TraceStep("SHIFT", lit, cause))

    return trace