from typing import Callable, cast

from datatypes.datatypes import (
    Token,
    StaticToken,
    keyword_tokens,
    ControlToken,
    control_tokens,
    StatementNode,
    InitialAssignmentNode,
    IfNode,
    IndexingAction,
    ReAssignmentNode,
    BreakNode,
    ContinueNode,
    ForLoopNode,
    Variable,
    ExpressionNode,
    ValueNode,
    Node,
    exc, VALUE_TOKEN_RT, ValueNodeToken, value_node_tokens, )
from lexer.lexer import lex

type ParsingOutput = tuple[list[Token], Variable | Node | list[Node] | None]

def chain(
    tokens: list[Token],
    chain_list: list[ControlToken | Callable[[list[Token]], ParsingOutput]],
) -> tuple[list[Token], list[Variable | Node | None]]:
    res: list[Variable | Node | None] = []
    for chain_link in chain_list:
        if chain_link in control_tokens:
            if not tokens or cast(str, chain_link) != tokens[0]:
                return exc(tokens)
            tokens = tokens[1:]
            continue
        tokens, next_nodes = chain_link(tokens)
        if isinstance(next_nodes, list):
            res.extend(next_nodes)
            continue
        res.append(next_nodes)
    return tokens, res


def parse_statement(tokens: list[Token]) -> tuple[list[Token], StatementNode]:
    match tokens:
        case [keyword, *rest_tokens] if keyword in keyword_tokens:
            match keyword:
                case StaticToken.INT | StaticToken.BOOL | StaticToken.STRING:
                    remaining_tokens, (variable, value_node) = chain(
                        rest_tokens,
                        [parse_variable, parse_value_node, StaticToken.SEMICOLON],
                    )
                    return remaining_tokens, InitialAssignmentNode(
                        variable_type=keyword,
                        variable=variable,
                        values=[value_node],
                    )
                case (
                    StaticToken.INT_ARR | StaticToken.BOOL_ARR | StaticToken.STRING_ARR
                ):
                    remaining_tokens, (variable, *values) = chain(
                        rest_tokens, [parse_variable, parse_rest_arr]
                    )
                    return remaining_tokens, InitialAssignmentNode(
                        variable_type=keyword, variable=variable, values=values
                    )
                case StaticToken.IF:
                    remaining_tokens, (condition, *result) = chain(
                        rest_tokens,
                        [
                            parse_cond,
                            StaticToken.THEN_BEGIN,
                            parse_expr(stoppage_tokens={StaticToken.THEN_END}),
                            parse_opt_else,
                            StaticToken.SEMICOLON,
                        ],
                    )
                    return remaining_tokens, IfNode(
                        condition=condition,
                        then_clause=result[0],
                        else_clause=result[1] if len(result) > 1 else None,
                    )
                case StaticToken.ASSIGN:
                    match rest_tokens:
                        case [
                            IndexingAction() as ia,
                            *rest_tokens_two,
                        ]:
                            remaining_tokens, (value_node) = chain(
                                rest_tokens_two,
                                [parse_value_node, StaticToken.SEMICOLON],
                            )
                            return remaining_tokens, ReAssignmentNode(
                                variable_or_index=ia, values=value_node
                            )
                        case _:
                            # i
                            remaining_tokens, (variable, value_node) = chain(
                                rest_tokens,
                                [
                                    parse_variable,
                                    parse_value_node,
                                    StaticToken.SEMICOLON,
                                ],
                            )
                            return remaining_tokens, ReAssignmentNode(
                                variable_or_index=variable, values=value_node
                            )
                case StaticToken.ASSIGN_ARR:
                    remaining_tokens, (variable, *values) = chain(
                        rest_tokens,
                        [parse_variable, parse_rest_arr, StaticToken.SEMICOLON],
                    )
                    return remaining_tokens, ReAssignmentNode(
                        variable_or_index=variable, values=values
                    )
                case StaticToken.BREAK:
                    remaining_tokens, _ = chain(rest_tokens, [StaticToken.SEMICOLON])
                    return remaining_tokens, BreakNode()
                case StaticToken.CONTINUE:
                    remaining_tokens, _ = chain(rest_tokens, [StaticToken.SEMICOLON])
                    return remaining_tokens, ContinueNode()
                case StaticToken.FOR_BEGIN:
                    remaining_tokens, (
                        variable,
                        start_value,
                        end_value,
                        step,
                        clause,
                    ) = chain(
                        rest_tokens,
                        [
                            parse_variable,
                            parse_value_node,
                            parse_value_node,
                            parse_value_node,
                            parse_expr(stoppage_tokens={StaticToken.FOR_END}),
                            StaticToken.SEMICOLON,
                        ],
                    )
                    return remaining_tokens, ForLoopNode(
                        counter_variable=variable,
                        start_value=start_value,
                        end_value=end_value,
                        step=step,
                        clause=clause,
                    )

    return exc(tokens)


def parse_opt_else(tokens: list[Token]) -> tuple[list[Token], ExpressionNode | None]:
    match tokens:
        case [StaticToken.ELSE_BEGIN, *rest_tokens]:
            return parse_expr(stoppage_tokens={StaticToken.ELSE_END})(rest_tokens)
    return tokens, None


