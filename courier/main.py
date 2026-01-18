
import sys
from courier.models import Package, Vehicle
from courier.services.cost_service import CostService
from courier.services.fleet_service import FleetService

def main():
    lines = sys.stdin.read().strip().splitlines()
    if not lines:
        return

    # Header: base_cost num_packages
    base_cost, num_packages = lines[0].split()[:2]
    base_cost = int(base_cost)
    num_packages = int(num_packages)

    packages = []
    # Next num_packages lines
    for i in range(1, 1 + num_packages):
        parts = lines[i].split()
        pkg_id = parts[0]
        weight = int(parts[1])
        dist = int(parts[2])
        offer = parts[3]
        packages.append(Package(pkg_id, weight, dist, offer))

    # Cost calculation
    cost_service = CostService(base_cost)
    for p in packages:
        cost_service.calculate_cost(p)

    # Fleet line (optional)
    if len(lines) > 1 + num_packages:
        info = lines[1 + num_packages].split()
        num_vehicles = int(info[0])
        max_speed = int(info[1])
        max_load = int(info[2])
        vehicles = [Vehicle(v_id=i + 1, max_speed=max_speed, max_weight=max_load) for i in range(num_vehicles)]
        FleetService(vehicles).process_deliveries(packages)

    # Output
    for p in packages:
        # discount and cost formatting
        disc = int(p.discount_amount) if abs(p.discount_amount - int(p.discount_amount)) < 1e-9 else float(f"{p.discount_amount:.2f}")
        cost = int(p.total_cost) if abs(p.total_cost - int(p.total_cost)) < 1e-9 else float(f"{p.total_cost:.2f}")
        if p.estimated_delivery_time >= 0:
            print(f"{p.pkg_id} {disc} {cost} {p.estimated_delivery_time:.2f}")
        else:
            print(f"{p.pkg_id} {disc} {cost}")

if __name__ == "__main__":
    main()
