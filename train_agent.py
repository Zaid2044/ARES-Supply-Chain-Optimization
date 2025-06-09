import os
from datetime import datetime
from stable_baselines3 import PPO
from ares_environment.supply_chain_env import SupplyChainEnv

# --- 1. Configuration ---
# Create directories to save logs and models
log_dir = f"logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
model_dir = "trained_models"
os.makedirs(log_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)

# --- 2. Create the Environment ---
# The same environment we tested before
env = SupplyChainEnv()
env.reset()

# --- 3. Instantiate the AI Agent ---
# We are using the PPO (Proximal Policy Optimization) algorithm.
# It's a robust and popular choice for this kind of problem.
# "MlpPolicy" means the agent will use a standard neural network (Multi-Layer Perceptron).
# We pass our environment to the agent and enable the TensorBoard logger.
model = PPO(
    "MlpPolicy",
    env,
    verbose=1, # This will print training progress
    tensorboard_log=log_dir
)

# --- 4. Train the Agent ---
# The number of timesteps is how long the agent will train.
# 10,000 is a very short run for initial testing. A real training run would be 1M+.
TIMESTEPS_TO_TRAIN = 50000 

print("--- Starting Agent Training (v2) ---")
model.learn(
    total_timesteps=TIMESTEPS_TO_TRAIN,
    reset_num_timesteps=False, # Important for continuous training
    tb_log_name="PPO_ARES_v1" # The name for our TensorBoard log
)
print("--- Agent Training Complete ---")

# --- 5. Save the Trained Model ---
# We save the model's "brain" so we can use it later without retraining.
model_path = os.path.join(model_dir, "ppo_ares_agent.zip")
model.save(model_path)
print(f"✅ Model saved to: {model_path}")

# --- 6. (Optional) View the Training Logs ---
# To see the beautiful graphs of your agent learning, run this in a SEPARATE terminal:
# tensorboard --logdir=logs/
print("\nTo view training results, run the following in a new terminal:")
print(f"tensorboard --logdir={log_dir}")

env.close()