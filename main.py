from parser import parse_initial_cnf, parse_final_model, parse_execution_trace
from visualizer import generate_row_form, generate_inference_form, generate_tree_form

def main():
    # 1. Parsing
    print("Parsing files...")
    clauses = parse_initial_cnf("pdf_example/initial_cnf.txt")
    model = parse_final_model("pdf_example/final_model.txt")
    trace = parse_execution_trace("pdf_example/execution_trace.txt")
    
    # REPAIR TRACE
    # trace = repair_trace(clauses, trace, model) # Disabled by user request

    # Determine Status from Model file header
    is_sat = False
    try:
        with open("pdf_example/final_model.txt", "r") as f:
            first_line = f.readline()
            if "SAT" in first_line and "UNSAT" not in first_line:
                is_sat = True
    except:
        pass

    # 2. Generate Strings
    output_text = []
    
    # Row Form
    output_text.append(generate_row_form(clauses, model))
    output_text.append("\n" + "="*40 + "\n")
    
    # Inference Form
    output_text.append(generate_inference_form(clauses, trace))
    output_text.append("\n" + "="*40 + "\n")
    
    # Tree Form
    output_text.append(generate_tree_form(trace, is_sat=is_sat))

    # 3. Save results
    final_content = "\n".join(output_text)
    with open("pdf_example/visualizer_output.txt", "w") as f:
        f.write(final_content)
    
    print("Success! Output saved to 'pdf_example/visualizer_output.txt'")
    print(final_content) # Print to console so we can see it right away

if __name__ == "__main__":
    main()