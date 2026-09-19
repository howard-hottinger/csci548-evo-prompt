from dataclasses import dataclass


@dataclass
class DefectCase:
    case_id: str
    family_id: str
    defect_type: str
    code: str
    expected_output: str | None = None


CASES = [
    DefectCase(
        case_id="syntax_001",
        family_id="addition",
        defect_type="SYNTAX",
        code="""
def add(a, b)
    return a + b
""",
    ),

    DefectCase(
        case_id="runtime_001",
        family_id="division",
        defect_type="RUNTIME",
        code="""
def divide(a, b):
    return a / b

print(divide(10, 0))
""",
    ),

    DefectCase(
        case_id="logic_001",
        family_id="multiplication",
        defect_type="LOGIC",
        code="""
def multiply(a, b):
    return a + b

print(multiply(4, 5))
""",
        expected_output="20",
    ),
]
