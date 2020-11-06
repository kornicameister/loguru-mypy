import functools
import typing as t

from mypy.errorcodes import ErrorCode
from mypy.nodes import (
    Expression,
    FuncDef,
    LambdaExpr,
    NameExpr,
    RefExpr,
)
from mypy.options import Options
from mypy.plugin import (
    MethodContext,
    Plugin,
)
from mypy.types import (
    get_proper_type,
    ProperType,
    Type,
)
import typing_extensions as te

from loguru_mypy import call_parser

ERROR_BAD_ARG: te.Final[ErrorCode] = ErrorCode(
    'logger-arg',
    'Positional argument of loguru handler is not valid for given message',
    'loguru',
)
ERROR_BAD_KWARG: te.Final[ErrorCode] = ErrorCode(
    'logger-kwarg',
    'Named argument of loguru handler is not valid for given message',
    'loguru',
)


class Opts(t.NamedTuple):
    lazy: bool


DEFAULT_LAZY = False  # type: te.Final
DEFAULT_OPTS = Opts(lazy=DEFAULT_LAZY)  # type: te.Final
NAME_TO_BOOL = {
    'False': False,
    'True': True,
}  # type: te.Final


def _loguru_logger_call_handler(
    loggers: t.Dict[ProperType, Opts],
    ctx: MethodContext,
) -> Type:
    logger_opts = loggers.get(ctx.type) or DEFAULT_OPTS

    call_arguments = call_parser.parse_arguments(ctx)
    msg_arguments = call_parser.parse_message(ctx)

    # collect args/kwargs from string interpolation

    if log_msg_expected_args_count > call_args_count:
        ctx.api.msg.fail(
            f'Missing {log_msg_expected_args_count - call_args_count} '
            'positional arguments for log message',
            context=log_msg_expr,
            code=ERROR_BAD_ARG,
        )
        return ctx.default_return_type
    elif log_msg_expected_args_count < call_args_count:
        ctx.api.msg.note(
            f'Expected {log_msg_expected_args_count} but found {call_args_count} '
            'positional arguments for log message',
            context=log_msg_expr,
            code=ERROR_BAD_ARG,
        )
        return ctx.default_return_type
    elif logger_opts.lazy:
        for call_pos, call_arg in enumerate(call_args):
            if isinstance(call_arg, LambdaExpr) and call_arg.arguments:
                ctx.api.msg.fail(
                    f'Expected 0 arguments for <lambda>: {call_pos} arg',
                    context=call_arg,
                    code=ERROR_BAD_ARG,
                )
            elif isinstance(call_arg, RefExpr) and isinstance(
                    call_arg.node, FuncDef) and call_arg.node.arguments:
                ctx.api.msg.fail(
                    f'Expected 0 arguments for {call_arg.fullname}: {call_pos} arg',
                    context=call_arg,
                    code=ERROR_BAD_ARG,
                )

    for log_msg_kwarg in log_msg_expected_kwargs:
        maybe_kwarg_expr = call_kwargs.pop(log_msg_kwarg, None)
        if maybe_kwarg_expr is None:
            ctx.api.msg.fail(
                f'{log_msg_kwarg} keyword argument is missing',
                context=log_msg_expr,
                code=ERROR_BAD_KWARG,
            )
            return ctx.default_return_type
        elif logger_opts.lazy:
            if isinstance(maybe_kwarg_expr, LambdaExpr) and maybe_kwarg_expr.arguments:
                ctx.api.msg.fail(
                    f'Expected 0 arguments for <lambda>: {log_msg_kwarg} kwarg',
                    context=maybe_kwarg_expr,
                    code=ERROR_BAD_KWARG,
                )
            elif isinstance(maybe_kwarg_expr, RefExpr) and isinstance(
                    maybe_kwarg_expr.node, FuncDef) and maybe_kwarg_expr.node.arguments:
                ctx.api.msg.fail(
                    'Expected 0 arguments for '
                    f'{maybe_kwarg_expr.node.fullname}: {log_msg_kwarg}',
                    context=maybe_kwarg_expr,
                    code=ERROR_BAD_KWARG,
                )

    for extra_kwarg_name in call_kwargs:
        ctx.api.msg.fail(
            f'{extra_kwarg_name} keyword argument not found in log message',
            context=log_msg_expr,
            code=ERROR_BAD_KWARG,
        )

    return ctx.default_return_type


def _loguru_opt_call_handler(
    loggers: t.Dict[ProperType, Opts],
    ctx: MethodContext,
) -> Type:
    return_type = get_proper_type(ctx.default_return_type)

    lazy_expr = _get_opt_arg('lazy', ctx=ctx)
    if isinstance(lazy_expr, NameExpr):
        loggers[return_type] = Opts(lazy=NAME_TO_BOOL[lazy_expr.name])

    return return_type


def _get_opt_arg(
    arg_name: str,
    *,
    ctx: MethodContext,
) -> t.Optional[Expression]:
    try:
        return ctx.args[ctx.callee_arg_names.index(arg_name)][0]
    except IndexError:
        return None


class LoguruPlugin(Plugin):
    builtin_severities = (
        'info',
        'debug',
        'warning',
        'error',
        'exception',
        'success',
        'trace',
    )

    def __init__(self, options: Options) -> None:
        super().__init__(options)
        self._known_loggers: t.Dict[ProperType, Opts] = {}

    def get_method_hook(
        self,
        fullname: str,
    ) -> t.Optional[t.Callable[[MethodContext], Type]]:
        if fullname.startswith('loguru'):
            _, method = fullname.rsplit('.', 1)
            if method in self.builtin_severities:
                return functools.partial(_loguru_logger_call_handler, self._known_loggers)
            elif method == 'opt':
                return functools.partial(_loguru_opt_call_handler, self._known_loggers)
        return super().get_method_hook(fullname)


def plugin(version: str) -> t.Type[LoguruPlugin]:
    return LoguruPlugin
