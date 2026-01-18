
import pytest
from courier.models import Package, Vehicle
from courier.services.cost_service import CostService
from courier.services.fleet_service import FleetService

def test_delivery_cost_calculation():
    base_cost = 100
    service = CostService(base_cost)

    # PKG1 5 5 OFR001 -> criteria fail (weight < 70), discount 0
    # Cost = 100 + (5*10) + (5*5) = 175
    p1 = Package("PKG1", 5, 5, "OFR001")
    service.calculate_cost(p1)
    assert p1.total_cost == 175
    assert p1.discount_amount == 0

    # PKG3 10 100 OFR003 -> matches (50-250km, 10-150kg). Disc 5%.
    # Cost = 100 + (10*10) + (100*5) = 700. Disc = 35. Total = 665.
    p3 = Package("PKG3", 10, 100, "OFR003")
    service.calculate_cost(p3)
    assert p3.total_cost == 665
    assert p3.discount_amount == 35


def test_shipment_grouping_logic():
    packages = [
        Package("PKG1", 50, 30, ""),
        Package("PKG2", 75, 125, ""),
        Package("PKG3", 175, 100, ""),
        Package("PKG4", 110, 60, ""),
        Package("PKG5", 155, 95, ""),
    ]

    from courier.services.shipment_service import ShipmentService
    shipment = ShipmentService.get_best_shipment(packages, 200)
    ids = sorted([p.pkg_id for p in shipment])
    assert ids == ["PKG2", "PKG4"]


def test_delivery_time_estimation():
    packages = [
        Package("PKG1", 50, 30, ""),
        Package("PKG2", 75, 125, ""),
        Package("PKG3", 175, 100, ""),
        Package("PKG4", 110, 60, ""),
        Package("PKG5", 155, 95, ""),
    ]
    vehicles = [
        Vehicle(1, 70, 200),
        Vehicle(2, 70, 200),
    ]

    fleet = FleetService(vehicles)
    fleet.process_deliveries(packages)

    p_map = {p.pkg_id: p.estimated_delivery_time for p in packages}

    assert p_map["PKG1"] == 3.98
    assert p_map["PKG2"] == 1.78
    assert p_map["PKG3"] == 1.42
    assert p_map["PKG4"] == 0.85
    assert p_map["PKG5"] == 4.19
