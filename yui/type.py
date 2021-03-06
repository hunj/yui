import inspect
from types import SimpleNamespace
from typing import (
    Any,
    Dict,
    List,
    NewType,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Union,
    cast as typing_cast,
)

if TYPE_CHECKING:
    from .bot import Bot as _Bot  # noqa

__all__ = (
    'AllChannelsError',
    'AppID',
    'Bot',
    'BotID',
    'BotLinkedNamespace',
    'Channel',
    'ChannelFromConfig',
    'ChannelsFromConfig',
    'ChannelID',
    'ChannelPurpose',
    'ChannelTopic',
    'Comment',
    'CommentID',
    'DirectMessageChannel',
    'DirectMessageChannelID',
    'DnDStatus',
    'File',
    'FileID',
    'FromChannelID',
    'FromID',
    'FromUserID',
    'MessageMessage',
    'MessageMessageEdited',
    'MessagePreviousMessage',
    'Namespace',
    'NoChannelsError',
    'PrivateChannel',
    'PrivateChannelID',
    'PublicChannel',
    'PublicChannelID',
    'Subteam',
    'SubteamID',
    'SubteamPrefs',
    'TeamID',
    'Ts',
    'UnixTimestamp',
    'UnknownChannel',
    'UnknownUser',
    'User',
    'UserID',
    'UserProfile',
    'cast',
    'is_container',
)

#: :type:`type` User ID type. It must start with 'U'.
UserID = NewType('UserID', str)

#: :type:`type` Public Channel ID type. It must start with 'C'.
PublicChannelID = NewType('PublicChannelID', str)

#: :type:`type` IM(as known as Direct Message) Channel ID type.
#: It must start with 'D'.
DirectMessageChannelID = NewType('DirectMessageChannelID', str)

#: :type:`type` Group(as known as Private Channel) ID type.
#: It must start with 'G'.
PrivateChannelID = NewType('PrivateChannelID', str)

ChannelID = Union[
    PublicChannelID,
    DirectMessageChannelID,
    PrivateChannelID,
]

#: :type:`type` File ID type. It must start with 'F'.
FileID = NewType('FileID', str)

Comment = NewType('Comment', dict)

#: :type:`type` Comment ID type.
CommentID = NewType('CommentID', str)

#: :type:`type` Type for slack event unique ID.
Ts = NewType('Ts', str)

#: :type:`type` Team ID type. It must start with 'T'.
TeamID = NewType('TeamID', str)

#: :type:`type` Sub-team ID type. It must start with 'S'.
SubteamID = NewType('SubteamID', str)

#: :type:`type` App ID type. IT must start with 'A'.
AppID = NewType('AppID', str)

#: :type:`type` Bot ID type. It must start with 'B'.
BotID = NewType('BotID', str)

#: :type:`type` Type for store UnixTimestamp.
UnixTimestamp = NewType('UnixTimestamp', int)


class AllChannelsError(Exception):
    pass


class NoChannelsError(Exception):
    pass


class Namespace(SimpleNamespace):
    """Typed Namespace."""

    def __init__(self, **kwargs) -> None:
        annotations = getattr(self, '__annotations__', {})
        for k, v in kwargs.items():
            t = annotations.get(k)
            if t:
                kwargs[k] = cast(t, v)

        super(Namespace, self).__init__(**kwargs)  # type: ignore


class ChannelTopic(Namespace):
    """Topic of Channel."""

    value: str
    creator: UserID
    last_set: UnixTimestamp


class ChannelPurpose(Namespace):
    """Purpose of Channel."""

    value: str
    creator: UserID
    last_set: UnixTimestamp


class BotLinkedNamespace(Namespace):
    """Bot-linked namespace."""

    _bot: '_Bot'


class FromID(BotLinkedNamespace):
    """.from_id"""

    @classmethod
    def from_id(cls, value: Union[str, Dict]):
        raise NotImplementedError()


class FromChannelID(FromID):
    """.from_id"""

    @classmethod
    def from_id(cls, value: Union[str, Dict], raise_error: bool = False):
        if isinstance(value, str):
            if value.startswith('C'):
                for c in cls._bot.channels:
                    if c.id == value:
                        return c
            elif value.startswith('D'):
                for d in cls._bot.ims:
                    if d.id == value:
                        return d
            elif value.startswith('G'):
                for g in cls._bot.groups:
                    if g.id == value:
                        return g
            if not raise_error:
                return UnknownChannel(id=value)
            raise KeyError('Given ID was not found.')
        return cls(**value)

    @classmethod
    def from_name(cls, name: str):
        for c in cls._bot.channels:
            if c.name == name:
                return c
        for g in cls._bot.groups:
            if g.name == name:
                return g
        raise KeyError('Channel was not found')

    @classmethod
    def from_config(cls, key: str)\
            -> Union['PrivateChannel', 'PublicChannel']:
        channel_name = cls._bot.config.CHANNELS[key]
        if isinstance(channel_name, str):
            return cls.from_name(channel_name)
        raise ValueError(f'{key} in CHANNELS is not str.')

    @classmethod
    def from_config_list(cls, key: str)\
            -> List[Union['PrivateChannel', 'PublicChannel']]:
        channels = cls._bot.config.CHANNELS[key]
        if not channels:
            raise NoChannelsError()
        if channels == ['*'] or channels == '*':
            raise AllChannelsError()
        if isinstance(channels, list):
            return [cls.from_name(x) for x in channels]
        raise ValueError(f'{key} in CHANNELS is not list.')


