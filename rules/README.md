# Diagnostic rules

Rules are data, not implementation-specific code.

A rule should describe:

1. what repository evidence it reads;
2. what machine evidence it needs;
3. the comparison logic;
4. the expected result;
5. the safety constraints;
6. the human-readable explanation.

Rules should be declarative YAML or TOML.

The reference implementation will interpret these rules rather than hard-code every diagnostic.

## First rule families

- Node.js semver constraints
- Node version files
- Python version constraints
- Python version files
- environment-variable presence
- Compose host/container port mappings
- host port availability
- declared runtime/tool presence

## Safety

Rules must not modify the user's machine.

Rules must not collect secret values.

For environment variables, the primitive is presence/missing/unknown, never the value.
