def get_var_name(var_id):
    """Maps custom var IDs to letters A, B, C..."""
    return chr(65 + var_id - 1)

def get_literal_str(lit):
    """e.g. 1 -> 'A', -1 -> '-A'"""
    var = abs(lit)
    name = get_var_name(var)
    return name if lit > 0 else f"-{name}"

def get_assignment_str(lit):
    """e.g. 1 -> 'A = 1', -1 -> 'A = 0'"""
    var = abs(lit)
    name = get_var_name(var)
    val = 1 if lit > 0 else 0
    return f"{name} = {val}"

def generate_row_form(clauses, model):
    """
    Generates the 'Row Form' visualization (Truth Table style).
    
    Shows each clause and how it evaluates under the final model.
    """
    output = []
    
    
    # Header: Model Assignment
    if not model:
        return "Model: UNSAT (No satisfiable assignment found)\n\n(Row form skipped for UNSAT result)"
        
    sorted_vars = sorted(model.keys())
    model_parts = [f"{get_var_name(v)}={1 if model[v] else 0}" for v in sorted_vars]
    output.append(f"Model: {', '.join(model_parts)}")
    output.append("")
    
    # Identify all variables involved to create a consistent column structure
    all_vars = sorted(list(set(abs(l) for c in clauses for l in c.literals)))
    
    for c in clauses:
        # Part A: Variable Indicators
        signs = []
        for v in all_vars:
            found = False
            sign = " "
            for lit in c.literals:
                if abs(lit) == v:
                    sign = "+" if lit > 0 else "-" # + for Positive literal, - for Negative
                    found = True
                    break
            signs.append(f"{sign:^3}") # Center in 3 chars for spacing
        
        signs_str = "".join(signs)
        
        # Part B: Logical Evaluation
        math_parts = []
        total = 0
        
        # Sort literals by variable ID to align with columns (Part A)
        sorted_lits = sorted(c.literals, key=abs)
        
        for l in sorted_lits:
            var = abs(l)
            val = model.get(var, False) # Default to false if missing
            
            # Check satisfaction
            sat = (l > 0 and val) or (l < 0 and not val)
            
            int_val = 1 if sat else 0
            math_parts.append(str(int_val))
            total += int_val
            
        math_str = " + ".join(math_parts) # e.g., "1 + 0 + 1"
        
        # Combine into Final Row string
        # C1 |  +     -  | 1 + 0 = 1
        # The sum is capped at 1 because it's logical OR (1+1=1).
        display_total = 1 if total > 0 else 0
        output.append(f"{c.c_id:<4}| {signs_str} | {math_str} = {display_total}")
        
    return "\n".join(output)

