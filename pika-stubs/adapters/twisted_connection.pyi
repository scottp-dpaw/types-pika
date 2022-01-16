from __future__ import annotations

from typing import (
    Any,
    Callable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Union,
    TypeVar,
    Tuple,
)

import twisted.internet.base
import twisted.internet.defer
import twisted.internet.interfaces
import twisted.internet.protocol
import twisted.python.failure
from twisted.internet.defer import Deferred, DeferredQueue

from .. import amqp_object
from .. import frame
from .. import spec
from ..connection import Connection
from ..connection import Parameters
from ..channel import Channel

_T = TypeVar("_T")

class ClosableDeferredQueue(DeferredQueue[_T]):

    closed: Union[twisted.python.failure.Failure, Exception] = ...

    def __init__(
        self,
        size: Optional[int] = ...,
        backlog: Optional[int] = ...,
    ) -> None: ...

    def put(self, obj: _T) -> None: ...
    def get(self) -> Deferred[_T]: ...
    def close(self, reason: Union[twisted.python.failure.Failure, Exception, str]) -> None: ...


# Generic [named] tuples aren't supported (https://github.com/python/mypy/issues/685)
# so we can't provide more specific type hints for `method`
class ReceivedMessage(NamedTuple):
    channel: TwistedChannel
    method: amqp_object.Method
    properties: spec.BasicProperties
    body: bytes



class TwistedChannel:

    on_closed: Deferred[Union[twisted.python.failure.Failure, Exception, str]]

    def __init__(self, channel: Channel) -> None: ...

    @property
    def channel_number(self) -> int: ...
    @property
    def connection(self) -> Connection: ...

    @property
    def is_closed(self) -> bool: ...
    @property
    def is_closing(self) -> bool: ...
    @property
    def is_open(self) -> bool: ...

    @property
    def flow_active(self) -> bool: ...
    @property
    def consumer_tags(self) -> List[str]: ...

    def callback_deferred(
        self,
        deferred: Deferred[Any],
        replies: Sequence[Any],
    ) -> None: ...

    # ReceivedMessage.method: spec.Basic.Return
    def add_on_return_callback(self, callback: Callable[[ReceivedMessage], None]) -> None: ...
    def basic_ack(self, delivery_tag: int = ..., multiple: bool = ...) -> None: ...
    def basic_cancel(self, consumer_tag: str = ...) -> None: ...


    # ReceivedMessage.method: spec.Basic.Deliver
    def basic_consume(
        self,
        queue: str,
        auto_ack: bool = ...,
        exclusive: bool = ...,
        consumer_tag: Optional[str] = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[Tuple[ClosableDeferredQueue[ReceivedMessage], str]]: ...

    # ReceivedMessage.method: spec.Basic.GetOk
    def basic_get(
        self,
        queue: str,
        auto_ack: bool = ...,
    ) -> Deferred[ReceivedMessage]: ...

    def basic_nack(
        self,
        delivery_tag: Optional[int] = ...,
        multiple: bool = ...,
        requeue: bool = ...,
    ) -> None: ...

    def basic_publish(
        self,
        exchange: str,
        routing_key: str,
        body: bytes | str,
        properties: Optional[spec.BasicProperties] = ...,
        mandatory: bool = ...,
    ) -> Deferred[None]: ...

    def basic_qos(
        self,
        prefetch_size: int = ...,
        prefetch_count: int = ...,
        global_qos: bool = ...,
    ) -> Deferred[frame.Method[spec.Basic.QosOk]]: ...

    def basic_reject(self, delivery_tag: int, requeue: bool = ...) -> None: ...
    def basic_recover(
        self, requeue: bool = ...
    ) -> Deferred[frame.Method[spec.Basic.RecoverOk]]: ...

    def close(self, reply_code: int = ..., reply_text: str = ...) -> None: ...
    def confirm_delivery(self) -> Deferred[frame.Method[spec.Confirm.SelectOk]]: ...

    def exchange_bind(
        self,
        destination: str,
        source: str,
        routing_key: str = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[frame.Method[spec.Exchange.BindOk]]: ...

    def exchange_declare(
        self,
        exchange: str,
        exchange_type: str = ...,
        passive: bool = ...,
        durable: bool = ...,
        auto_delete: bool = ...,
        internal: bool = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[frame.Method[spec.Exchange.DeclareOk]]: ...

    def exchange_delete(
        self,
        exchange: Optional[str] = ...,
        if_unused: bool = ...,
    ) -> Deferred[frame.Method[spec.Exchange.DeleteOk]]: ...

    def exchange_unbind(
        self,
        destination: Optional[str] = ...,
        source: Optional[str] = ...,
        routing_key: str = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[frame.Method[spec.Exchange.UnbindOk]]: ...

    def flow(self, active: bool) -> Deferred[frame.Method[spec.Channel.FlowOk]]: ...
    def open(self) -> None: ...

    def queue_bind(
        self,
        queue: str,
        exchange: str,
        routing_key: Optional[str] = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[frame.Method[spec.Queue.BindOk]]: ...

    def queue_declare(
        self,
        queue: str,
        passive: bool = ...,
        durable: bool = ...,
        exclusive: bool = ...,
        auto_delete: bool = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[frame.Method[spec.Queue.DeclareOk]]: ...

    def queue_delete(
        self,
        queue: str,
        if_unused: bool = ...,
        if_empty: bool = ...,
    ) -> Deferred[frame.Method[spec.Queue.DeleteOk]]: ...

    def queue_purge(self, queue: str) -> Deferred[frame.Method[spec.Queue.PurgeOk]]: ...

    def queue_unbind(
        self,
        queue: str,
        exchange: Optional[str] = ...,
        routing_key: Optional[str] = ...,
        arguments: Optional[Mapping[str, Any]] = ...,
    ) -> Deferred[frame.Method[spec.Queue.UnbindOk]]: ...

    def tx_commit(self) -> Deferred[frame.Method[spec.Tx.CommitOk]]: ...
    def tx_rollback(self) -> Deferred[frame.Method[spec.Tx.RollbackOk]]: ...
    def tx_select(self) -> Deferred[frame.Method[spec.Tx.SelectOk]]: ...


class TwistedProtocolConnection(twisted.internet.protocol.Protocol):

    ready: Deferred[TwistedProtocolConnection] = ...
    closed: Optional[Deferred[Union[twisted.python.failure.Failure, Exception]]] = ...

    def __init__(
        self,
        parameters: Optional[Parameters] = ...,
        custom_reactor: Optional[twisted.internet.base.ReactorBase] = ...,
    ) -> None: ...

    def channel(self, channel_number: Optional[int] = ...) -> Deferred[TwistedChannel]: ...

    @property
    def is_closed(self) -> bool: ...

    def close(
        self,
        reply_code: int = ...,
        reply_text: str = ...,
    ) -> Deferred[Exception]: ...

    # IProtocol methods

    def dataReceived(self, data: bytes) -> None: ...
    def connectionLost(self, reason: twisted.python.failure.Failure = ...) -> None: ...
    def makeConnection(self, transport: twisted.internet.interfaces.ITransport) -> None: ...

    # Our own methods

    def connectionReady(self) -> TwistedProtocolConnection: ...
