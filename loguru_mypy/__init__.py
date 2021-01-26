import functools
import string
import typing as t

from mypy.checker import TypeChecker
from mypy.errorcodes import ErrorCode
from mypy.nodes import (
    CallExpr,
    Expression,
    FuncDef,
    LambdaExpr,
    MemberExpr,
    NameExpr,
    RefExpr,
    StrExpr,
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
NOTE_EDGE_CASE: te.Final[str] = (
    'Congratulations!'
    'You have found an edge case in the loguru plugin.'
    'Please open an issue :)'
)


class Opts(t.NamedTuple):
    lazy: bool


DEFAULT_LAZY = False  # type: te.Final
DEFAULT_OPTS = Opts(lazy=DEFAULT_LAZY)  # type: te.Final
NAME_TO_BOOL = {
    'False': False,
    'True': True,
}  # type: te.Final


def _check_str_format_call(
    log_msg_expr: t.Union[StrExpr, NameExpr],
    ctx: MethodContext,
) -> None:
    """ Taps into mypy to typecheck something like this:

        ```py
        logger.debug('The bar is "{my_foo.bar}"', my_foo=foo)
        ```

        as if it was written like this:

        ```py
        logger.debug('The bar is "{my_foo.bar}"'.format(my_foo=foo))
        ```
    """
    call_expr = CallExpr(
        callee=MemberExpr(expr=log_msg_expr, name='format'),
        args=ctx.args[1] + ctx.args[2],
        arg_kinds=ctx.arg_kinds[1] + ctx.arg_kinds[2],
        arg_names=ctx.arg_names[1] + ctx.arg_names[2],
    )
    call_expr.set_line(log_msg_expr)

    # WARNING: `ctx.api` *is* technically a `mypy.checker.TypeChecker` so the cast is
    # safe to make, however, mypy says this should be an implementation detail.
    # So, anything that's not part of the `CheckerPluginInterface` should be expected to
    # change. See https://github.com/python/mypy/issues/6617
    try:
        type_checker = t.cast(TypeChecker, ctx.api)
        type_checker.expr_checker.visit_call_expr(call_expr)
    except AttributeError:
        ctx.api.msg.fail(
            (
                "AttributeError when trying to access mypy's functionality. "
                'This could mean you are trying to use incompatible versions '
                'of mypy and loguru-mypy.'
            ),
            context=log_msg_expr,
        )


def _unpack_call_arguments(
    ctx: MethodContext,
) -> t.Tuple[Expression, t.Sequence[Expression], t.Sequence[Expression]]:
    # Mypy has validated the call before handing it over to us
    # So it's passing the context parsed according to loguru's method signature
    # (Yes it's a bit funky)
    try:
        # (__self, __message: str, *args: Any, **kwargs: Any) -> None
        [[log_msg_expr], args, kwargs] = ctx.args
    except ValueError:
        # (__self, __message: Any) -> None
        [[log_msg_expr]] = ctx.args
        args = []
        kwargs = []
    return log_msg_expr, args, kwargs


def _loguru_logger_call_handler(
    loggers: t.Dict[ProperType, Opts],
    ctx: MethodContext,
) -> Type:
    call_msg, call_args, call_kwargs = _unpack_call_arguments(ctx)

    if isinstance(call_msg, (StrExpr, NameExpr)):
        _check_str_format_call(call_msg, ctx)
    elif not (call_args or call_kwargs):
        # Single argument, loguru will str() it, so nothing to be done
        # and callee is not expected to provide anything useful over here
        return ctx.default_return_type
    else:
        ctx.api.msg.note(
            NOTE_EDGE_CASE,
            context=call_msg,
        )
        return ctx.default_return_type

    logger_opts = loggers.get(ctx.type, DEFAULT_OPTS)
    if logger_opts.lazy and isinstance(call_msg, StrExpr):
        # collect args/kwargs from string interpolation
        log_msg_value: str = call_msg.value
        log_msg_expected_kwargs = []
        for res in string.Formatter().parse(log_msg_value):
            if res[1] is None:
                continue
            else:
                log_msg_expected_kwargs.append(res[1].strip())

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

        call_named_kwargs = {
            kwarg_name: call_kwargs[idx]
            for idx, kwarg_name in enumerate(ctx.arg_names[2])
        } if call_kwargs else {}
        for log_msg_kwarg in log_msg_expected_kwargs:
            maybe_kwarg_expr = call_named_kwargs.pop(log_msg_kwarg, None)
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


class UnsupportedMypyVersion(RuntimeError):
    def __init__(self, version: str) -> None:
        super().__init__(f'Mypy {version} is not supported')


def plugin(version: str) -> t.Type[LoguruPlugin]:
    minor = int(version.split('.')[1].replace('+dev', ''))
    if minor < 770:
        raise UnsupportedMypyVersion(version)
    return LoguruPlugin
