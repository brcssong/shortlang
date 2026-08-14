import re
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum, Enum
from typing import cast


def rmm(self, other) -> list[typing.Any]:
    if isinstance(other, list):
        other.append(self)
        return other
    return [other, self]


class AtAble:
    def __matmul__(self, other) -> list[typing.Any]:
        return [self, other]

    def __rmatmul__(self, other) -> list[typing.Any]:
        return rmm(self, other)


class Representable:
    def __repr__(self):
        res = [
            f"{type(self).__name__.upper()}: ",
            *(f"\t{line}" for line in self.short_lang_print()),
        ]
        return "\n".join(res)

    def short_lang_print(self, extra_tabs: int = 0) -> list[str]:
        res = []
        for attr, value in vars(self).items():
            res.append(f"[{attr.upper()}]:")
            if hasattr(value, "short_lang_print"):
                res.extend(value.short_lang_print(1))
            else:
                if type(value) == list:
                    res[-1] += " ["
                    res.extend(process_list(value))
                    res.append("]")
                else:
                    res.append("\t" + str(value))
        for idx in range(len(res)):
            res[idx] = "\t" * extra_tabs + res[idx]
        return res


def process_list(value: list[list | Representable]) -> list[str]:
    res = []
    for idx, val in enumerate(value):
        res.append(f"\t{idx}/{type(val).__name__.upper()}:")
        if isinstance(val, Representable):
            res.extend(val.short_lang_print(2))
        elif isinstance(val, list):
            res.extend(process_list(val))
        else:
            res.append(f"\t\t{val}")
    return res


class StaticToken(AtAble, StrEnum):
    INT = "i"
    BOOL = "b"
    STRING = "s"
    INT_ARR = "i[]"
    BOOL_ARR = "b[]"
    STRING_ARR = "s[]"
    IF = "if"
    THEN_BEGIN = "th"
    THEN_END = "en"
    ELSE_BEGIN = "el"
    ELSE_END = "se"
    ASSIGN = "g"
    ASSIGN_ARR = "gn"
    BREAK = "brk"
    CONTINUE = "cnt"
    FOR_BEGIN = "f"
    FOR_END = "ff"

    LPAREN = "("
    RPAREN = ")"

    SEMICOLON = ";"

    PLUS = "+"
    MINUS = "-"
    DIVIDE = "/"
    MULTIPLY = "*"
    LSHIFT = "<<"
    RSHIFT = ">>"
    BITWISE_OR = "|"
    BITWISE_AND = "&"
    XOR = "^"
    EXPONENT = "**"

    EQUALS = "="
    LTE = "<="
    GTE = ">="
    LT = "<"
    GT = ">"
    NE = "!"

    CMP_AND = "&&"
    CMP_OR = "||"
    CMP_NOT = "!!"

    EMPTY = ""


class DynamicToken(Representable, AtAble, ABC):
    @classmethod
    @abstractmethod
    def from_rem(cls, regex_match: re.Match) -> typing.Self:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def get_type(self) -> 'VariableType':
        pass


class Variable(DynamicToken):
    """
    this_a_variable
    """

    def __init__(self, value: str):
        self.name = value

    @classmethod
    def from_rem(cls, regex_match: re.Match):
        return cls(regex_match.group())

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other: object):
        if not isinstance(other, Variable):
            return NotImplemented

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def get_type(self) -> 'VariableType':
        return StaticToken.STRING


class IndexingAction(DynamicToken):
    """
    name_of_arr[5]
    """

    def __init__(self, variable: Variable, index: int):
        self.variable = variable
        self.index = index

    @classmethod
    def from_rem(cls, regex_match: re.Match):
        return cls(
            variable=Variable(regex_match.group(1)), index=int(regex_match.group(2))
        )

    def __str__(self):
        return f"{self.variable}[{self.index}]"

    def get_type(self) -> 'VariableType':
        return StaticToken.STRING


class IntLiteral(DynamicToken):
    """
    578
    """

    def __init__(self, value: int):
        self.value = value

    @classmethod
    def from_rem(cls, regex_match: re.Match):
        return cls(int(regex_match.group()))

    def __str__(self):
        return f"{self.value}"

    def get_type(self) -> 'VariableType':
        return StaticToken.INT


