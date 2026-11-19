# Copyright (c) 2026 Harmattan AI.
from pathlib import Path

import pytest
import yaml
from paperlib.naming import (
    NamingError,
    UnknownAcronymError,
    format_name,
    surname,
    title_snake,
)

FIXTURE = Path(__file__).parent / "fixtures" / "library_names.yaml"


@pytest.mark.parametrize(
    "title, expected",
    [
        (
            "Optimization Under Aerodynamic-Like Constraints",
            "optimization_under_aerodynamic-like_constraints",
        ),
        (
            "To CFD or not to CFD? Comparing RANS and viscous panel methods",
            "to_CFD_or_not_to_CFD_comparing_RANS_and_viscous_panel_methods",
        ),
        ("Sectional prediction of 3D effects", "sectional_prediction_of_3D_effects"),
        ("A 2.5d viscous model", "a_2.5D_viscous_model"),
        ("Solvers in deal.II", "solvers_in_deal.II"),
        (
            "The eN Method for Transition Prediction",
            "the_eN_method_for_transition_prediction",
        ),
        ("The e<sup>N</sup> method", "the_eN_method"),
        (
            "Boundary Layer Theory. Part I. Laminar Flows",
            "boundary_layer_theory_part_I_laminar_flows",
        ),
        ("Propeller at Mach Numbers to 0.96", "propeller_at_mach_numbers_to_0.96"),
        ("Case Histories 1920–1950", "case_histories_1920-1950"),
        ("Multi‐stage operator‑based design", "multi-stage_operator-based_design"),
        ("Theory & Practice", "theory_and_practice"),
        (
            "Momentum Equations w Shape Parameters",
            "momentum_equations_with_shape_parameters",
        ),
        ("Future Aircraft Sizing Tool (FAST)", "future_aircraft_sizing_tool_FAST"),
        ("Fast solvers", "fast_solvers"),
        ("Design of UAVs", "design_of_UAVs"),
        ("F50 wing at TU Delft", "F50_wing_at_TU_Delft"),
        ("The Kármán Vortex", "the_karman_vortex"),
        ("Prandtl's Theory", "prandtls_theory"),
        (
            "A WIND-TUNNEL INVESTIGATION OF A NACA PROPELLER",
            "a_wind-tunnel_investigation_of_a_NACA_propeller",
        ),
        (
            "Flow <i>over</i> a <mml:math><mml:mi>plate</mml:mi></mml:math>",
            "flow_over_a_plate",
        ),
        ("Low Reynolds Number Airfoils: XFOIL", "low_reynolds_number_airfoils_XFOIL"),
    ],
)
def test_title_snake(title: str, expected: str) -> None:
    assert title_snake(title) == expected


def test_unknown_acronym() -> None:
    with pytest.raises(UnknownAcronymError) as exc:
        title_snake("The MSES solver")
    assert exc.value.tokens == ["MSES"]


@pytest.mark.parametrize(
    "family, expected",
    [
        ("van Tooren", "van_Tooren"),
        ("van der Vorst", "van_der_Vorst"),
        ("Ramos García", "Ramos_Garcia"),
        ("Vaziry-Zanjany", "Vaziry-Zanjany"),
        ("Bendsøe", "Bendsoe"),
        ("Rüter", "Ruter"),
        ("Smith Jr.", "Smith"),
        ("Research in Flight", "Research_in_Flight"),
    ],
)
def test_surname(family: str, expected: str) -> None:
    assert surname(family) == expected


def test_et_al_after_three() -> None:
    assert format_name(
        "Topology optimization of turbulent flows",
        ["Dilgen", "Dilgen", "Fuhrman", "Sigmund"],
        2018,
    ) == ("topology_optimization_of_turbulent_flows_Dilgen_Dilgen_Fuhrman_et_al_2018")


def test_three_authors_no_et_al() -> None:
    assert (
        format_name("Q3D solver", ["Mariëns", "Elham", "van Tooren"], "2014")
        == "Q3D_solver_Mariens_Elham_van_Tooren_2014"
    )


@pytest.mark.parametrize("year", ["", "14", "1850", "twenty"])
def test_bad_year(year: str) -> None:
    with pytest.raises(NamingError):
        format_name("A title", ["Doe"], year)


def test_no_author() -> None:
    with pytest.raises(NamingError):
        format_name("A title", [], 2020)


def test_too_long() -> None:
    with pytest.raises(NamingError):
        format_name("word " * 60, ["Doe"], 2020)


@pytest.mark.skipif(
    not FIXTURE.exists(), reason="fixture generated from the migrated library"
)
def test_library_names_reproduce() -> None:
    entries = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    assert len(entries) == 95
    for entry in entries:
        assert (
            format_name(entry["title"], entry["families"], entry["year"])
            == entry["name"]
        )
