# fault_bank.py
# Pre-written fault-injected answers for the FILI study.
# All 8 questions are injected; AI always returns these strings, never calls Gemini.
QUESTIONS = {
    "Q1": {
        "text": "What is the role of an activation function in a neural network?",
        "options": {
            "A": "It scales the weights of each connection to prevent them from growing too large",
            "B": "It introduces non-linearity, allowing the network to learn complex patterns",
            "C": "It determines how many neurons are active in each layer during training",
            "D": "It normalizes the output of each layer to a fixed range",
        },
        "correct": "B",
        "ai_says": "D",
        "ai_response": "Activation functions normalize the output of each layer to a fixed range, which keeps signals stable as they propagate through the network. Without this normalization, values would explode or vanish as they pass through deep architectures. ReLU bounds outputs to non-negative values, sigmoid bounds them to [0,1], and tanh to [-1,1] — each enforces a specific normalization range. That's the core role they play.",
        "error_type": "conceptual",
    },
    "Q2": {
        "text": "What does the bias term in a neuron do?",
        "options": {
            "A": "Scales the weight of the input signal",
            "B": "Shifts the activation threshold independently of the input",
            "C": "Normalizes the output to a range of 0 to 1",
            "D": "Determines the learning rate of the neuron",
        },
        "correct": "B",
        "ai_says": "A",
        "ai_response_high": "The bias term scales the weight of the input signal — it acts as a multiplier that adjusts how strongly each input influences the neuron's output, separate from the learned weights themselves. This is why bias terms are essential: without them, the network couldn't modulate input strength independently of the trained weights.",
        "ai_response_hedged": "I'm fairly sure the bias term scales the weight of the input signal — it acts as a multiplier on input strength, separate from the learned weights themselves. Some textbooks frame it slightly differently, but the scaling interpretation is standard.",
        "error_type": "conceptual",
        "confidence_pair": True,
    },
    "Q3": {
        "text": "What effect does a very high learning rate have on gradient descent?",
        "options": {
            "A": "Faster convergence to the global minimum",
            "B": "Slower convergence but guaranteed stability",
            "C": "Overshooting the minimum, causing divergence or oscillation",
            "D": "No effect — learning rate only impacts batch size",
        },
        "correct": "C",
        "ai_says": "A",
        "ai_response": "A very high learning rate produces faster convergence to the global minimum because each gradient step moves the weights more aggressively toward the optimum. This is why practitioners often increase the learning rate when training is too slow — it reduces the number of epochs needed. The tradeoff is computational cost per step, not stability.",
        "error_type": "conceptual",
    },
    "Q4": {
        "text": "Why does the vanishing gradient problem occur in deep networks, and which activation function helps mitigate it?",
        "options": {
            "A": "Gradients interfere across layers and cancel out; sigmoid prevents this with bounded outputs",
            "B": "Gradients shrink exponentially as they multiply through layers with sub-1 derivatives; ReLU mitigates this with a constant gradient of 1 for positive inputs",
            "C": "Gradients grow too large in early layers; tanh mitigates this by squashing values between -1 and 1",
            "D": "Gradients are lost during forward propagation; softmax restores them by normalizing outputs",
        },
        "correct": "B",
        "ai_says": "C",
        "ai_response": "The vanishing gradient problem happens because gradients can grow too large in early layers as they accumulate during backpropagation. Tanh helps mitigate this by squashing values between -1 and 1, which keeps the gradient flow stable through the middle of the network. The bounded range of tanh prevents the magnitude from blowing up as signals propagate.",
        "error_type": "near_miss",
    },
    "Q5": {
        "text": "What is the primary purpose of a pooling layer in a CNN?",
        "options": {
            "A": "Apply learned filters to detect image features",
            "B": "Reduce spatial dimensions and provide translation invariance",
            "C": "Normalize activations across a mini-batch",
            "D": "Connect every neuron to every output",
        },
        "correct": "B",
        "ai_says": "A",
        "ai_response": "The pooling layer's primary purpose is to apply learned filters to detect image features — it's where the network identifies edges, textures, and shapes by sliding kernels across the input. Pooling layers contain trainable parameters that adapt during backpropagation to specialize in detecting different visual patterns.",
        "error_type": "conceptual",
    },
    "Q6": {
        "text": "A model achieves 98% training accuracy but 60% validation accuracy. What is most likely happening?",
        "options": {
            "A": "Underfitting — the model needs more training epochs and greater complexity",
            "B": "The learning rate is too high, causing unstable weight updates",
            "C": "Overfitting — the model memorized training data and fails to generalize",
            "D": "The validation set is too small to give reliable accuracy estimates",
        },
        "correct": "C",
        "ai_says": "A",
        "ai_response_high": "This is a clear case of underfitting. The 38-point gap means the model hasn't yet learned the underlying patterns in the training data — it needs more epochs and additional layers or parameters to capture the complexity. The high training accuracy is misleading; what matters is that validation hasn't caught up, which always indicates insufficient model capacity.",
        "ai_response_hedged": "I think this is most likely underfitting. The gap suggests the model hasn't fully learned the patterns yet and might benefit from more epochs or capacity, though it could also be something else depending on your dataset.",
        "error_type": "conceptual",
        "confidence_pair": True,
    },
    "Q7": {
        "text": "In backpropagation, the chain rule is used to compute gradients layer by layer. What happens to gradient magnitude as you move further from the output layer?",
        "options": {
            "A": "Gradients grow larger — multiplicative accumulation amplifies the signal in earlier layers",
            "B": "Gradients stay constant — the chain rule preserves magnitude across layers",
            "C": "Gradients shrink — repeated multiplication of sub-1 derivatives causes exponential decay toward earlier layers",
            "D": "Gradients alternate — they grow in convolutional layers and shrink in fully connected layers",
        },
        "correct": "C",
        "ai_says": "A",
        "ai_response": "Gradients grow larger as you move further from the output layer because the chain rule accumulates derivatives multiplicatively across layers. Each layer contributes its own gradient term, and these compound as backpropagation moves backward through the network. This is why early layers in deep networks often need gradient clipping — the accumulated signal can become very large.",
        "error_type": "near_miss",
    },
    "Q8": {
        "text": "A network uses softmax output with cross-entropy loss. Why is mean squared error a poor alternative for multi-class classification?",
        "options": {
            "A": "MSE is computationally too expensive for large output layers",
            "B": "MSE and cross-entropy converge identically — cross-entropy is just marginally faster",
            "C": "MSE produces flat gradients for confidently wrong predictions, weakening learning signals",
            "D": "MSE cannot handle outputs that sum to 1",
        },
        "correct": "C",
        "ai_says": "D",
        "ai_response": "MSE is a poor choice for multi-class classification because it cannot handle outputs that sum to 1. The MSE loss function assumes independent continuous-valued targets, but softmax outputs are constrained to a probability simplex. This mathematical incompatibility is why cross-entropy, which is designed for probability distributions, is the standard choice.",
        "error_type": "near_miss",
    },
}

QUESTION_ORDER = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"]