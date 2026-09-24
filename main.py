import json
import math
import sys



# 1. Calculate Euclidean Distance


def calculate_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.

    Formula:
        distance = sqrt((x2-x1)^2 + (y2-y1)^2)
    """

    x1, y1 = point1
    x2, y2 = point2

    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )



# 2. Normalize Different JSON Formats

def normalize_data(data):
    """
    Convert different JSON formats into one common format.

    Supported warehouse/agent formats:

    Format 1:
        "agents": [
            {"id": "A1", "location": [5, 5]}
        ]

    Format 2:
        "agents": {
            "A1": [5, 5]
        }

    The same normalization is applied to warehouses.

    Package formats supported:

        "warehouse_id": "W1"

    or:

        "warehouse": "W1"
    """

   
    # Normalize warehouses
   

    warehouses = data["warehouses"]

    if isinstance(warehouses, dict):

        normalized_warehouses = []

        for warehouse_id, location in warehouses.items():

            normalized_warehouses.append({
                "id": warehouse_id,
                "location": location
            })

        data["warehouses"] = normalized_warehouses

   
    # Normalize agents
   

    agents = data["agents"]

    if isinstance(agents, dict):

        normalized_agents = []

        for agent_id, location in agents.items():

            normalized_agents.append({
                "id": agent_id,
                "location": location
            })

        data["agents"] = normalized_agents

   
    # Normalize package warehouse field
   

    for package in data["packages"]:

        if "warehouse_id" not in package:

            if "warehouse" in package:

                package["warehouse_id"] = package["warehouse"]

    return data



# 3. Find Warehouse by ID


def find_warehouse(warehouse_id, warehouses):
    """
    Find and return a warehouse using its ID.
    """

    for warehouse in warehouses:

        if warehouse["id"] == warehouse_id:
            return warehouse

    return None



# 4. Find Nearest Agent


def find_nearest_agent(warehouse_location, agents):
    """
    Find the agent whose location is closest
    to the warehouse.
    """

    nearest_agent = None
    shortest_distance = float("inf")

    for agent in agents:

        distance = calculate_distance(
            agent["location"],
            warehouse_location
        )

        if distance < shortest_distance:

            shortest_distance = distance
            nearest_agent = agent

    return nearest_agent



# 5. Load JSON Data


def load_data(filename):
    """
    Read and parse the JSON input file.
    """

    try:

        with open(filename, "r") as file:

            data = json.load(file)

        return data

    except FileNotFoundError:

        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    except json.JSONDecodeError:

        print(f"Error: '{filename}' is not a valid JSON file.")
        sys.exit(1)



# 6. Validate Input Data


def validate_data(data):
    """
    Validate the basic structure of the input JSON.
    """

    required_keys = [
        "warehouses",
        "agents",
        "packages"
    ]

    # Check required keys
    for key in required_keys:

        if key not in data:

            print(
                f"Error: Missing '{key}' "
                f"in input JSON."
            )

            sys.exit(1)

    # Check warehouses
    if not data["warehouses"]:

        print("Error: No warehouses found.")
        sys.exit(1)

    # Check agents
    if not data["agents"]:

        print("Error: No agents found.")
        sys.exit(1)

    # Check packages
    if not data["packages"]:

        print("Error: No packages found.")
        sys.exit(1)



# 7. Initialize Report


def initialize_report(agents):
    """
    Create an empty report for every agent.
    """

    report = {}

    for agent in agents:

        report[agent["id"]] = {
            "packages_delivered": 0,
            "total_distance": 0.0
        }

    return report



# 8. Process All Packages


def process_packages(data, report):
    """
    Assign every package to the nearest agent
    and calculate the delivery distance.
    """

    warehouses = data["warehouses"]
    agents = data["agents"]
    packages = data["packages"]

    for package in packages:

        package_id = package["id"]

     
        # Find package warehouse
     

        warehouse_id = package["warehouse_id"]

        warehouse = find_warehouse(
            warehouse_id,
            warehouses
        )

        if warehouse is None:

            print(
                f"Warning: Warehouse "
                f"'{warehouse_id}' not found "
                f"for package {package_id}."
            )

            continue

        warehouse_location = warehouse["location"]

     
        # Find nearest agent
     

        nearest_agent = find_nearest_agent(
            warehouse_location,
            agents
        )

        if nearest_agent is None:

            print(
                f"Warning: No agent available "
                f"for package {package_id}."
            )

            continue

     
        # Agent -> Warehouse
     

        distance_to_warehouse = calculate_distance(
            nearest_agent["location"],
            warehouse_location
        )

     
        # Warehouse -> Destination
     

        distance_to_destination = calculate_distance(
            warehouse_location,
            package["destination"]
        )

     
        # Total distance
     

        total_distance = (
            distance_to_warehouse +
            distance_to_destination
        )

     
        # Update report
     

        agent_id = nearest_agent["id"]

        report[agent_id]["packages_delivered"] += 1

        report[agent_id]["total_distance"] += total_distance

     
        # Display package assignment
     

        print(
            f"{package_id} -> "
            f"{agent_id} | "
            f"Warehouse: {warehouse['id']} | "
            f"Distance: {total_distance:.2f}"
        )



# 9. Calculate Efficiency


def calculate_efficiency(report):
    """
    Calculate efficiency for every agent.

    Formula:

        efficiency =
            total_distance / packages_delivered
    """

    for agent_id in report:

        packages_delivered = (
            report[agent_id]["packages_delivered"]
        )

        total_distance = (
            report[agent_id]["total_distance"]
        )

        if packages_delivered > 0:

            efficiency = (
                total_distance /
                packages_delivered
            )

        else:

            efficiency = 0.0

        # Round total distance
        report[agent_id]["total_distance"] = round(
            total_distance,
            2
        )

        # Round efficiency
        report[agent_id]["efficiency"] = round(
            efficiency,
            2
        )



# 10. Find Best Agent


def find_best_agent(report):
    """
    Find the agent with the lowest efficiency value.

    Only agents who delivered at least one package
    are considered.
    """

    active_agents = [
        agent_id
        for agent_id in report
        if report[agent_id]["packages_delivered"] > 0
    ]

    if not active_agents:

        return None

    best_agent = min(
        active_agents,
        key=lambda agent_id:
        report[agent_id]["efficiency"]
    )

    return best_agent



# 11. Validate Delivery Count


def validate_delivery_count(data, report):
    """
    Check whether all packages were delivered.
    """

    total_packages = len(
        data["packages"]
    )

    total_delivered = sum(
        report[agent_id]["packages_delivered"]
        for agent_id in report
    )

    print()
    print("Delivery Validation")
    print("--------------------")

    print(
        f"Total packages:   "
        f"{total_packages}"
    )

    print(
        f"Total delivered:  "
        f"{total_delivered}"
    )

    if total_packages == total_delivered:

        print(
            "Status: All packages "
            "delivered successfully."
        )

        return True

    else:

        print(
            "Status: Some packages "
            "were not delivered."
        )

        return False



# 12. Save Report


def save_report(report, filename="report.json"):
    """
    Save the final report as JSON.
    """

    try:

        with open(filename, "w") as file:

            json.dump(
                report,
                file,
                indent=4
            )

        print()
        print(
            f"Report saved successfully "
            f"to '{filename}'."
        )

    except OSError as error:

        print(
            f"Error while saving report: "
            f"{error}"
        )



# 13. Main Program


def main():

    print("=" * 60)

    print(
        "          FASTBOX MYSTERY DELIVERY SYSTEM"
    )

    print("=" * 60)

   
    # Get input filename
   

    if len(sys.argv) > 1:

        input_file = sys.argv[1]

    else:

        input_file = "data.json"

    print()
    print(
        f"Input file: {input_file}"
    )
    print()

   
    # Load JSON
   

    data = load_data(
        input_file
    )

   
    # Normalize JSON
   

    data = normalize_data(
        data
    )

   
    # Validate input
   

    validate_data(
        data
    )

   
    # Initialize report
   

    report = initialize_report(
        data["agents"]
    )

    
    # Process packages
    

    print(
        "Package Assignments"
    )

    print(
        "--------------------"
    )

    process_packages(
        data,
        report
    )

   
    # Calculate efficiency
   

    calculate_efficiency(
        report
    )

   
    # Find best agent
   

    best_agent = find_best_agent(
        report
    )

   
    # Validate delivery count
   

    validate_delivery_count(
        data,
        report
    )

   
    # Add best agent AFTER validation
   

    report["best_agent"] = best_agent

   
    # Save report
   

    save_report(
        report,
        "report.json"
    )

   
    # Display final report
   

    print()
    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    for agent_id, details in report.items():

        # Skip best_agent because it is not an agent object
        if agent_id == "best_agent":
            continue

        print()
        print(agent_id)

        print(
            f"  Packages Delivered: "
            f"{details['packages_delivered']}"
        )

        print(
            f"  Total Distance: "
            f"{details['total_distance']:.2f}"
        )

        print(
            f"  Efficiency: "
            f"{details['efficiency']:.2f}"
        )

    print()
    print("-" * 60)

    print(
        f"Best Agent: "
        f"{report['best_agent']}"
    )

    print("-" * 60)



# Program Entry Point


if __name__ == "__main__":
    main()