class Channel(FromChannelID):

    id: str
    created: UnixTimestamp
    is_org_shared: bool
    has_pins: bool
    last_read: Ts


class PublicChannel(Channel):

    name: str
    is_channel: bool
    is_archived: bool
    is_general: bool
    unlinked: int
    creator: UserID
    name_normalized: str
    is_shared: bool
    is_member: bool
    is_private: bool
    is_mpim: bool
    members: List[UserID]
    topic: ChannelTopic
    purpose: ChannelPurpose
    previous_names: List[str]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class DirectMessageChannel(Channel):

    is_im: bool
    user: UserID
    last_read: Ts
    is_open: bool

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, user={self.user!r})'


class PrivateChannel(Channel):

    name: str
    is_group: bool
    creator: UserID
    is_archived: bool
    members: List[UserID]
    topic: ChannelTopic
    purpose: ChannelPurpose

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class UnknownChannel(Channel):
    pass


class ChannelFromConfig:
    """Lazy loading helper to get channel from config"""

    def __init__(self, key: str) -> None:
        self.key = key

    def get(self) -> Union[PrivateChannel, PublicChannel]:
        return Channel.from_config(self.key)


class ChannelsFromConfig:
    """Lazy loading helper to get list of channels from config"""

    def __init__(self, key: str) -> None:
        self.key = key

    def get(self) -> List[Union[PrivateChannel, PublicChannel]]:
        return Channel.from_config_list(self.key)


class FromUserID(FromID):

    @classmethod
    def from_id(cls, value: Union[str, Dict], raise_error: bool = False):
        if isinstance(value, str):
            value = typing_cast(UserID, value)
            if value.startswith('U') and value in cls._bot.users:
                return cls._bot.users[value]
            if not raise_error:
                return UnknownUser(id=value)
            raise KeyError('Given ID was not found.')
        return cls(**value)

    @classmethod
    def from_name(cls, name: str):
        for c in cls._bot.users.values():
            if c.name == name:
                return c
        raise KeyError('Channel was not found')


class UserProfile(Namespace):
    """Profile of User."""

    first_name: str
    last_name: str
    avatar_hash: str
    title: str
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    email: str
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    team: TeamID


class User(FromUserID):

    id: str
    team_id: TeamID
    name: str
    deleted: bool
    color: str
    real_name: str
    tz: str
    tz_label: str
    tz_offset: int
    profile: UserProfile
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_bot: bool
    updated: UnixTimestamp
    is_app_user: bool
    has_2fa: bool
    locale: str
    presence: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class UnknownUser(FromUserID):

    id: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r})'


class Bot(Namespace):
    """Bot."""

    id: BotID
    app_id: AppID
    name: str
    icons: Dict[str, str]


class DnDStatus(Namespace):
    """DnD status."""

    dnd_enabled: bool
    next_dnd_start_ts: UnixTimestamp
    next_dnd_end_ts: UnixTimestamp
    snooze_enabled: Optional[bool]
    snooze_endtime: Optional[UnixTimestamp]


class File(Namespace):
    """https://api.slack.com/types/file"""

    id: FileID


class SubteamPrefs(Namespace):
    """Prefs of Subteam."""

    channels: List
    groups: List


class Subteam(Namespace):
    """https://api.slack.com/types/usergroup"""

    id: SubteamID
    team_id: TeamID
    is_usergroup: bool
    name: str
    description: str
    handle: str
    is_external: bool
    date_create: UnixTimestamp
    date_update: UnixTimestamp
    date_delete: UnixTimestamp
    auto_type: str
    created_by: UserID
    updated_by: Optional[UserID]
    deleted_by: Optional[UserID]
    perfs: SubteamPrefs
    users: List[UserID]
    user_count: str


class MessageMessageEdited(Namespace):
    """edited attr in MessageMessage."""

    user: UserID
    ts: Ts


class MessageMessage(Namespace):
    """Message in Message."""

    type: str
    text: str
    user: UserID
    ts: Ts
    edited: Optional[MessageMessageEdited]


