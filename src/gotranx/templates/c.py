from textwrap import dedent, indent


def init_state_values(name, values, code):
    indented_code = indent(code, "    ")
    indent_values = indent(values, "    ")
    return dedent(
        f"""
void init_state_values(double* {name}){{
    /*
{indent_values}
    */
{indented_code}
}}
""",
    )


def init_parameter_values(name, values, code):
    indented_code = indent(code, "    ")
    indent_values = indent(values, "    ")
    return dedent(
        f"""
void init_parameter_values(double* {name}){{
    /*
{indent_values}
    */
{indented_code}
}}
""",
    )


def method(
    name: str,
    args: str,
    states: str,
    parameters: str,
    values: str,
    retrun_name: None = None,
):
    indent_states = indent(states, "    ")
    indent_parameters = indent(parameters, "    ")
    indent_values = indent(values, "    ")
    return dedent(
        f"""
void {name}({args}){{

    // Assign states
{indent_states}

    // Assign parameters
{indent_parameters}

    // Assign expressions
{indent_values}
}}
""",
    )
