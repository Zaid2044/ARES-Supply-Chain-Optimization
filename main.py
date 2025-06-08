# main.py

import simpy
from ares_environment.simulation_nodes import Factory, Warehouse, ship_goods

def setup_and_run_simulation():
    """Sets up and runs a basic supply chain simulation."""
    # 1. Create a SimPy environment
    env = simpy.Environment()

    # 2. Create the simulation nodes (the "things" in our world)
    factory_a = Factory(env, name="Factory_EU")
    warehouse_us = Warehouse(env, name="Warehouse_US")

    # 3. Define the simulation logic as a generator function
    def simulation_logic(env):
        print("\n--- Simulation Starting ---")
        
        # Start the continuous processes
        env.process(warehouse_us.charge_holding_cost())

        # The main sequence of events
        # Factory A produces 100 units
        yield env.process(factory_a.produce(quantity=100))
        
        # Ship 70 units from Factory A to the US Warehouse
        yield env.process(ship_goods(env, from_location=factory_a, to_location=warehouse_us, quantity=70))

        # Factory A produces another 50 units
        yield env.process(factory_a.produce(quantity=50))
        
        print(f"--- Simulation Complete at time {env.now:.2f} ---")
        print(f"Final State: '{factory_a.name}' inventory: {factory_a.inventory.level}")
        print(f"Final State: '{warehouse_us.name}' inventory: {warehouse_us.inventory.level}")


    # 4. Start the simulation logic
    env.process(simulation_logic(env))

    # 5. Run the simulation for a set duration
    simulation_duration = 30 
    env.run(until=simulation_duration)


if __name__ == "__main__":
    setup_and_run_simulation()