class BLiteral(StrEnum):
    TRUE = "true"
    FALSE = "false"


class BoolLiteral(DynamicToken):
    """
    true
    """

    def __init__(self, value: BLiteral):
        self.value = value

    @classmethod
    def from_rem(cls, regex_match: re.Match):
        return cls(BLiteral(regex_match.group()))

    def __str__(self):
        return f"{self.value}"

    def get_type(self) -> 'VariableType':
        return StaticToken.BOOL


class StringLiteral(DynamicToken):
    """
    "example of a string"
    """

    def __init__(self, value: str):
        self.value = value

    @classmethod
    def from_rem(cls, regex_match: re.Match):
        return cls(regex_match.group(1))

    def __str__(self):
        return f'"{self.value}"'

    def get_type(self) -> 'VariableType':
        return StaticToken.STRING


type Token = StaticToken | DynamicToken

type KeywordToken = typing.Literal[
    StaticToken.INT,
    StaticToken.BOOL,
    StaticToken.STRING,
    StaticToken.INT_ARR,
    StaticToken.BOOL_ARR,
    StaticToken.STRING_ARR,
    StaticToken.IF,
    StaticToken.ASSIGN,
    StaticToken.ASSIGN_ARR,
    StaticToken.BREAK,
    StaticToken.CONTINUE,
    StaticToken.FOR_BEGIN,
    StaticToken.FOR_END,
]
type ConnectorToken = typing.Literal[
    StaticToken.THEN_BEGIN,
    StaticToken.THEN_END,
    StaticToken.ELSE_BEGIN,
    StaticToken.ELSE_END,
]
type ControlToken = typing.Literal[
    StaticToken.LPAREN,
    StaticToken.RPAREN,
    StaticToken.SEMICOLON,
    StaticToken.THEN_BEGIN,
]
type OperatorToken = typing.Literal[
    StaticToken.PLUS,
    StaticToken.MINUS,
    StaticToken.DIVIDE,
    StaticToken.MULTIPLY,
    StaticToken.LSHIFT,
    StaticToken.RSHIFT,
    StaticToken.BITWISE_OR,
    StaticToken.BITWISE_AND,
    StaticToken.EXPONENT,
    StaticToken.XOR,
]
type ComparatorToken = typing.Literal[
    StaticToken.EQUALS,
    StaticToken.LTE,
    StaticToken.GTE,
    StaticToken.LT,
    StaticToken.GT,
    StaticToken.NE,
]
type JunctionToken = typing.Literal[StaticToken.CMP_AND, StaticToken.CMP_OR]
type ArithmeticInjectedToken = typing.Literal[StaticToken.CMP_NOT, StaticToken.LPAREN, StaticToken.RPAREN]
keyword_tokens: set[KeywordToken] = {
    StaticToken.INT,
    StaticToken.BOOL,
    StaticToken.STRING,
    StaticToken.INT_ARR,
    StaticToken.BOOL_ARR,
    StaticToken.STRING_ARR,
    StaticToken.IF,
    StaticToken.ASSIGN,
    StaticToken.ASSIGN_ARR,
    StaticToken.BREAK,
    StaticToken.CONTINUE,
    StaticToken.FOR_BEGIN,
    StaticToken.FOR_END,
}
connector_tokens: set[ConnectorToken] = {
    StaticToken.THEN_BEGIN,
    StaticToken.THEN_END,
    StaticToken.ELSE_BEGIN,
    StaticToken.ELSE_END,
}
control_tokens: set[ControlToken] = {
    StaticToken.LPAREN,
    StaticToken.RPAREN,
    StaticToken.SEMICOLON,
    StaticToken.THEN_BEGIN,
}
operator_tokens: set[OperatorToken] = {
    StaticToken.PLUS,
    StaticToken.MINUS,
    StaticToken.DIVIDE,
    StaticToken.MULTIPLY,
    StaticToken.LSHIFT,
    StaticToken.RSHIFT,
    StaticToken.BITWISE_OR,
    StaticToken.BITWISE_AND,
    StaticToken.XOR,
    StaticToken.EXPONENT,
}
comparator_tokens: set[ComparatorToken] = {
    StaticToken.EQUALS,
    StaticToken.LTE,
    StaticToken.GTE,
    StaticToken.LT,
    StaticToken.GT,
    StaticToken.NE,
}
junction_tokens: set[JunctionToken] = {
    StaticToken.CMP_AND,
    StaticToken.CMP_OR,
}
arithmetic_injected_tokens: set[ArithmeticInjectedToken] = {
    StaticToken.CMP_NOT,
    StaticToken.LPAREN,
    StaticToken.RPAREN,
}

