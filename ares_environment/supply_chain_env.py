# ares_environment/supply_chain_env.py

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import simpy

from .simulation_nodes import Factory, Warehouse, Market, ship_goods

class SupplyChainEnv(gym.Env):
    """A custom Gymnasium environment for the ARES Supply Chain simulation."""
    metadata = {'render_modes': ['human']}

    def __init__(self, max_steps=365):
        super(SupplyChainEnv, self).__init__()
        
        self.max_steps = max_steps
        
        # Define the ACTION SPACE: what the AI can do.
        # Action: A single value representing the quantity to order from the factory.
        self.action_space = spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32)

        # Define the OBSERVATION SPACE: what the AI can see.
        # [factory_inventory, warehouse_inventory, market_demand]
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float32)

        # This will be initialized in reset()
        self.sim_env = None
        self.factory = None
        self.warehouse = None
        self.market = None
        
    def _get_obs(self):
        """Helper function to get the current state of the system."""
        return np.array([
            self.factory.inventory.level,
            self.warehouse.inventory.level,
            self.market.demand
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        """Resets the environment to an initial state."""
        super().reset(seed=seed)
        
        # Re-create the simulation environment for a clean slate
        self.sim_env = simpy.Environment()
        self.factory = Factory(self.sim_env, "Factory_EU")
        self.warehouse = Warehouse(self.sim_env, "Warehouse_US")
        self.market = Market(self.sim_env, "Market_NA", self.warehouse)
        
        # Give the factory some initial stock to get started
        self.sim_env.process(self.factory.produce(100))
        self.sim_env.run(until=1) # Run for a tiny step to process initial events
        
        observation = self._get_obs()
        info = {} # You can add extra info here for debugging
        return observation, info

    def step(self, action):
        """Executes one time step within the environment."""
        
        # --- 1. The AI's Action ---
        order_quantity = int(action[0])

        # Execute the action: Order production if there is enough inventory at the factory
        if order_quantity > 0 and self.factory.inventory.level >= order_quantity:
            # The factory produces and then ships the goods
            self.sim_env.process(self.factory.produce(order_quantity))
            self.sim_env.process(ship_goods(self.sim_env, self.factory, self.warehouse, order_quantity))
        
        # --- 2. Run the simulation for one step (e.g., one day) ---
        current_time = self.sim_env.now
        self.sim_env.run(until=current_time + 1)
        
        # --- 3. Calculate the Reward ---
        # The reward function is CRITICAL. It guides the AI's learning.
        reward = 0
        
        # Positive reward for revenue from sales
        reward += self.market.total_revenue 
        self.market.total_revenue = 0 # Reset for the next step

        # Negative reward (penalty) for holding inventory
        holding_cost = self.warehouse.inventory.level * 0.1 # Using a simplified cost
        reward -= holding_cost
        
        # Heavy penalty for unmet demand (lost sales)
        unmet_demand_penalty = self.market.unmet_demand * 5.0 
        reward -= unmet_demand_penalty

        # --- 4. Get the Next State and Other Info ---
        observation = self._get_obs()
        
        terminated = False # An episode is "terminated" if something catastrophic happens (e.g., bankruptcy)
        truncated = self.sim_env.now >= self.max_steps # "Truncated" means the time limit is reached

        info = {}

        return observation, reward, terminated, truncated, info