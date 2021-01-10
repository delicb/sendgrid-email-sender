import pytest
from typing import List, Optional, Union, Mapping, Tuple, Any
from email_sender import EmailSender, EmailSendingException


DEF_API_KEY = "dummy"
DEF_FROM = "from@exaample.com"
DEF_TO = "to@example.com"
DEF_SUBJECT = "email subject"
DEF_CONTENT = "email content to be sent"
DEF_CONTENT_TYPE = "text/plain"


def test_init_args_applied():
    s = EmailSender(DEF_API_KEY, DEF_FROM)

    assert s._client.api_key == DEF_API_KEY, "API key not applied"
    assert s._from.email == DEF_FROM, "From address not applied"


def test_sync_email_send_success(mocker):
    sender, mock = _create_client(mocker)

    sender.send(to_=DEF_TO, subject=DEF_SUBJECT, content=DEF_CONTENT)

    _assert_client_call(mock)


def test_async_email_send(mocker):
    sender, mock = _create_client(mocker)

    future = sender.send(
        to_=DEF_TO,
        subject=DEF_SUBJECT,
        content=DEF_CONTENT,
        async_=True,
    )

    # wait for the future to finish
    future.result()

    _assert_client_call(mock)


def test_async_email_send_fail_exception(mocker):
    sender, _ = _create_client(mocker, exc=Exception("error"))

    future = sender.send(
        to_=DEF_TO, subject=DEF_SUBJECT, content=DEF_CONTENT, async_=True
    )
    with pytest.raises(EmailSendingException, match="error"):
        future.result()


def test_non200_status_code_email_send(mocker):
    sender, _ = _create_client(mocker, response_code=400)

    with pytest.raises(Exception):
        sender.send(
            to_=DEF_TO,
            subject=DEF_SUBJECT,
            content=DEF_CONTENT,
            async_=False,
        )


def test_email_send_exception(mocker):
    sender, _ = _create_client(mocker, exc=Exception("cause"))

    with pytest.raises(Exception, match="cause"):
        sender.send(
            to_=DEF_TO,
            subject=DEF_SUBJECT,
            content=DEF_CONTENT,
            async_=False,
        )


def test_multi_to_addresses(mocker):
    to_addresses = ["a@example.com", "b@example.com"]
    sender, mock = _create_client(mocker)
    sender.send(
        to_=to_addresses,
        subject=DEF_SUBJECT,
        content=DEF_CONTENT,
        async_=False,
    )
    _assert_client_call(mock, to_=to_addresses)


def test_non_default_content_type(mocker):
    content = "<b>html</b>"
    content_type = "text/html"

    sender, mock = _create_client(mocker)
    sender.send(
        to_=DEF_TO,
        subject=DEF_SUBJECT,
        content=content,
        content_type=content_type,
    )
    _assert_client_call(mock, content=content, content_type=content_type)


##############################################################################
# Section containing testing utilities, not tests themselves.
# Could be extracted to other file in the future.
##############################################################################


class _SendGridRequestBody:
    def __init__(self, mock_call):
        call_args, call_kwargs = mock_call
        self.request_body = (
            call_args[0]
            if len(call_args) == 1
            else call_kwargs.get("request_body", {})
        )

    @property
    def from_(self) -> Optional[str]:
        return self.request_body.get("from", {}).get("email", None)

    @property
    def subject(self) -> Optional[str]:
        return self.request_body.get("subject", None)

    @property
    def to_(self) -> Optional[Union[str, List[str]]]:
        # to is stored in "personalizations" key and hos form of
        # "personalizations": [{"to": [{"email": "me@foo.com"}]}],
        tos = [
            to
            for to in self.request_body.get("personalizations", [])
            if to.get("to", None)
        ]
        emails = []
        for to_ in tos:
            emails.extend([e.get("email", None) for e in to_.get("to", {})])
        return list(filter(None, emails))

    @property
    def content(self) -> Mapping[str, str]:
        return {
            v["type"]: v["value"] for v in self.request_body.get("content", [])
        }

    def assert_from(self, from_: str):
        assert from_ == self.from_, "unexpected from address"

    def assert_to(self, to_: Union[List[str], str]):
        assert to_ == self.to_, "unexpected list of email receiver addresses"

    def assert_subject(self, subject: str):
        assert subject == self.subject, "unexpected subject"

    def assert_content(self, content: str, content_type: str = "text/plain"):
        assert (
            content == self.content[content_type]
        ), f"unexpected content for content type {content_type}"


class _MockResponse:
    """Dummy mock http response class."""

    def __init__(self, status_code: int):
        self.status_code = status_code


def _create_client(
    mocker,
    response_code: int = 202,
    api_key: str = DEF_API_KEY,
    from_: str = DEF_FROM,
    exc: Exception = None,
) -> Tuple[EmailSender, Any]:
    sender = EmailSender(api_key, from_)
    mock = mocker.patch.object(sender, "_client")
    if not exc:
        mock.client.mail.send.post.return_value = _MockResponse(response_code)
    else:
        mock.client.mail.send.post.side_effect = exc

    return sender, mock


def _assert_client_call(
    mock: Any,
    from_: str = DEF_FROM,
    to_: Union[str, List[str]] = DEF_TO,
    subject: str = DEF_SUBJECT,
    content: str = DEF_CONTENT,
    content_type: str = DEF_CONTENT_TYPE,
) -> None:
    # check send is called only once
    mock.client.mail.send.post.called_once()
    # check it is called with all expected parameters
    req = _SendGridRequestBody(mock.client.mail.send.post.call_args_list[0])
    if isinstance(to_, str):
        req.assert_to([to_])
    else:
        req.assert_to(to_)
    req.assert_from(from_)
    req.assert_subject(subject)
    req.assert_content(content, content_type)
