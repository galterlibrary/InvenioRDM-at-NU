"""Contact us views."""

from flask import (
    Blueprint, current_app, flash, redirect, render_template, url_for
)
from flask_wtf import FlaskForm
from invenio_mail.api import TemplatedMessage
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

blueprint = Blueprint(
    'contact_us',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""contact_us blueprint used to define templates and static folders."""


def strip_filter(text):
    """Trim whitespace."""
    return text.strip() if text else text


class ContactForm(FlaskForm):
    """Contact form."""

    name = StringField(
        'Your Name', filters=[strip_filter], validators=[DataRequired()]
    )
    email = StringField(
        'Your Email', filters=[strip_filter], validators=[DataRequired()]
    )
    subject = StringField(
        'Subject', filters=[strip_filter], validators=[DataRequired()]
    )
    message = TextAreaField(
        'Message', filters=[strip_filter], validators=[DataRequired()]
    )


# TODO: If useful enough, place in a new utilities module
def render_template_to_string(template, **kwargs):
    """Return rendered template read from filesystem."""
    template = current_app.jinja_env.get_or_select_template(template)
    return template.render(**kwargs)


@blueprint.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    """Provide form for questions/comments."""
    form = ContactForm()

    if form.validate_on_submit():

        current_app.jinja_env.add_extension("jinja2_time.TimeExtension")

        # Send email to site operators
        subject = render_template_to_string(
            current_app.config['CONTACT_US_SUPPORT_EMAIL_SUBJECT_TEMPLATE'],
            original_subject=form.subject.data
        )
        msg = TemplatedMessage(
            subject=subject,
            template_body=(
                current_app.config['CONTACT_US_SUPPORT_EMAIL_BODY_TEMPLATE_TXT']  # noqa
            ),
            template_html=(
                current_app.config['CONTACT_US_SUPPORT_EMAIL_BODY_TEMPLATE_HTML']  # noqa
            ),
            sender=(form.name.data, form.email.data),
            recipients=[
                (
                    current_app.config['CONTACT_US_RECIPIENT_NAME'],
                    current_app.config['CONTACT_US_RECIPIENT_EMAIL'],
                ),
            ],
            reply_to=(form.name.data, form.email.data),
            ctx={'poster': form.data}
        )
        current_app.extensions['mail'].send(msg)

        # Send confirmation to the original poster
        subject = render_template_to_string(
            current_app.config['CONTACT_US_CONFIRMATION_EMAIL_SUBJECT_TEMPLATE']  # noqa
        )

        msg = TemplatedMessage(
            subject=subject,
            template_body=(
                current_app.config['CONTACT_US_CONFIRMATION_EMAIL_BODY_TEMPLATE_TXT']  # noqa
            ),
            template_html=(
                current_app.config['CONTACT_US_CONFIRMATION_EMAIL_BODY_TEMPLATE_HTML']  # noqa
            ),
            sender=(
                current_app.config['CONTACT_US_SENDER_NAME'],
                current_app.config['CONTACT_US_SENDER_EMAIL']
            ),
            recipients=[(form.name.data, form.email.data)],
            ctx={}  # Needed because of Invenio bug.
                    # PR inveniosoftware/invenio-mail #44 sent.
        )
        current_app.extensions['mail'].send(msg)
        # TODO?: Add mailing error resiliency
        # TODO?: Make mailing asynchronous

        flash(
            "Thank you for contacting us. We will be in touch soon!",
            category='success'
        )

        return redirect(url_for('cd2hrepo_frontpage.index'))
    else:
        return render_template(
            'contact_us/contact_us.html',
            form=form,
        )
