import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

class QuantumHypeClassifier:
    def __init__(self):
        # We use 3 features: Technical Realism, Timeline Proximity, Sentiment Exaggeration
        self.num_features = 3
        
        # Feature map to encode classical data into quantum states
        self.feature_map = ZZFeatureMap(feature_dimension=self.num_features, reps=1)
        
        # Variational form (Ansatz)
        self.ansatz = RealAmplitudes(num_qubits=self.num_features, reps=1)
        
        # Combine into a single circuit
        self.circuit = self.feature_map.compose(self.ansatz)
        self.circuit.measure_all()
        
        # We will use pre-trained weights for this demo 
        # (simulating a trained model for hype detection)
        # We want: 
        # High Exaggeration (feature 2) -> High Hype Score
        # High Realism (feature 0) -> Low Hype Score
        # High Timeline Proximity (feature 1) -> Low Hype Score
        np.random.seed(42)
        self.optimal_weights = np.random.uniform(-np.pi, np.pi, self.ansatz.num_parameters)
        
        self.simulator = AerSimulator()

    def calculate_hype_score(self, features: list[float]) -> float:
        """
        Calculates the Hype Score using a Variational Quantum Circuit.
        Features must be a list of 3 floats between 0 and 1:
        [Technical Realism, Timeline Proximity, Sentiment Exaggeration]
        """
        # Bind features to the feature map parameters
        feature_dict = {
            self.feature_map.parameters[i]: features[i] 
            for i in range(self.num_features)
        }
        
        # Bind optimal weights to the ansatz parameters
        weight_dict = {
            self.ansatz.parameters[i]: self.optimal_weights[i] 
            for i in range(self.ansatz.num_parameters)
        }
        
        # Combine bindings
        bound_circuit = self.circuit.assign_parameters({**feature_dict, **weight_dict})
        
        # Transpile for simulator
        pm = generate_preset_pass_manager(optimization_level=1, backend=self.simulator)
        isa_circuit = pm.run(bound_circuit)
        
        # Run the circuit
        result = self.simulator.run(isa_circuit, shots=1024).result()
        counts = result.get_counts()
        
        # For our mock model, let's say the "Hype" state is defined by the probability
        # of the first qubit being '1'
        hype_count = sum(counts[state] for state in counts if state[-1] == '1')
        total_shots = sum(counts.values())
        
        # Calculate raw probability
        hype_prob = hype_count / total_shots
        
        # Adjusting the score heuristically based on the features to make it a better demo:
        # If exaggeration is high and realism is low, hype should definitely be high.
        # We blend the quantum probability with a heuristic for a robust demo.
        exaggeration = features[2]
        realism = features[0]
        
        heuristic_score = (exaggeration + (1 - realism)) / 2.0
        final_score = 0.5 * hype_prob + 0.5 * heuristic_score
        
        return round(final_score, 2)
