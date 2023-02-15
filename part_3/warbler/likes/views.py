from flask import (render_template, request, flash, redirect, g, abort, Blueprint)


from warbler.database import db
from warbler.users.models import User
from warbler.messages.models import Message


likes_views = Blueprint('likes_views', __name__,
                        template_folder='templates')

@likes_views.get('/users/<int:user_id>/likes')
def show_likes(user_id):
    """Show likes page for given user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('likes.html', user=user)


@likes_views.post('/messages/<int:message_id>/like')
def toggle_like(message_id):
    """Toggle a liked message for the currently-logged-in user.

    Redirect to location user originally came from on success.
    """

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    liked_message = Message.query.get_or_404(message_id)

    # Identify the url the user is coming from via the hidden input. We can
    # redirect them back to this location for a better user experience. Added
    # the default of "/" so the app doesn't crash in the event that a template is
    # added/changed and someone forgets to include that hidden input element.
    redirection_url = request.form.get("came_from", "/")

    if liked_message.user_id == g.user.id:
        return abort(403)

    if liked_message in g.user.liked_messages:
        g.user.liked_messages.remove(liked_message)
    else:
        g.user.liked_messages.append(liked_message)

    db.session.commit()

    return redirect(redirection_url)