type ValueNodeToken = OperatorToken | JunctionToken | ComparatorToken
value_node_tokens: set[ValueNodeToken] = set()
value_node_tokens.update(operator_tokens)
value_node_tokens.update(junction_tokens)
value_node_tokens.update(comparator_tokens)

type OperationNodeToken = OperatorToken | JunctionToken | ComparatorToken | ArithmeticInjectedToken
operation_node_tokens: set[OperationNodeToken] = set()
operation_node_tokens.update(operator_tokens)
operation_node_tokens.update(junction_tokens)
operation_node_tokens.update(comparator_tokens)
operation_node_tokens.update(arithmetic_injected_tokens)

type ValueToken = IntLiteral | BoolLiteral | StringLiteral | Variable | IndexingAction
VALUE_TOKEN_RT = (IntLiteral, BoolLiteral, StringLiteral, Variable, IndexingAction)

type VariableType = typing.Literal[
    StaticToken.INT,
    StaticToken.BOOL,
    StaticToken.STRING,
    StaticToken.INT_ARR,
    StaticToken.BOOL_ARR,
    StaticToken.STRING_ARR,
]
variable_tokens: set[VariableType] = {
    StaticToken.INT,
    StaticToken.BOOL,
    StaticToken.STRING,
    StaticToken.INT_ARR,
    StaticToken.BOOL_ARR,
    StaticToken.STRING_ARR,
}
type StatementNode = BreakNode | ContinueNode | IfNode | ForLoopNode | InitialAssignmentNode | ReAssignmentNode


class Node(Representable, ABC):
    @abstractmethod
    def transform_and_convert(self) -> "OperationNode | None":
        """
        Convert value_nodes into Operation Nodes, formalizing an AST for each mathematical expression
        """
        pass


type Scope = dict[Variable, tuple[VariableType, int]]


class ResultantType(Enum):
    LEFT = 0
    RIGHT = 1


# _ARR are not allowed in OperationNodes
@dataclass(kw_only=True)
class ResultantDeductionType:
    type: VariableType | None = None  # if None, means it inherits, ands it returns either 1 or 2 (left or right element)
    inherited_type: ResultantType | None = ResultantType.LEFT
    allowed_operand_types: set[VariableType] = field(default_factory=set)  # if empty, means any type is allowed


arithmetic_allowed_types: set[VariableType] = {StaticToken.INT, StaticToken.BOOL}

operand_type_deduction: dict[OperationNodeToken, ResultantDeductionType] = {
    StaticToken.CMP_NOT: ResultantDeductionType(),
    StaticToken.EXPONENT: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.MULTIPLY: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.DIVIDE: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.PLUS: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.MINUS: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.LSHIFT: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.RSHIFT: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.BITWISE_AND: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.XOR: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.BITWISE_OR: ResultantDeductionType(allowed_operand_types=arithmetic_allowed_types),
    StaticToken.EQUALS: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.LTE: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.GTE: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.LT: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.GT: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.NE: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.CMP_AND: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
    StaticToken.CMP_OR: ResultantDeductionType(type=StaticToken.BOOL, inherited_type=None),
}


def _extract_type_from_operand(value: 'OperationNode | ValueToken', variable_types: Scope) -> VariableType:
    if isinstance(value, Variable):
        return variable_types[value][0]
    elif isinstance(value, OperationNode):
        return value.evaluate_type(variable_types)
    elif isinstance(value, IndexingAction):
        match variable_types[value.variable][0]:
            case StaticToken.INT_ARR:
                return StaticToken.INT
            case StaticToken.BOOL_ARR:
                return StaticToken.BOOL
            case StaticToken.STRING_ARR:
                return StaticToken.STRING
            case _:
                raise Exception("Attempting to index into non-array type.")
    # Remaining case: pure Literal
    return cast(DynamicToken, value).get_type()