def generate_inference_form(clauses, trace):
    """
    Simulates the simplification of clauses step-by-step.
    
    Shows what the clause database looks like after each decision/unit propagation.
    Satisfied clauses are hidden, leaving only the "residual" problem.
    """
    output = [] 
    
    # Track current assignments to compute simplified clauses
    active_assignments = {} # var_id -> boolean value
    levels = [] # Stack of decision levels
    
    # Print the current state of all clauses
    def print_state():
        block = []
        for c in clauses:
            # Check the status of this clause under current assignments
            is_satisfied = False
            remaining = []
            
            for lit in c.literals:
                var = abs(lit)
                val = active_assignments.get(var)
                
                if val is not None:
                    # If variable is assigned, check if it satisfies the literal
                    if (val and lit > 0) or (not val and lit < 0):
                        is_satisfied = True
                        break
                    # If literal is falsified, it vanishes from the clause.
                else:
                    # Unassigned literals remain
                    remaining.append(get_literal_str(lit))
            
            # Formate line
            if not is_satisfied:
                if not remaining:
                    # Conflict: Not satisfied and no literals remain
                    block.append(f"{c.c_id} | 0 | Conflict")
                else:
                    # Partial clause
                    block.append(f"{c.c_id} | {' + '.join(remaining)}")
            # Satisfied clauses are hidden
        return block

    # Initial State
    output.extend(print_state())

    for step in trace:
        step_type = step.step_type.upper()
        
        # DECISION
        if step_type == "DECIDE":
            output.append(f"---------- Decision L={step.literal}")
            var = abs(step.literal)
            val = (step.literal > 0)
            
            active_assignments[var] = val
            levels.append([var]) # New level
            output.extend(print_state())
            
        # UNIT / ASSIGN
        elif step_type == "UNIT" or step_type == "ASSIGN":
            label = "Unit" if step_type == "UNIT" else "Assign"
            output.append(f"---------- {label} L={step.literal}")
            
            var = abs(step.literal)
            val = (step.literal > 0)
            
            active_assignments[var] = val
            if levels:
                levels[-1].append(var)
            else:
                levels.append([var])
            output.extend(print_state())
            
        # BACKTRACK
        elif step_type == "BACKTRACK":
            if levels:
                popped = levels.pop()
                for v in popped:
                    if v in active_assignments:
                        del active_assignments[v]
            # No state print typically for backtrack itself
        
        # SHIFT
        elif step_type == "SHIFT":
            pass 

        # SATISFIED
        elif "SATISFIED" in step_type:
            pass

        # CONFLICT
        elif step_type == "CONFLICT":
            pass 

    # Check final satisfaction state
    all_satisfied = True
    for c in clauses:
        is_sat = False
        for lit in c.literals:
            var = abs(lit)
            val = active_assignments.get(var)
            if val is not None:
                if (val and lit > 0) or (not val and lit < 0):
                    is_sat = True
                    break
        if not is_sat:
            all_satisfied = False
            break
            
    if all_satisfied:
        output.append("Satisfied")

    return "\n".join(output)

def generate_tree_form(trace, is_sat=False):
    """
    Builds an ASCII tree structure to visualize the search process.
    Branches are decisions, leaves are conflicts or saturation.
    matches the requested diagonal line style.
    """
    
    # 1. Build tree structure
    class Node:
        def __init__(self, text):
            self.text = text
            self.children = []

    root = Node("Root")
    stack = [root]

    for step in trace:
        step_type = step.step_type.upper()
        
        if step_type == "DECIDE":
            node = Node(f"Decide {get_assignment_str(step.literal)}")
            stack[-1].children.append(node)
            stack.append(node)
            
        elif step_type == "BACKTRACK":
            if len(stack) > 1:
                stack.pop()
                
        elif step_type in ["UNIT", "ASSIGN", "CONFLICT"]:
            label = step_type.capitalize()
            if step_type == "UNIT" or step_type == "ASSIGN":
                text = f"{label} {get_assignment_str(step.literal)}"
            else:
                text = "Conflict!"
            
            node = Node(text)
            stack[-1].children.append(node)

        # IGNORE SHIFT
    
    # Check satisfaction
    if is_sat:
        active = stack[-1]
        if not active.children or "Satisfied" not in active.children[-1].text:
             active.children.append(Node("Satisfied!"))

    # 2. Draw the tree
    lines = []
    
    def draw(node, prefix, is_root=False):
        if is_root:
            lines.append(node.text)
            if node.children:
                lines.append("|")
        else:
            pass
    
    def print_tree(node, prefix, is_last_child):
        # Print the node itself
        connector = "|----- "
        lines.append(prefix + connector + node.text)
        
        # Now process children
        if node.children:
            # Determine the prefix for children
            child_prefix_segment = "         " if is_last_child else "|        "
            child_prefix = prefix + child_prefix_segment
            
            # Draw "Spacer" line leading to first child
            lines.append(child_prefix + "|")
            
            num_children = len(node.children)
            for i, child in enumerate(node.children):
                is_last = (i == num_children - 1)
                if i > 0:
                    lines.append(child_prefix + "|")
                print_tree(child, child_prefix, is_last)

    # Start with Root
    lines.append(root.text)
    if root.children:
        lines.append("|")
        
        for i, child in enumerate(root.children):
            is_last = (i == len(root.children) - 1)
            if i > 0:
                lines.append("|")
            print_tree(child, "", is_last)

    return "\n".join(lines)

