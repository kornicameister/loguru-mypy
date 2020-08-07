import functools
import re
import string
import typing as t

from mypy.errorcodes import ErrorCode
from mypy.nodes import (
    Expression,
    FuncDef,
    LambdaExpr,
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

RECORD_ARG_REGEX = re.compile('record\\[["|\'](?P<arg>.*)["|\']\\]')  # type: te.Final

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
ERROR_BAD_RECORD: te.Final[ErrorCode] = ErrorCode(
    'logger-record',
    'Invalid access to loguru record structure',
    'loguru',
)


class Opts(t.NamedTuple):
    lazy: bool
    record: bool


DEFAULT_LAZY = False  # type: te.Final
DEFAULT_RECORD = False  # type: te.Final
DEFAULT_OPTS = Opts(
    lazy=DEFAULT_LAZY,
    record=DEFAULT_RECORD,
)  # type: te.Final
NAME_TO_BOOL = {
    'False': False,
    'True': True,
}  # type: te.Final

RECORD_ARGS = (
    'elapsed',
    'exception',
    'extra',
    'file',
    'function',
    'level',
    'line',
    'message',
    'module',
    'name',
    'process',
    'thread',
    'time',
)  # type: te.Final


def _loguru_logger_call_handler(
    loggers: t.Dict[ProperType, Opts],
    ctx: MethodContext,
) -> Type:
    log_msg_expr = ctx.args[0][0]
    logger_opts = loggers.get(ctx.type) or DEFAULT_OPTS

    assert isinstance(log_msg_expr, StrExpr), type(log_msg_expr)

    # collect call args/kwargs
    # due to funky structure mypy offers here, it's easier
    # to beg for forgiveness here
    try:
        call_args = ctx.args[1]
        call_args_count = len(call_args)
    except IndexError:
        call_args = []
        call_args_count = 0
    try:
        call_kwargs: t.Dict[str, Expression] = {
            kwarg_name: ctx.args[2][idx]
            for idx, kwarg_name in enumerate(ctx.arg_names[2]) if kwarg_name
        }
    except IndexError:
        call_kwargs = {}

    # collect args/kwargs from string interpolation
    log_msg_value: str = log_msg_expr.value
    log_msg_expected_args_count = 0
    log_msg_expected_kwargs = []
    log_msg_record_references = []

    for res in string.Formatter().parse(log_msg_value):
        s_arg_name = res[1].strip() if res[1] is not None else None
        if s_arg_name is None:
            continue
        elif not s_arg_name:
            log_msg_expected_args_count += 1
        else:
            maybe_record_match = RECORD_ARG_REGEX.search(s_arg_name)
            if maybe_record_match:
                log_msg_record_references.append(maybe_record_match.group('arg'))
            else:
                log_msg_expected_kwargs.append(s_arg_name)

    if not _analyze_record_results(
            log_msg_expr,
            log_msg_record_references,
            call_kwargs,
            logger_opts,
            ctx=ctx,
    ):
        return ctx.default_return_type

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


def _analyze_record_results(
    log_msg_expr: StrExpr,
    log_msg_record_references: t.Sequence[str],
    call_kwargs: t.Mapping[str, Expression],
    logger_opts: Opts,
    *,
    ctx: MethodContext,
) -> bool:
    if logger_opts.record and 'record' in call_kwargs:
        ctx.api.msg.fail(
            'record keyword argument cannot override record structure',
            context=log_msg_expr,
            code=ERROR_BAD_KWARG,
        )
        return False
    if logger_opts.record and not log_msg_record_references:
        ctx.api.msg.note(
            'Logger configured with record=True is not using record structure',
            context=log_msg_expr,
            code=ERROR_BAD_RECORD,
        )
        return False
    elif not logger_opts.record and log_msg_record_references:
        ctx.api.msg.fail(
            'Logger is accessing record structure without record=True',
            context=log_msg_expr,
            code=ERROR_BAD_RECORD,
        )
        return False
    elif logger_opts.record:
        for record_attr in log_msg_record_references:
            if record_attr not in RECORD_ARGS:
                ctx.api.msg.fail(
                    f'Logger record structure does not contain {record_attr} key',
                    context=log_msg_expr,
                    code=ERROR_BAD_RECORD,
                )
    return True


def _loguru_opt_call_handler(
    loggers: t.Dict[ProperType, Opts],
    ctx: MethodContext,
) -> Type:
    return_type = get_proper_type(ctx.default_return_type)

    lazy_expr = _get_opt_arg('lazy', ctx=ctx)
    record_expr = _get_opt_arg('record', ctx=ctx)

    loggers[return_type] = Opts(
        lazy=NAME_TO_BOOL[lazy_expr.name] if isinstance(
            lazy_expr,
            NameExpr,
        ) else False,
        record=NAME_TO_BOOL[record_expr.name] if isinstance(
            record_expr,
            NameExpr,
        ) else False,
    )

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