class MessagePreviousMessage(MessageMessage):
    """Previous message in Message."""


NoneType = type(None)
UnionType = type(Union)


KNOWN_TYPES = {
    bytes,
    float,
    int,
    str,
}


class CastError(Exception):
    pass


class BaseCaster:

    def check(self, t, value):
        raise NotImplementedError

    def cast(self, caster, t, value):
        raise NotImplementedError


class Caster:

    def __init__(self, caster: List[BaseCaster]) -> None:
        self.caster = caster

    def __call__(self, t, value):
        try:
            return self.cast(t, value)
        except CastError:
            return t(value)

    def sort(self, types, value):
        return [
            t for t in types for c in self.caster
            if c.check(t, value)
        ]

    def cast(self, t, value):
        for caster in self.caster:
            if caster.check(t, value):
                return caster.cast(self, t, value)
        raise CastError


class BoolCaster(BaseCaster):

    def check(self, t, value):
        return t == bool

    def cast(self, caster, t, value):
        return t(value)


class KnownTypesCaster(BaseCaster):

    def check(self, t, value):
        if t in KNOWN_TYPES and value is not None:
            try:
                t(value)
            except ValueError:
                return False
            return True
        return False

    def cast(self, caster, t, value):
        return t(value)


class TypeVarCaster(BaseCaster):

    def check(self, t, value):
        return isinstance(t, TypeVar)

    def cast(self, caster, t, value):
        if t.__constraints__:
            types = caster.sort(t.__constraints__)
            for ty in types:
                try:
                    return caster.cast(ty, value)
                except CastError:
                    continue
            raise CastError
        else:
            return value


class NewTypeCaster(BaseCaster):

    def check(self, t, value):
        return hasattr(t, '__supertype__')

    def cast(self, caster, t, value):
        return caster.cast(t.__supertype__, value)


class AnyCaster(BaseCaster):

    def check(self, t, value):
        return t == Any

    def cast(self, caster, t, value):
        return value


class UnionCaster(BaseCaster):

    def check(self, t, value):
        return getattr(t, '__origin__', None) == Union

    def cast(self, caster, t, value):
        types = caster.sort(t.__args__, value)
        for ty in types:
            try:
                return caster.cast(ty, value)
            except CastError:
                continue
        raise ValueError


class TupleCaster(BaseCaster):

    def check(self, t, value):
        return getattr(t, '__origin__', None) == tuple

    def cast(self, caster, t, value):
        if t.__args__:
            return tuple(
                caster.cast(ty, x) for ty, x in zip(t.__args__, value)
            )
        else:
            return tuple(value)


class SetCaster(BaseCaster):

    def check(self, t, value):
        return getattr(t, '__origin__', None) == set

    def cast(self, caster, t, value):
        if t.__args__:
            return {caster.cast(t.__args__[0], x) for x in value}
        else:
            return set(value)


class ListCaster(BaseCaster):

    def check(self, t, value):
        return getattr(t, '__origin__', None) == list

    def cast(self, caster, t, value):
        if t.__args__:
            return [caster.cast(t.__args__[0], x) for x in value]
        else:
            return list(value)


class DictCaster(BaseCaster):

    def check(self, t, value):
        return getattr(t, '__origin__', None) == dict

    def cast(self, caster, t, value):
        if t.__args__:
            return {
                caster.cast(t.__args__[0], k): caster.cast(t.__args__[1], v)
                for k, v in value.items()
            }
        else:
            return dict(value)


class FromIDCaster(BaseCaster):

    def check(self, t, value):
        return inspect.isclass(t) and issubclass(t, FromID)

    def cast(self, caster, t, value):
        return t.from_id(value)


class NamespaceCaster(BaseCaster):

    def check(self, t, value):
        return inspect.isclass(t) and issubclass(t, Namespace)

    def cast(self, caster, t, value):
        return t(**value)


class NoHandleCaster(BaseCaster):

    def check(self, t, value):
        try:
            return isinstance(value, t)
        except TypeError:
            return False

    def cast(self, caster, t, value):
        return value


class NoneTypeCaster(BaseCaster):

    def check(self, t, value):
        return t == NoneType  # type: ignore

    def cast(self, caster, t, value):
        return None


cast = Caster([
    NoHandleCaster(),
    BoolCaster(),
    KnownTypesCaster(),
    AnyCaster(),
    TypeVarCaster(),
    NewTypeCaster(),
    UnionCaster(),
    TupleCaster(),
    SetCaster(),
    ListCaster(),
    DictCaster(),
    FromIDCaster(),
    NamespaceCaster(),
])


CONTAINER = (set, tuple, list)


def is_container(t) -> bool:
    """Check given value is container type?"""

    if hasattr(t, '__origin__'):
        return t.__origin__ in CONTAINER

    return t in CONTAINER
