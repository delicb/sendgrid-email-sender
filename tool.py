"""
Command line tool for sending emails via SendGrid.

In order for sending to work, SendGrid API key has to be set in environment
under name SENDGRID_API_KEY.
"""
import os
import sys
import argparse
import pydotenvs  # type: ignore
from email_sender import EmailSender, EmailSendingException

pydotenvs.load_env()

ENV_KEY_VAR = "SENDGRID_API_KEY"


def main(args):
    # verify for credentials, only in environment variables, since we do not
    # want it to be passed as command line arguments and be left in terminal
    # history
    api_key = os.getenv(ENV_KEY_VAR)
    if not api_key:
        print(f"{ENV_KEY_VAR} environment variable not set")
        sys.exit(1)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from",
        "-f",
        metavar="FROM",
        required=True,
        type=str,
        help="Source address. Must be registered and validated " "in SendGrid.",
        dest="from_email",
    )
    parser.add_argument(
        "--to",
        "-t",
        metavar="TO",
        required=True,
        type=str,
        help="Address to which to send an email.",
    )
    parser.add_argument(
        "--subject",
        "-s",
        metavar="SUBJECT",
        required=True,
        type=str,
        help="Subject of an email.",
    )
    parser.add_argument(
        "--content",
        "-c",
        metavar="CONTENT",
        required=True,
        type=str,
        help="Email content.",
    )
    parser.add_argument(
        "--content-type",
        metavar="CONTENT_TYPE",
        required=False,
        type=str,
        default="text/plain",
        help="Content type of provided body content.",
    )

    ns = parser.parse_args(args)

    sender = EmailSender(api_key=api_key, from_=ns.from_email)
    try:
        sender.send(
            to_=ns.to,
            subject=ns.subject,
            async_=False,
            content=ns.content,
            content_type=ns.content_type,
        )
    except EmailSendingException as e:
        print(f"Failed to send emails: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
