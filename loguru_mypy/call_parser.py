from dataclasses import dataclass
import string
import typing as t

from mypy.nodes import (
    DictExpr,
    Expression,
    StrExpr,
)
from mypy.plugin import MethodContext

CallArgs = t.Sequence[Expression]
CallKwargs = t.Dict[str, Expression]

T = t.TypeVar('T', int, str)


@dataclass
class BaseCallArgument(t.Generic[T]):
    idx: T
    expression: Expression

    @property
    def is_complex(self) -> bool:
        return isinstance(self.expression, DictExpr)

    @property
    def is_arg(self) -> bool:
        return False

    @property
    def is_kwarg(self) -> bool:
        return False


@dataclass(frozen=True)
class CallArg(BaseCallArgument[int]):
    @property
    def is_arg(self) -> bool:
        return True


@dataclass(frozen=True)
class CallKwarg(BaseCallArgument[str]):
    @property
    def is_kwarg(self) -> bool:
        return True


class CallArguments(t.List[t.Union[CallArg, CallKwarg]]):
    @property
    def args(self) -> t.Sequence[CallArg]:
        return tuple(filter(lambda x: isinstance(x, CallArg), self))


def parse_arguments(ctx: MethodContext) -> CallArguments:
    call_arguments = CallArguments()

    try:
        call_arguments.extend(
            CallArg(idx=T(idx), expression=expression)
            for idx, expression in enumerate(ctx.args[1])
        )
    except IndexError:
        ...

    try:
        call_arguments.extend(
            CallKwarg(idx=T(kwarg_name), expression=ctx.args[2][idx])
            for idx, kwarg_name in enumerate(ctx.arg_names[2]) if kwarg_name
        )
    except IndexError:
        ...

    return call_arguments


def parse_message(ctx: MethodContext) -> None:
    expr = ctx.args[0][0]

    # once there is more types to handle use t.overload
    assert isinstance(expr, StrExpr), type(expr)
    return _parse_message(expr)


def _parse_message(expr: StrExpr) -> None:
    log_msg_value: str = expr.value

    log_msg_expected_args_count = 0
    log_msg_expected_kwargs = []

    for idx, arg in enumerate(string.Formatter().parse(log_msg_value)):
        if arg[1] is None:
            continue
        elif not arg[1].strip():
            log_msg_expected_args_count += 1
        else:
            log_msg_expected_kwargs.append(arg[1].strip())