class OperationNode(Node, AtAble):
    def __init__(
            self,
            operator: OperationNodeToken | None,
            left_value: typing.Self | ValueToken,
            right_value: typing.Self | ValueToken | None,
    ):
        self.operator = operator
        self.left_value = left_value
        self.right_value = right_value

    def transform_and_convert(self) -> typing.Self | None:
        return self

    def evaluate_type(self, variable_types: Scope) -> VariableType:
        operand_types: list[VariableType] = [_extract_type_from_operand(self.left_value, variable_types)]
        if self.operator is None:
            return operand_types[0]
        if self.right_value is not None:
            operand_types.append(_extract_type_from_operand(self.right_value, variable_types))
        resultant_deduction_type = operand_type_deduction[cast(OperationNodeToken, self.operator)]
        if resultant_deduction_type.allowed_operand_types:
            for _type in operand_types:
                if _type not in resultant_deduction_type.allowed_operand_types:
                    raise Exception(
                        f"Type {_type} was not allowed for operator {self.operator}. Allowed types are {resultant_deduction_type.allowed_operand_types}.")
        if resultant_deduction_type.type is not None:
            return resultant_deduction_type.type
        if resultant_deduction_type.inherited_type is None:
            raise Exception(
                f"Operator {self.operator} was set to inherit, meaning that it must have an inherited index.")
        return operand_types[resultant_deduction_type.inherited_type.value]

    def type_check(self, outer_scope: Scope,
                   inner_scope: Scope) -> VariableType:
        all_variables = {**outer_scope, **inner_scope}
        return self.evaluate_type(all_variables)


@dataclass
class Precedence:
    precedence_value: int
    left_associative: bool


arithmetic_token_precedence: dict[OperationNodeToken, Precedence] = {
    StaticToken.LPAREN: Precedence(6, True),
    StaticToken.RPAREN: Precedence(6, True),
    StaticToken.CMP_NOT: Precedence(5, False),
    StaticToken.EXPONENT: Precedence(4, False),
    StaticToken.MULTIPLY: Precedence(3, True),
    StaticToken.DIVIDE: Precedence(3, True),
    StaticToken.PLUS: Precedence(2, True),
    StaticToken.MINUS: Precedence(2, True),
    StaticToken.LSHIFT: Precedence(1, True),
    StaticToken.RSHIFT: Precedence(1, True),
    StaticToken.BITWISE_AND: Precedence(0, True),
    StaticToken.XOR: Precedence(-1, True),
    StaticToken.BITWISE_OR: Precedence(-2, True),
    StaticToken.EQUALS: Precedence(-3, True),
    StaticToken.LTE: Precedence(-3, True),
    StaticToken.GTE: Precedence(-3, True),
    StaticToken.LT: Precedence(-3, True),
    StaticToken.GT: Precedence(-3, True),
    StaticToken.NE: Precedence(-3, True),
    StaticToken.CMP_AND: Precedence(-5, True),
    StaticToken.CMP_OR: Precedence(-6, True),
}


def convert_postfix_to_op_node(output_stack: list[OperationNode | Token]) -> OperationNode:
    if not output_stack:
        raise Exception(f"Could not finish converting postfix in expression stack {output_stack}")
    top_value = output_stack.pop()
    if top_value in operation_node_tokens:
        operator = cast(OperationNodeToken, top_value)
        if operator in [StaticToken.CMP_NOT]:
            left_parse = convert_postfix_to_op_node(output_stack)
            return OperationNode(
                operator=operator,
                left_value=left_parse,
                right_value=None
            )
        right_parse = convert_postfix_to_op_node(output_stack)
        left_parse = convert_postfix_to_op_node(output_stack)
        return OperationNode(
            operator=operator,
            left_value=left_parse,
            right_value=right_parse,
        )
    elif isinstance(top_value, VALUE_TOKEN_RT):
        return OperationNode(operator=None, left_value=top_value, right_value=None)
    else:
        raise Exception(f"Value in postfix expression stack is not matching any valid type: {output_stack[-1]}")


