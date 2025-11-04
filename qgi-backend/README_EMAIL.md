

## Welcome email
Add a new SendGrid **Dynamic Template** for welcome messages and set:
```
SG_TPL_WELCOME=d-<your-welcome-template-id>
```
The template should accept: `name`.
The backend calls `send_welcome_email(email, name)` right after a user is created.
