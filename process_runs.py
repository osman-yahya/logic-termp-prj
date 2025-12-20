import os
import glob
from parser import parse_initial_cnf, parse_final_model, parse_execution_trace
from visualizer import generate_row_form, generate_inference_form, generate_tree_form

def process_single_run(run_dir, output_file):
    """
    Handles one run directory (e.g., sample_runs/1).
    
    Parses the CNF, model, and trace files, then generates all the visualizations
    (Row, Inference, Tree forms) and dumps them into the output file.
    """
    print(f"Processing {run_dir} -> {output_file}")
    
    cnf_path = os.path.join(run_dir, "initial_cnf.txt")
    model_path = os.path.join(run_dir, "final_model.txt")
    
    # --- Step 1: Parse CNF and Final Model ---
    clauses = parse_initial_cnf(cnf_path)
    model = parse_final_model(model_path)
    
    # Determine if the run resulted in SAT by reading the model file header
    is_sat = False
    try:
        with open(model_path, "r") as f:
            content = f.read()
            if "STATUS: SAT" in content:
                is_sat = True
    except:
        pass

    # --- Step 2: Merge Execution Trace Files ---
    # Sometimes distributed solving produces multiple trace files (execution_trace_0.txt, _1, etc.).
    # We need to find them all and stitch them together sequentially.
    
    trace_files = glob.glob(os.path.join(run_dir, "execution_trace_*.txt"))
    
    # Helper to sort files numerically by the suffix X in execution_trace_X.txt
    def get_suffix(path):
        base = os.path.basename(path)
        name = os.path.splitext(base)[0] # remove .txt
        try:
            # Split "execution_trace_5" -> ["execution", "trace", "5"] -> 5
            num = int(name.split('_')[-1])
            return num
        except:
            return 999
            
    trace_files.sort(key=get_suffix)
    
    # Merge contents into a temporary file
    merged_trace_path = os.path.join(run_dir, "merged_trace.tmp")
    with open(merged_trace_path, "w") as outfile:
        for fname in trace_files:
            with open(fname, "r") as infile:
                outfile.write(infile.read())
                outfile.write("\n") # Ensure newline separation between files
    
    # --- Step 3: Parse the Merged Trace ---
    trace = parse_execution_trace(merged_trace_path)
    
    # --- Step 4: Logic Repair ---
    # User requested to disable trace repair logic.
    pass # trace = repair_trace(clauses, trace, model)

    # --- Step 5: Generate Output Visualizations ---
    output_text = []
    
    # 5.1. Row Form: Truth Table style
    output_text.append(generate_row_form(clauses, model))
    output_text.append("\n" + "="*40 + "\n")
    
    # 5.2. Inference Form: Simplified Clause List progression
    output_text.append(generate_inference_form(clauses, trace))
    output_text.append("\n" + "="*40 + "\n")
    
    # 5.3. Tree Form: ASCII Tree
    output_text.append(generate_tree_form(trace, is_sat=is_sat))
    
    # --- Step 6: Save Results ---
    final_content = "\n".join(output_text)
    with open(output_file, "w") as f:
        f.write(final_content)
        
    # Valid Cleanup of the temp file
    if os.path.exists(merged_trace_path):
        os.remove(merged_trace_path)

def main():
    """
    Loops through the example runs (1-7) and processes them.
    Useful for batch processing everything at once.
    """
    base_dir = "sample_runs"
    output_dir = "outputs"
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"--- Starting Batch Processing ---")
    print(f"Input Directory: {base_dir}")
    print(f"Output Directory: {output_dir}")
    
    # Process folders 1 to 7 
    for i in range(1, 8):
        run_dir = os.path.join(base_dir, str(i))
        
        # Only process if the directory actually exists
        if os.path.exists(run_dir):
            output_file = os.path.join(output_dir, f"output_{i}.txt")
            try:
                process_single_run(run_dir, output_file)
            except Exception as e:
                print(f"Failed to process {run_dir}: {e}")
                # print full traceback for debugging
                import traceback
                traceback.print_exc()
        else:
             print(f"Skipping {run_dir} (Not found)")

    print("--- Batch Processing Complete ---")

if __name__ == "__main__":
    main()
