import pytest
import gotranx


@pytest.fixture
def main_ode(trans, parser):
    expr = """
    parameters("Main component",
    sigma=ScalarParam(12.0, description="Some description"),
    rho=21.0
    )

    parameters("Z component",
    beta=2.4
    )

    states("Main component", x=1.0, y=2.0)

    states("Z component", z=3.05)

    expressions("Main component")
    rhoz = rho - z
    dy_dt = x*rhoz - y # millivolt
    dx_dt = sigma*(-x + y)

    expressions("Z component")
    betaz = beta*z
    dz_dt = -betaz + x*y
    """

    tree = parser.parse(expr)
    return gotranx.ode.make_ode(*trans.transform(tree), name="lorentz")


def test_component_to_ode(main_ode):
    z_comp = main_ode.get_component("Z component")
    z_ode = z_comp.to_ode()
    assert z_ode.missing_variables == {"x", "y"}
    assert z_ode.num_states == 1
    assert z_ode.num_parameters == 1
    assert z_ode.parameters[0].name == "beta"
    assert z_ode.states[0].name == "z"
    assert z_ode.name == "Z component"

    remaining_ode = main_ode - z_comp
    assert remaining_ode.missing_variables == {"z"}
    assert remaining_ode.num_states == 2
    assert remaining_ode.num_parameters == 2
    assert remaining_ode.parameters[0].name == "rho"
    assert remaining_ode.parameters[1].name == "sigma"
    assert remaining_ode.states[0].name == "x"
    assert remaining_ode.states[1].name == "y"
    assert remaining_ode.name == "lorentz - Z component"


@pytest.fixture
def z_ode_codegen(main_ode):
    z_comp = main_ode.get_component("Z component")
    z_ode = z_comp.to_ode()
    return gotranx.codegen.PythonCodeGenerator(z_ode)


def test_codegen_component_ode_missing_index(z_ode_codegen):
    assert z_ode_codegen.missing_index() == (
        "def missing_index(name: str) -> int:"
        '\n    """Return the index of the missing with the given name'
        "\n"
        "\n    Arguments"
        "\n    ---------"
        "\n    name : str"
        "\n        The name of the missing"
        "\n"
        "\n    Returns"
        "\n    -------"
        "\n    int"
        "\n        The index of the missing"
        "\n"
        "\n    Raises"
        "\n    ------"
        "\n    KeyError"
        "\n        If the name is not a valid missing"
        '\n    """'
        "\n"
        '\n    data = {"x": 0, "y": 1}'
        "\n    return data[name]"
        "\n"
    )


def test_codegen_component_ode_rhs(z_ode_codegen):
    assert z_ode_codegen.rhs() == (
        "def rhs(t, states, parameters, missing_variables):"
        "\n"
        "\n    # Assign states"
        "\n    z = states[0]"
        "\n"
        "\n    # Assign parameters"
        "\n    beta = parameters[0]"
        "\n"
        "\n    # Assign missing variables"
        "\n    x = missing_variables[0]"
        "\n    y = missing_variables[1]"
        "\n"
        "\n    # Assign expressions"
        "\n"
        "\n    values = numpy.zeros_like(states)"
        "\n    betaz = beta * z"
        "\n    dz_dt = -betaz + x * y"
        "\n    values[0] = dz_dt"
        "\n"
        "\n    return values"
        "\n"
    )
