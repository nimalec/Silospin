import numpy as np

def make_rabisweep_file(qubits, start_tau, end_tau, npoints, amplitude, filepath):
    tau_grid = np.linspace(start_tau, end_tau, npoints)
    amp_str = str(amplitude)
    file_str = ""
    for t in tau_grid:
        tau_str = str(t)
        gate_str = f"{amp_str}*X[{tau_str}&0&0]"
        temp_line = ""
        for q in qubits:
            gate_line = f"({str(q)}){gate_str}({str(q)});"
            temp_line += gate_line
        temp_line = temp_line+'\n'
        file_str += temp_line

    with open(filepath, 'w') as f:
        f.write(file_str)
    f.close()
