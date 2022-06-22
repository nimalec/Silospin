import pandas as pd

def read_qubit_paramater_file(file_path):
    qubit_parameters = pd.read_csv(file_path)
    return qubit_parameters.to_dict

def write_qubit_parameter_file(qubit_parameters, file_path):
    param_df = pd.DataFrame.from_dict(qubit_parameters)
    param_df.to_csv(file_path)
