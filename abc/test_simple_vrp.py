"""
Simple VRP Solver - Test version
"""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Test data
locations = [
    {'name': 'Start', 'lat': 10.7723, 'lon': 106.6981},  # Start
    {'name': 'A', 'lat': 10.7797, 'lon': 106.699},
    {'name': 'B', 'lat': 10.7676, 'lon': 106.7071},
    {'name': 'C', 'lat': 10.7769, 'lon': 106.6952},
]

# Distance matrix (simplified - Manhattan distance * 100)
distance_matrix = [
    [0, 80, 95, 70],
    [80, 0, 140, 85],
    [95, 140, 0, 115],
    [70, 85, 115, 0]
]

print("Testing simple VRP...")
print(f"Locations: {len(locations)}")

# Create routing model
manager = pywrapcp.RoutingIndexManager(len(locations), 1, 0)
routing = pywrapcp.RoutingModel(manager)

# Distance callback
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Search parameters
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)

# Solve
print("Solving...")
solution = routing.SolveWithParameters(search_parameters)

if solution:
    print("✅ Solution found!")
    index = routing.Start(0)
    route = []
    total_distance = 0
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route.append(locations[node]['name'])
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        total_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    
    print(f"Route: {' -> '.join(route)}")
    print(f"Distance: {total_distance}")
else:
    print("❌ No solution found")