class ValueNode(Node, AtAble):
    def __init__(
            self,
            terms: list[typing.Self | ValueToken | OperationNodeToken],
            is_negated: bool = False,
    ):
        self.terms = terms
        self.is_negated = is_negated

    def get_flattened_terms(self) -> list[typing.Self | ValueToken | OperationNodeToken]:
        res = []
        for term in self.terms:
            if isinstance(term, ValueNode):
                if term.is_negated:
                    res.append(StaticToken.CMP_NOT)
                    res.append(StaticToken.LPAREN)
                res.extend(term.get_flattened_terms())
            else:
                res.append(term)
        return res

    def transform_and_convert(self) -> OperationNode:
        # Shunting Yard algorithm
        op_stk: list[OperationNodeToken] = []
        output: list[OperationNode | Token] = []
        for term in self.get_flattened_terms():
            if isinstance(term, ValueNode):
                output.append(term.transform_and_convert())
            elif isinstance(term, VALUE_TOKEN_RT):
                output.append(term)
            elif term in operation_node_tokens:
                term = cast(OperationNodeToken, term)
                if term == StaticToken.RPAREN:
                    # Special case of drain
                    while op_stk and op_stk[-1] != StaticToken.LPAREN:
                        output.append(op_stk.pop())
                    op_stk.pop()
                    continue
                elif term == StaticToken.LPAREN:
                    # Special case of add
                    op_stk.append(term)
                    continue
                while op_stk:
                    precedence = arithmetic_token_precedence[op_stk[-1]].precedence_value
                    if op_stk[-1] != StaticToken.LPAREN and arithmetic_token_precedence[term].left_associative and \
                            arithmetic_token_precedence[term].precedence_value <= precedence or \
                            not arithmetic_token_precedence[term].left_associative and \
                            arithmetic_token_precedence[term].precedence_value < precedence:
                        output.append(op_stk.pop())
                    else:
                        break
                op_stk.append(term)
            else:
                return exc_type_check(self, f"Error treating {term} as an operator.")
        while op_stk:
            output.append(op_stk.pop())
        # At postfix stage
        return convert_postfix_to_op_node(output)


class BreakNode(Node, AtAble):
    def __init__(self):
        pass

    def transform_and_convert(self) -> 'OperationNode | None':
        return

    def type_check(self, outer_scope: Scope,
                   old_inner_scope: Scope):
        return


class ContinueNode(Node, AtAble):
    def __init__(self):
        pass

    def transform_and_convert(self) -> "OperationNode | None":
        return

    def type_check(self, outer_scope: Scope,
                   inner_scope: Scope):
        return


class ForLoopNode(Node, AtAble):
    def __init__(
            self,
            counter_variable: Variable,
            start_value: ValueNode | OperationNode,
            end_value: ValueNode | OperationNode,
            step: ValueNode | OperationNode,
            clause: "ExpressionNode",
    ):
        self.counter_variable = counter_variable
        self.start_value = start_value
        self.end_value = end_value
        self.step = step
        self.clause = clause

    def transform_and_convert(self) -> "OperationNode | None":
        self.start_value = self.start_value.transform_and_convert()
        self.end_value = self.end_value.transform_and_convert()
        self.step = self.step.transform_and_convert()

    def type_check(self, outer_scope: Scope, old_inner_scope: Scope):
        outer_scope: Scope = {**outer_scope, **old_inner_scope}
        inner_scope: Scope = {self.counter_variable: (StaticToken.INT, -1)}
        self.clause.type_check(outer_scope, inner_scope)


class IfNode(Node, AtAble):
    def __init__(
            self,
            condition: ValueNode | OperationNode,
            then_clause: "ExpressionNode",
            else_clause: "ExpressionNode | None",
    ):
        self.condition = condition
        self.then_clause = then_clause
        self.else_clause = else_clause

    def transform_and_convert(self) -> "OperationNode | None":
        self.condition = self.condition.transform_and_convert()
        self.then_clause.transform_and_convert()
        if self.else_clause:
            self.else_clause.transform_and_convert()

    def type_check(self, outer_scope: Scope, inner_scope: Scope):
        if isinstance(self.condition, ValueNode):
            return exc_type_check(self, f"Illegally invoked type check on condition {self.condition} before conversion to OperationNode.")
        self.condition.type_check(outer_scope, inner_scope)
        self.then_clause.type_check({**outer_scope, **inner_scope}, dict())
        if self.else_clause is not None:
            self.else_clause.type_check({**outer_scope, **inner_scope}, dict())
        return None


