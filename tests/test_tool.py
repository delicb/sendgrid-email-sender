import os
import pytest
from email_sender import EmailSendingException

import tool


def test_api_key_as_env_required(capsys):
    # ensure that there is environment variable set
    del os.environ["SENDGRID_API_KEY"]
    with pytest.raises(SystemExit):
        tool.main([])
        # check if error message is similar to what we expect
        out = capsys.readstdout()
        assert (
            "environment variable" in out.lower()
        ), "unexpected error message"


@pytest.mark.parametrize(
    "cmdargs",
    [
        ["--from", "from", "--to", "to", "--subject", "subject"],
        ["--from", "from", "--to", "to", "--content", "content"],
        ["--from", "from", "--subject", "subject", "--content", "content"],
        ["--to", "to", "--subject", "subject", "--content", "content"],
    ],
    ids=("missing content", "missing subject", "missing to", "missing from"),
)
def test_argument_parsing(capsys, cmdargs):
    # ensure there is api key set
    os.environ["SENDGRID_API_KEY"] = "dummy"

    with pytest.raises(SystemExit):
        tool.main([cmdargs])
        out = capsys.readstdout()
        assert (
            "the following arguments are required" in out.lower()
        ), "unexpected error message"


def test_email_sending_exception(capsys, mocker):
    # endure there is an api key set
    os.environ["SENDGRID_API_KEY"] = "dummy"

    mock = mocker.patch("tool.EmailSender")
    mock().send.side_effect = EmailSendingException

    # except tool to exit since it received exception
    with pytest.raises(SystemExit):
        tool.main(
            [
                "--from",
                "from",
                "--to",
                "to",
                "--subject",
                "subject",
                "--content",
                "content",
                "--content-type",
                "custom-content-type",
            ]
        )
        out = capsys.readstdout()
        assert "failed to send emails" in out.lower()


def test_success(mocker):
    # ensure there is as api key set
    os.environ["SENDGRID_API_KEY"] = "dummy"

    mock = mocker.patch("tool.EmailSender")
    tool.main(
        [
            "--from",
            "from",
            "--to",
            "to",
            "--subject",
            "subject",
            "--content",
            "content",
            "--content-type",
            "custom-content-type",
        ]
    )

    # check if instance was created
    mock.assert_called_with(api_key="dummy", from_="from")
    # get mock object
    obj = mock()
    # check send is called with expected parameters
    obj.send.assert_called_with(
        async_=False,
        to_="to",
        subject="subject",
        content="content",
        content_type="custom-content-type",
    )
