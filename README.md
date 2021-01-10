# SendGrid Email sender
A simple wrapper around SendGrid python library for sending emails. 

## Setup
Before using this library, there are two prerequisites.

First, you need to have SendGrid account. If you do not already have one, it 
can be registered [here](https://signup.sendgrid.com/).

Once you have an account, you will need and API key with at least a permission
to send emails (no other permissions are needed by this library). Relevant
SendGrid documentation is [here](https://sendgrid.com/docs/ui/account-and-settings/api-keys/).

This API key must be provided when instance of `EmailSender` is created and will
be used to authenticate to SendGrid API. 

In order for SendGrid to actually send emails, at lest one `from` address must
be validated, if not entire domain. Most simple way is to perform
[Single Sender Verification](https://sendgrid.com/docs/ui/sending-email/sender-verification/)
which will allow you to use single `from` email address as a source. Note that
if you fail to provide the same address to `EmailSender` class, it will fail
with `401 Forbidden` status code.

## Usage
Simply import EmailSender, create instance and start calling `send` method. 

```python
import os
from email_sender import EmailSender

sender = EmailSender(os.getenv('SENDGRID_API_KEY'), os.getenv('FROM_ADDRESS'))
sender.send(to_='me@example.com', subject='something happened',
            content='your attention is needed')
```

If email sending fails, `send` method will raise `EmailSendingException`. 

There is an async mode that can be used in order not to wait for SendGrid
response when email is sent. To use it, simply include `async_=True` parameter
when calling `send` method. In that case, `send` will return 
`concurrent.futures.Future` instance that can be used to check if request was
sent successfully. For async mode, thread pool is created and size of it can be
controlled via `max_workers` parameter when `EmailSender` is created. 

## Tool
In addition to using this project as a library in your project, it can be used
as command line tool as well. 

In order to use it as such, all the same prerequisites mentioned earlier
must be fulfilled. API key must be set in environment with name `SENDGRID_API_KEY`.
This can be done by using `.env` file, which the tool will read if it exists. 

To get more help, run `python tool.py --help`. 

## Development
Create virtual environment, install all requirements from `requirements-dev.txt`
and start developing. 

`pytest` is used for testing, so executing tests should be as simple as running
`pytest` command in project directory with relevant virtual environment activated.

## Todo
- [ ] Create `setup.py`
- [ ] Create entry point in `setup.py` so that tool can be installed in `PATH`
- [ ] Support multiple content types for same email


## Author
Bojan Delic <bojan@delic.in.rs>
