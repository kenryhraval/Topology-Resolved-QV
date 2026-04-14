# Complete QV Project

## `1_Extract_Calibration.ipynb` 
- extracts calibration data from IBM Quantum backends and stores it locally (uses environment `runtime.txt`)
- stores snapshots under: `calibrations/<backend_name>/<timestamp>.json`
- this notebook only needs to be run when updating calibration data


## `2_Run_Experiment.ipynb` 
- runs Quantum Volume experiments using classical simulation with GPU acceleration (uses environment `gpu.txt`)
- uses the GPU environment with: `qiskit-aer-gpu`, CUDA-enabled Aer simulation
- enumerates connected qubit n-tuples from the device coupling graph and calculates QV for each


## `3_Analyze_Results.ipynb` 


## Quantum Volume Methodology

Quantum Volume (QV) is evaluated following the standard definition:

- Circuits are square, with width = depth as the number of qubits `m`.
- For each `m`, multiple random QV circuits are generated and executed. A run is considered successful if fallowing conditions are met: mean heavy-output probability $HOP > 2/3$ and statistical confidence $≥ 97\%$. [4]

## Similiar Scientific Studies
[1] [Quantum Volume in Practice: What Users Can Expect from NISQ Devices](https://arxiv.org/pdf/2203.03816) 

[2] [Validating quantum computers using randomized model circuits](https://arxiv.org/pdf/1811.12926)

[3] [A volumetric framework for quantum computer benchmarks](https://arxiv.org/pdf/1904.05546)

[4] [Quantum Benchmark Zoo](https://quantumbenchmarkzoo.org/)

[5] [How are we benchmarking our quantum computers today?](https://www.ibm.com/quantum/blog/quantum-metric-layer-fidelity)

Providing a qubit subset choice for the logical to physical qubit mapping allows us to characterize the regions
of the backend (i.e. the qubit and 2-qubit interacting gates) that give the highest fidelity QV results. Not
all qubits and connections on a NISQ device are of the same quality; thus even if a device passes a QV test,
such success often relies on selecting a good qubit subset, which is not trivial to identify. This fact slightly
compromises the original intuitive appeal of the QV measure: passing a QV $2^m$ test does not necessarily
imply that the device will generally handle any circuit of depth and width m well because it may not start
with a good qubit subset choice. [1] 


What we’re doing — enumerating subsets — is actually the missing step that vendors do internally. IBM explicitly notes that QV usually highlights a subset of the best-performing qubits on a device rather than representing the entire processor. [5]
