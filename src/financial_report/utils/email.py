import base64
import json
import os
from datetime import datetime as dt

import requests
from dotenv import load_dotenv
from utils import file_system as fs


class User:
    """
    `User` represents a user with an email and name.

    Attributes
    ----------
    email : str
        The email address of the user.
    name : str
        The name of the user.

    Methods
    -------
    to_dict()
        Returns a dictionary of the user
    to_json()
        Returns a JSON representation of the user.
    from_dict(data)
        Creates a new User instance from a dictionary.
    from_json(json_str)
        Creates a new User instance from a JSON string.

    """

    def __init__(self, email, name):
        self.email = email
        self.name = name

    def to_dict(self):
        """
        `to_dict` returns a dictionary representation of the user.

        Returns
        -------
        dict
            A dictionary containing the email and name of the user.

        """

        return {"email": self.email, "name": self.name}

    def to_json(self):
        """
        `to_json` returns a JSON representation of the user.

        Returns
        -------
        str
            JSON string containing the email and name of the user.

        """

        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        """
        `from_dict` returns a new User instance from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary containing the email and name of the user.

        Returns
        -------
        User
            A new User instance with the email and name specified in the
            dictionary.

        """

        return cls(email=data["email"], name=data["name"])

    @classmethod
    def from_json(cls, json_str):
        """
        `from_json` returns a new User instance from a JSON string.

        Parameters
        ----------
        json_str : str
            A JSON string containing the email and name of the user.

        Returns
        -------
        User
            A new User instance with the email and name specified in the JSON
            string.

        """

        data = json.loads(json_str)
        return cls.from_dict(data)


class Attachment():
    """
    `Attachment` represents an email attachment.

    Attributes
    ----------
    content : str
        The Base64 encoded content of the attachment.
    filename : str
        The filename of the attachment.
    type : str
        The MIME type of the attachment's content (e.g., "text/plain",
        "text/html")
    disposition : str, optional
        The content-disposition of the attachment, specifying how it is
        displayed (e.g., `inline` the attachment is displayed within the
        message, `attachment` the attachment is downloadable). The default is
        `attachment`.
    content_id : str
        The content ID of the attachment. This is used when the disposition is
        set to `inline` and it is a reference to the attachment in the message.

    Methods
    -------
    to_dict()
        Returns a dictionary of the attachment
    to_json()
        Returns a JSON representation of the attachment

    """

    def __init__(self, content, filename, type, disposition='attachment',
                 content_id=None):
        self.content = content
        self.filename = filename
        self.type = type
        self.disposition = disposition
        self.content_id = content_id

    def to_dict(self):
        """
        `to_dict` returns a dictionary representation of the attachment.

        Returns
        -------
        dict
            A dictionary containing the content, filename, type, disposition,
            and content ID of the attachment.

        """

        return {"content": self.content,
                "filename": self.filename,
                "type": self.type,
                "disposition": self.disposition,
                "content_id": self.content_id}

    def to_json(self):
        """
        `to_json` returns a JSON representation of the attachment

        Returns
        -------
        str
            JSON string containing the content, filename, type, disposition,
            and content ID of the attachment.

        """

        return json.dumps(self.to_dict())


class Email():
    """
    `Email` represents an email with a sender, recipients, attachments,
    subject, text content, html content, and category.

    Attributes
    ----------
    to : list of User
        A list of users to whom the email is sent
    fromm : list of User
        A user from whom the email is sent
    attachments : list of Attachment
        A list of attachments
    subject : str
        Subject of the email
    text : str
        Text content of the email
    html : str
        HTML content of the email
    category : str
        Category of the email (e.g., `Important`, `Social`)

    Methods
    -------
    to_dict()
        Returns a dictionary of the Email
    to_json()
        Returns a JSON representation of the Email

    """

    def __init__(self, to, fromm, attachment, subject, text, html, category):
        self.to = to
        self.fromm = fromm
        self.attachment = attachment
        self.subject = subject
        self.text = text
        self.html = html
        self.category = category

    def to_dict(self):
        """
        `to_dict` returns a dictionary representation of the Email

        Returns
        -------
        dict
            A dictionary containing the sender, recipients, attachments,
            subject, text content, html content, and category.

        """

        attachment_dict = [att.to_dict() for att in self.attachment]
        return {"to": self.to,
                "from": self.fromm.to_dict(),
                "attachments": attachment_dict,
                "subject": self.subject,
                "text": self.text,
                "html": self.html,
                "category": self.category}

    def to_json(self):
        """
        `to_json` returns a JSON representation of the Email

        Returns
        -------
        str
            A JSON string containing the sender, recipients, attachments,
            subject, text content, html content, and category..

        """

        return json.dumps(self.to_dict())


def send(port):

    # Set email address
    email_from = User('finance@panpancorp.com', 'Finance - Panpan Corp')
    email_to = port.users

    # Set attachments
    file = f'../../resources/{port.parent_dir}/logo/panpan_corp_new.png'
    with open(file, "rb") as f:
        content_1 = base64.b64encode(f.read()).decode('ascii')
    att_1 = Attachment(content_1,
                       'logo.png',
                       'image/png',
                       'inline',
                       'logo')

    ym = dt.today().strftime('%Y-%m')
    file = f'../../resources/{port.parent_dir}/{port.output_file}_{ym}.pdf'
    with open(file, "rb") as f:
        content_2 = base64.b64encode(f.read()).decode('ascii')
    att_2 = Attachment(content_2,
                       f'{port.output_file}_{ym}.pdf',
                       "application/pdf")

    att = [att_1, att_2]

    # Loop through all email addresses registered in this portfolio
    for user in (email_to):
        # Set HTML message
        html = fs.load_template().format(f'{user["name"]}',
                                         dt.now().strftime('%B'),
                                         dt.now().year)

        # Compose email
        email = Email([user],
                      email_from,
                      att,
                      f'Financial Report {ym}',
                      text_tmpl(),
                      html,
                      "Finance")

        # Load environmental variables
        load_dotenv()
        api_token = os.environ.get("api_token")

        url = "https://send.api.mailtrap.io/api/send"
        payload = email.to_dict()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Api-Token": api_token
        }
        response = requests.post(url, json=payload, headers=headers)

        print(response.json())


def text_tmpl():

    return (
        """
        <img src='cid:logo'>

        Hello, {}!

        This is your monthly portfolio analysis for the month of {}, {}.



        Regards,
        Finance - Panpan Corp.
        """
    )
