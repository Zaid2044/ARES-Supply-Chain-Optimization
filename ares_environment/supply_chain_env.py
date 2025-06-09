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
        self.max_order_quantity = 100 # The max we can order in one go
        
        # <<< CHANGE 1: Normalizing the Action Space >>>
        # The agent now picks a value between -1 and 1.
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)

        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float32)

        self.sim_env = None
        self.factory = None
        self.warehouse = None
        self.market = None
        
    def _get_obs(self):
        return np.array([
            self.factory.inventory.level,
            self.warehouse.inventory.level,
            self.market.demand
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.sim_env = simpy.Environment()
        self.factory = Factory(self.sim_env, "Factory_EU")
        self.warehouse = Warehouse(self.sim_env, "Warehouse_US")
        self.market = Market(self.sim_env, "Market_NA", self.warehouse)
        
        self.sim_env.process(self.factory.produce(100))
        self.sim_env.run(until=1)
        
        observation = self._get_obs()
        info = {}
        return observation, info

    def step(self, action):
        
        # <<< CHANGE 2: Rescaling the Action >>>
        # We rescale the agent's action from [-1, 1] to our desired range [0, max_order_quantity].
        # (action[0] + 1) / 2 scales it from [0, 1].
        # Then we multiply by our max order size.
        order_quantity = int(((action[0] + 1) / 2) * self.max_order_quantity)
        
        reward = 0

        # <<< CHANGE 3: Reward Shaping >>>
        # Give an immediate penalty if the agent tries to order more than is available.
        if order_quantity > self.factory.inventory.level:
            reward -= 50  # Immediate penalty for a bad decision
            # Don't process the order
        elif order_quantity > 0:
            # The factory produces and then ships the goods
            self.sim_env.process(self.factory.produce(order_quantity))
            self.sim_env.process(ship_goods(self.sim_env, self.factory, self.warehouse, order_quantity))
        
        current_time = self.sim_env.now
        self.sim_env.run(until=current_time + 1)
        
        # Main rewards (delayed)
        reward += self.market.total_revenue 
        self.market.total_revenue = 0

        holding_cost = self.warehouse.inventory.level * 0.1
        reward -= holding_cost
        
        unmet_demand_penalty = self.market.unmet_demand * 5.0 
        reward -= unmet_demand_penalty

        observation = self._get_obs()
        terminated = False
        truncated = self.sim_env.now >= self.max_steps
        info = {}

        return observation, reward, terminated, truncated, info