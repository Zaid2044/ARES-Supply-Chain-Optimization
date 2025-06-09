# main.py

from ares_environment.supply_chain_env import SupplyChainEnv
from stable_baselines3.common.env_checker import check_env

def test_environment():
    """Tests the custom Gymnasium environment."""
    
    print("--- Creating and Checking the Environment ---")
    env = SupplyChainEnv()
    
    # It's good practice to use the environment checker from Stable-Baselines3
    # to catch potential issues.
    try:
        check_env(env)
        print("\n✅ Environment check passed!")
    except Exception as e:
        print(f"\n❌ Environment check failed: {e}")
        return

    print("\n--- Testing a Short Episode with Random Actions ---")
    obs, info = env.reset()
    total_reward = 0
    
    for i in range(20): # Run for 20 steps
        action = env.action_space.sample() # Take a random action
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        print(f"\nStep {i+1}:")
        print(f"  Action Taken: Order {int(action[0])} units")
        print(f"  Observation: [Factory Inv: {int(obs[0])}, Whs Inv: {int(obs[1])}, Mkt Demand: {int(obs[2])}]")
        print(f"  Reward for this step: {reward:.2f}")

        if terminated or truncated:
            print("Episode finished.")
            break
            
    env.close()
    print(f"\n--- Test Complete ---")
    print(f"Total reward over 20 steps: {total_reward:.2f}")

if __name__ == "__main__":
    test_environment()