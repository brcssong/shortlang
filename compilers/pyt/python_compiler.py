from typing import cast

from datatypes.datatypes import ExpressionNode, InitialAssignmentNode, StaticToken, OperationNode, ValueToken, \
    OperationNodeToken, arithmetic_token_precedence, ReAssignmentNode, Variable, ForLoopNode, IfNode, BreakNode, \
    ContinueNode, DynamicToken, BoolLiteral, BLiteral
from lexer.lexer import lex
from parser.parser import parse

operator_to_python: dict[OperationNodeToken, str] = {
    StaticToken.CMP_NOT: "not",
    StaticToken.DIVIDE: "//",
    StaticToken.EQUALS: "==",
    StaticToken.NE: "!=",
    StaticToken.CMP_AND: "and",
    StaticToken.CMP_OR: "or",
}

def compile_value_token(token: DynamicToken) -> str:
    if isinstance(token, BoolLiteral):
        return "True" if token.value == BLiteral.TRUE else "False"
    return f"{token}"

def operator_inverted(parent: OperationNodeToken, child: OperationNodeToken) -> bool:
    # Inverted if parent's operator is of greater precedence than child
    return arithmetic_token_precedence[parent].precedence_value > arithmetic_token_precedence[child].precedence_value

def compile_operator(operator: StaticToken) -> str:
    return operator_to_python.get(cast(OperationNodeToken, operator), operator)

def compile_operation_node(node: OperationNode) -> str:
    def extract_value(node_or_token: OperationNode | ValueToken) -> str:
        if isinstance(node_or_token, OperationNode):
            return compile_operation_node(node_or_token)
        return f"{compile_value_token(node_or_token)}"
    if not node.operator:
        return f"{extract_value(node_or_token=node.left_value)}"
    if not node.right_value:
        return f"{compile_operator(node.operator)}({extract_value(node_or_token=node.left_value)})"
    result_string = ""
    if isinstance(node.left_value, OperationNode) and node.left_value.operator and operator_inverted(cast(OperationNodeToken, node.operator), cast(OperationNodeToken, node.left_value.operator)):
        result_string += f"({extract_value(node_or_token=node.left_value)})"
    else:
        result_string += f"{extract_value(node_or_token=node.left_value)}"
    result_string += f" {compile_operator(node.operator)} "
    if isinstance(node.right_value, OperationNode) and node.right_value.operator and operator_inverted(cast(OperationNodeToken, node.operator), cast(OperationNodeToken, node.right_value.operator)):
        result_string += f"({extract_value(node_or_token=node.right_value)})"
    else:
        result_string += f"{extract_value(node_or_token=node.right_value)}"

    return result_string

def compile_op_node_array(values: list[OperationNode]) -> str:
    return f"[{", ".join(compile_operation_node(value) for value in values)}]"

def compile_initial_assignment_node(node: InitialAssignmentNode, tabs: int = 0) -> str:
    match node.variable_type:
        case StaticToken.INT | StaticToken.BOOL | StaticToken.STRING:
            return "\t" * tabs + f"{node.variable.name} = {compile_operation_node(node.values[0])}"
        case _:
            return "\t" * tabs + f"{node.variable.name} = {compile_op_node_array(cast(list[OperationNode], node.values))}"

def compile_reassignment_node(node: ReAssignmentNode, tabs: int = 0) -> str:
    node_values = cast(list[OperationNode], node.values)
    if isinstance(node.variable_or_index, Variable):
        return "\t" * tabs + f"{node.variable_or_index.name} = {compile_operation_node(node_values[0]) if not node.is_arr else compile_op_node_array(node_values)}"
    else:
        return "\t" * tabs + f"{node.variable_or_index.variable.name}[{node.variable_or_index.index}] = {compile_operation_node(node_values[0]) if not node.is_arr else compile_op_node_array(node_values)}"

def compile_break_node(tabs: int = 0) -> str:
    return "\t" * tabs + "break"

def compile_continue_node(tabs: int = 0) -> str:
    return "\t" * tabs + "continue"

def compile_for_loop_node(for_node: ForLoopNode, tabs: int = 0) -> str:
    for_condition = "\t" * tabs + f"for {for_node.counter_variable.name} in range({compile_operation_node(cast(OperationNode, for_node.start_value))}, {compile_operation_node(cast(OperationNode, for_node.end_value))}, {compile_operation_node(cast(OperationNode, for_node.step))}):"
    body_clause = compile_expression_node(for_node.clause, tabs + 1)
    return f"{for_condition}\n{body_clause}"

def compile_if_node(if_node: IfNode, tabs: int = 0) -> str:
    if_parts = [f"if {compile_operation_node(cast(OperationNode, if_node.condition))}:",
                compile_expression_node(if_node.then_clause, tabs + 1)]
    if if_node.else_clause:
        if_parts.append("else:")
        if_parts.append(compile_expression_node(if_node.else_clause, tabs + 1))
    return "\n".join(if_parts)

def compile_expression_node(exp_node: ExpressionNode, tabs: int = 0) -> str:
    res = []
    for statement in exp_node.statements:
        match statement:
            case InitialAssignmentNode() as node:
                res.append(compile_initial_assignment_node(node, tabs))
            case ReAssignmentNode() as node:
                res.append(compile_reassignment_node(node, tabs))
            case ForLoopNode() as node:
                res.append(compile_for_loop_node(node, tabs))
            case IfNode() as node:
                res.append(compile_if_node(node, tabs))
            case BreakNode():
                res.append(compile_break_node(tabs))
            case ContinueNode():
                res.append(compile_continue_node(tabs))
    return "\n".join(res)

def compile_to_python(code: str) -> str:
    return compile_expression_node(parse(lex(code)))

if __name__ == '__main__':
    print(compile_to_python("""
                b[] a true false true false;
                if !!(a[1] + ((3 << 6) * 5)) = -6
                    th
                        i c 4;
                        f a 0 150 10
                            brk;
                        ff;
                    en
                    el
                        i d 9;
                    se
                ;
            """))