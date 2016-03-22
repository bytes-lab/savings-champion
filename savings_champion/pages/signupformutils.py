from common.accounts.forms import SignUpForm
from pages.forms import ConciergeSignupForm


def get_post_form(post):
    if post.show_ratetracker_form or post.show_newsletter_form or post.show_ratealert_form or post.show_joint_form:
        return SignUpForm()
    if post.show_concierge_form:
        data = {'source' : post.slug}
        return ConciergeSignupForm(initial=data)
    return None