# ares_environment/simulation_nodes.py

import simpy
import random # We need random for demand

# --- Constants ---
FACTORY_PROCESSING_TIME = 2
WAREHOUSE_HOLDING_COST = 0.1
SHIPPING_TIME = 5
MARKET_DEMAND_INTERVAL = 1 # A market demands goods every 1 time unit (day)
REVENUE_PER_UNIT = 10.0 # Revenue for selling one unit

class Factory:
    """Represents a production facility."""
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.inventory = simpy.Container(env, capacity=1000, init=0)
        # print(f"{self.env.now:.2f}: Factory '{self.name}' created.") # We'll quiet this for AI training

    def produce(self, quantity):
        """Simulates the production of goods."""
        # print(f"{self.env.now:.2f}: '{self.name}' starting production of {quantity} units.")
        yield self.env.timeout(FACTORY_PROCESSING_TIME * quantity)
        yield self.inventory.put(quantity)
        # print(f"{self.env.now:.2f}: '{self.name}' finished production. Current inventory: {self.inventory.level}")

class Warehouse:
    """Represents a storage and distribution center."""
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.inventory = simpy.Container(env, capacity=5000, init=0)
        # print(f"{self.env.now:.2f}: Warehouse '{self.name}' created.")

    def charge_holding_cost(self):
        """A process that continuously charges for holding inventory."""
        while True:
            cost = self.inventory.level * WAREHOUSE_HOLDING_COST
            yield self.env.timeout(1)

# --- NEW CLASS ---
class Market:
    """Represents an end market with customer demand."""
    def __init__(self, env, name, associated_warehouse):
        self.env = env
        self.name = name
        self.associated_warehouse = associated_warehouse
        self.demand = 0
        self.unmet_demand = 0
        self.total_revenue = 0
        self.env.process(self.demand_process())
        # print(f"{self.env.now:.2f}: Market '{self.name}' created, supplied by '{associated_warehouse.name}'.")

    def demand_process(self):
        """A process that generates customer demand periodically."""
        while True:
            # Generate random demand for this step
            self.demand = random.randint(10, 40)
            # print(f"{self.env.now:.2f}: Market '{self.name}' has new demand of {self.demand} units.")
            
            # Try to fulfill demand from the warehouse
            units_available = self.associated_warehouse.inventory.level
            units_to_sell = min(self.demand, units_available)
            
            if units_to_sell > 0:
                # print(f"{self.env.now:.2f}: Fulfilling {units_to_sell} units for Market '{self.name}'.")
                yield self.associated_warehouse.inventory.get(units_to_sell)
                self.total_revenue += units_to_sell * REVENUE_PER_UNIT

            # Track unmet demand
            self.unmet_demand = self.demand - units_to_sell
            if self.unmet_demand > 0:
                # print(f"{self.env.now:.2f}: WARNING - Market '{self.name}' has unmet demand of {self.unmet_demand} units.")
                 pass # We don't want to print this during training

            yield self.env.timeout(MARKET_DEMAND_INTERVAL)

def ship_goods(env, from_location, to_location, quantity):
    """Simulates shipping goods between two locations."""
    # print(f"{env.now:.2f}: Shipping {quantity} units from '{from_location.name}' to '{to_location.name}'.")
    yield from_location.inventory.get(quantity)
    yield env.timeout(SHIPPING_TIME)
    yield to_location.inventory.put(quantity)
    # print(f"{env.now:.2f}: Shipment arrived at '{to_location.name}'. Its inventory is now {to_location.inventory.level}.")