class InitialAssignmentNode(Node, AtAble):
    def __init__(
            self,
            variable_type: VariableType,
            variable: Variable,
            values: list[ValueNode] | list[OperationNode],
    ):
        self.variable_type = variable_type
        self.variable = variable
        self.values = values

    def transform_and_convert(self) -> "OperationNode | None":
        self.values = [value.transform_and_convert() for value in self.values]

    def type_check(self, _, inner_scope: Scope):
        if self.variable in inner_scope:
            return exc_type_check(self, f"Type checking failed at AST node {self}.")
        # Deduce initial assignment type
        match self.variable_type:
            case StaticToken.INT_ARR:
                variable = StaticToken.INT
            case StaticToken.BOOL_ARR:
                variable = StaticToken.BOOL
            case StaticToken.STRING_ARR:
                variable = StaticToken.STRING
            case _:
                variable = self.variable_type

        # On initial assignment, types must strictly confirm (i.e. 4 for bool is not valid)
        for value in self.values:
            if not isinstance(value, OperationNode):
                return exc_type_check(self, f"Value {value} must have been converted to OperationNode first before type checking")
            if value.type_check({}, inner_scope) != variable:
                return exc_type_check(self, f"Error when type checking for InitialAssignment of {self.variable}")

        if self.variable_type in {StaticToken.INT, StaticToken.BOOL, StaticToken.STRING}:
            inner_scope[self.variable] = (self.variable_type, -1)
        else:
            inner_scope[self.variable] = (cast(VariableType, self.variable_type), len(self.values))
        return None


class ReAssignmentNode(Node, AtAble):
    def __init__(
            self,
            variable_or_index: Variable | IndexingAction,
            values: ValueNode | list[ValueNode] | list[OperationNode],
    ):
        self.is_arr = None
        self.variable_or_index = variable_or_index
        self.values = values

    def transform_and_convert(self) -> "OperationNode | None":
        if isinstance(self.values, list):
            self.values = [value.transform_and_convert() for value in self.values]
            self.is_arr = True
        else:
            self.values = [self.values.transform_and_convert()]
            self.is_arr = False

    def type_check(self, outer_scope: Scope, inner_scope: Scope):
        variable = self.variable_or_index.variable if isinstance(self.variable_or_index, IndexingAction) else self.variable_or_index
        variable_scope = inner_scope if variable in inner_scope else outer_scope
        if self.variable_or_index not in variable_scope:
            return exc_type_check(self, "Could not find variable {self.variable_or_index..")
        variable_type, length_of_structure = variable_scope[variable]
        match variable_type:
            case StaticToken.INT | StaticToken.BOOL | StaticToken.STRING:
                if isinstance(self.variable_or_index, IndexingAction):
                    # ASSIGN INDEX ON AN ASSIGN TYPE
                    return exc_type_check(self, "Attempted to assign array index to singular value.")
                if self.is_arr:
                    return exc_type_check(self, "Reassignment tried to set array value to non-array variable.")
            case _:
                if isinstance(self.variable_or_index, IndexingAction):
                    # ASSIGN_ARR
                    if length_of_structure == -1 or not 0 <= self.variable_or_index.index < length_of_structure:
                        return exc_type_check(self, "Selected index was either out of bounds or attempted to assign array index to singular element.")
                if not self.is_arr:
                    return exc_type_check(self, "Reassignment tried to set non-array value to array variable.")
        return None


class ExpressionNode(Node, AtAble):
    def __init__(self, statements: list[StatementNode]):
        self.statements = statements

    def transform_and_convert(self) -> "OperationNode | None":
        for statement in self.statements:
            statement.transform_and_convert()

    def type_check(self, outer_scope: Scope, inner_scope: Scope):
        for statement in self.statements:
            statement.type_check(outer_scope, inner_scope)


def exc(tokens: list[Token]):
    raise Exception(
        f"Error parsing tokens near [{tokens[0]}]"
    )

def exc_type_check(node: Node, msg: str):
    raise Exception(
        f"Error while type checking for node: {type(node).__name__}: {msg}"
    )