def parse_variable(tokens: list[Token]) -> tuple[list[Token], Variable]:
    match tokens[0]:
        case shadowed_keyword if shadowed_keyword in keyword_tokens:
            tokens[0] = Variable(value=cast(str, shadowed_keyword))

    match tokens:
        case [variable, *rest_tokens] if isinstance(variable, Variable):
            return rest_tokens, variable
    return exc(tokens)


def parse_rest_arr(tokens: list[Token]) -> tuple[list[Token], list[ValueNode]]:
    match tokens:
        case [StaticToken.SEMICOLON, *rest_tokens]:
            return rest_tokens, []
    remaining_tokens, (value_node, *rest) = chain(
        tokens, [parse_value_node, parse_rest_arr]
    )
    return remaining_tokens, [value_node, *rest]


def parse_value_node(tokens: list[Token]) -> tuple[list[Token], ValueNode]:
    match tokens:
        case [StaticToken.LPAREN, *rest_tokens]:
            remaining_tokens, (value_node, *rest_of_values) = chain(
                rest_tokens,
                [parse_value_node, StaticToken.RPAREN, parse_rest_value_nodes],
            )
            return remaining_tokens, ValueNode(terms=[StaticToken.LPAREN, value_node, StaticToken.RPAREN, *rest_of_values])
        case [value_token, *rest_tokens] if (
            is_negated := value_token == StaticToken.CMP_NOT
        ) or isinstance(value_token, VALUE_TOKEN_RT):
            if is_negated:
                # must match evaluated ValueToken or a Lparen Rparen
                match rest_tokens:
                    case [StaticToken.LPAREN, *rest_tokens_two]:
                        remaining_tokens, (value_node, *rest_of_values) = chain(
                            rest_tokens_two,
                            [
                                parse_value_node,
                                StaticToken.RPAREN,
                                parse_rest_value_nodes,
                            ],
                        )
                        value_node.is_negated = not value_node.is_negated
                        return remaining_tokens, ValueNode(
                            terms=[value_node, StaticToken.RPAREN, *rest_of_values], is_negated=False
                        )
                    case [value_token_two, *rest_tokens_two] if isinstance(
                        value_token_two, VALUE_TOKEN_RT
                    ):
                        remaining_tokens, (rest_of_values) = chain(
                            rest_tokens_two, [parse_rest_value_nodes]
                        )
                        return remaining_tokens, ValueNode(
                            terms=[
                                StaticToken.LPAREN,
                                ValueNode(terms=[value_token], is_negated=True),
                                StaticToken.RPAREN,
                                *rest_of_values,
                            ],
                            is_negated=False,
                        )
            else:
                remaining_tokens, (rest_of_values) = chain(
                    rest_tokens, [parse_rest_value_nodes]
                )
                return remaining_tokens, ValueNode(
                    terms=[value_token, *rest_of_values], is_negated=False
                )
    return exc(tokens)


def parse_rest_value_nodes(
    tokens: list[Token],
) -> tuple[list[Token], ValueNode | list[ValueNode]]:
    match tokens:
        case [op_comp, *rest_tokens] if op_comp in value_node_tokens:
            remaining_tokens, (value_node) = chain(rest_tokens, [parse_value_node])
            return remaining_tokens, ValueNode(terms=[cast(ValueNodeToken, op_comp), *value_node])
    return tokens, []


def parse_expr(
    stoppage_tokens: set[Token],
) -> Callable[[list[Token]], tuple[list[Token], ExpressionNode]]:

    def parse_expr_inner(tokens: list[Token]) -> tuple[list[Token], ExpressionNode]:
        remaining_tokens, (statements) = chain(
            tokens, [parse_statement, parse_rest_expr_inner]
        )
        return remaining_tokens, ExpressionNode(statements=statements)

    def parse_rest_expr_inner(
        tokens: list[Token],
    ) -> tuple[list[Token], list[StatementNode]]:
        match tokens:
            case []:
                return [], []
            case [potential_ending_token, *rest_tokens] if (
                potential_ending_token in stoppage_tokens
            ):
                return rest_tokens, []
        remaining_tokens, (expression_node,) = chain(
            tokens, [parse_expr(stoppage_tokens=stoppage_tokens)]
        )
        return remaining_tokens, expression_node.statements

    return parse_expr_inner


def parse_cond(tokens: list[Token]) -> tuple[list[Token], ValueNode]:
    remaining_tokens, (value_node) = chain(tokens, [parse_value_node])
    return remaining_tokens, value_node


def first_pass_parse(code_tokens: list[Token]) -> ExpressionNode:
    expr = parse_expr(set())(code_tokens)[1]
    return expr


def second_pass_parse(exp_node: ExpressionNode):
    # Flatten out value nodes into operation nodes (Shunting Yard)
    exp_node.transform_and_convert()
    # Type check entire code
    exp_node.type_check({}, {})

def parse(code_tokens: list[Token]) -> ExpressionNode:
    exp_node = first_pass_parse(code_tokens)
    second_pass_parse(exp_node)
    return exp_node


if __name__ == "__main__":
    parse(lex("""
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
