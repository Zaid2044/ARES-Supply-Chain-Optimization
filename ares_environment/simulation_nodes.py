import simpy

# --- Constants ---

FACTORY_PROCESSING_TIME = 2  
WAREHOUSE_HOLDING_COST = 0.1 
SHIPPING_TIME = 5            

class Factory:
    """Represents a production facility."""
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.inventory = simpy.Container(env, capacity=1000, init=0) 
        print(f"{self.env.now:.2f}: Factory '{self.name}' created.")

    def produce(self, quantity):
        """Simulates the production of goods."""
        print(f"{self.env.now:.2f}: '{self.name}' starting production of {quantity} units.")
        yield self.env.timeout(FACTORY_PROCESSING_TIME * quantity)
        yield self.inventory.put(quantity)
        print(f"{self.env.now:.2f}: '{self.name}' finished production. Current inventory: {self.inventory.level}")

class Warehouse:
    """Represents a storage and distribution center."""
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.inventory = simpy.Container(env, capacity=5000, init=0)
        print(f"{self.env.now:.2f}: Warehouse '{self.name}' created.")

    def charge_holding_cost(self):
        """A process that continuously charges for holding inventory."""
        while True:
            cost = self.inventory.level * WAREHOUSE_HOLDING_COST
            yield self.env.timeout(1)

def ship_goods(self,env, from_location, to_location, quantity):
    """Simulates shipping goods between two locations."""
    print(f"{self.env.now:.2f}: Shipping {quantity} units from '{from_location.name}' to '{to_location.name}'.")
    yield from_location.inventory.get(quantity)
    yield env.timeout(SHIPPING_TIME)
    yield to_location.inventory.put(quantity)
    print(f"{self.env.now:.2f}: Shipment arrived at '{to_location.name}'. Its inventory is now {to_location.inventory.level}.")