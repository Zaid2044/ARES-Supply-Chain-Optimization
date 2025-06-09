import numpy as np
from stable_baselines3 import PPO
from ares_environment.supply_chain_env import SupplyChainEnv

# --- 1. Load the environment and the trained model ---
env = SupplyChainEnv()
model = PPO.load("trained_models/ppo_ares_agent.zip", env=env)

# --- 2. Define a "Dumb" Baseline Agent ---
# This agent will represent a simple, non-learning strategy.
# Our dumb agent's policy is to always try and order 30 units, a reasonable constant.
def baseline_agent_action(obs):
    # We need to scale our '30' to the [-1, 1] action space.
    # The reverse of our rescaling formula: (action_value * 2 / max_quantity) - 1
    scaled_action = (30 * 2 / env.max_order_quantity) - 1
    return np.array([scaled_action])

# --- 3. Run Evaluation Episodes ---
def run_episode(agent, is_baseline=False):
    obs, info = env.reset()
    total_reward = 0
    done = False
    
    print(f"\n--- Running Episode for {'Baseline Agent' if is_baseline else 'Trained PPO Agent'} ---")
    
    while not done:
        if is_baseline:
            action = baseline_agent_action(obs)
        else:
            action, _states = agent.predict(obs, deterministic=True)
        
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        done = terminated or truncated
        
    print(f"--- Episode Complete. Total Reward: {total_reward:.2f} ---")
    return total_reward

# --- 4. Compare Performance ---
num_episodes = 5
ppo_rewards = []
baseline_rewards = []

for i in range(num_episodes):
    print(f"\n--- Evaluation Round {i+1}/{num_episodes} ---")
    ppo_rewards.append(run_episode(model))
    baseline_rewards.append(run_episode(None, is_baseline=True))

env.close()

# --- 5. Print Final Results ---
print("\n\n--- EVALUATION SUMMARY ---")
print(f"Average Reward for Trained PPO Agent: {np.mean(ppo_rewards):.2f}")
print(f"Average Reward for Baseline Agent:   {np.mean(baseline_rewards):.2f}")
print("--------------------------")

if np.mean(ppo_rewards) > np.mean(baseline_rewards):
    print("✅ SUCCESS: The trained agent outperformed the baseline agent!")
else:
    print("❌ NOTE: The trained agent did not outperform the baseline. Consider more training or hyperparameter tuning.")