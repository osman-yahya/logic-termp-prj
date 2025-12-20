class Clause:
    """
    Simple wrapper for a CNF clause.
    
    Basically a list of literals where integers are used for variables.
    Positive ints are just the variable (e.g., 2), negative are NOT variable (e.g., -2).
    The c_id is just for logging/debugging so we can track which clause caused what.
    """
    def __init__(self, c_id, literals):
        self.c_id = c_id          # "C1", "C2", etc
        self.literals = literals  # [-1, 2] means (NOT 1 OR 2)

    def __repr__(self):
        return f"{self.c_id}: {self.literals}"

class TraceStep:
    """
    One step in the solver's execution trace.
    
    We use this to replay what the solver did (decisions, propagations, conflicts).
    """
    def __init__(self, step_type, literal=None, cause=None):
        self.step_type = step_type  # DECIDE, UNIT, CONFLICT, etc.
        self.literal = literal      # Variable involved (e.g., 2 or -3)
        self.cause = cause          # Clause ID that forced this step (if applicable)

    def __repr__(self):
        return f"[{self.step_type}] L={self.literal}, Cause={self.cause}"