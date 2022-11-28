# Quantum compiler and pulse generation scheme    
The quantum compiler is responsible for converting a quantum algorithm represented as a string of gates operated on multiple qubits to a sequence of amplitude and phase modulated waveforms played on an arbitrary waveform generator. Spin qubits

                                 (1)x(1);(2)x(2);  


## Gate species and phase/amplitude relations      

## Calibration parameters and protocols   


## Channel groupings

## Phase increments and command table formulation    


##Worked example: controlled-Z gate calibration scheme
To convey a comprehensive understanding of the quantum compiler's inner-workings, let's attempt to generate the pulse sequences for the following quantum algorithm on a three-qubit array:



![Image](img/quantumcircuit_example.png)

This algorithm has three qubits denoted by \(Q_1, Q_2, Q_3 \). The \( \textbf{X} \) gates denote \( \pi \) rotations about the \(x\)-axis, the \( \sqrt{\textbf{X}} \) gates denote \( \frac{\pi}{2} \) rotations about the \(x\)-axis, and the  \( \textbf{Z}(\theta) \) gates are \( \theta\) rotations about the \(z\)-axis (will take \(\theta = \frac{\pi}{2}\) here). Pairs of connected filled circles represent controlled-Z (CZ) gates, which are implemented between qubits  \(Q_1-Q_2\) and \(Q_2-Q_3\) via barrier gates \(P_{12} (\tau)\) and \(P_{23} (\tau)\). This algorithm lays out a typical experiment for CZ-gate calibration, where parameters  \(P_{12} (\tau)\) and \(P_{23} (\tau)\) are swept over.   

Silospin would read in this algorithm in the form of a CSV file containing the following gate strings (all one line in the file). Let's store this in  `cz_calibration.csv` . Refer to the earlier section for definitions of each gate in this convention.  

    (1)xx(1)(2)xx(2)(3)xx(3);(7)p(7)(8)p(8);(1)x(1)(2)x(2)(3)x(3);
    (1)z90z(1)(2)z90z(2)(3)z90z(3);(1)x(1)(2)x(2)(3)x(3);

The
