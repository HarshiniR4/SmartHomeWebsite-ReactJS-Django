from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Session)
def on_session_begin(sender, session, **kwargs):
    # Delete other sessions for the same user
    user_sessions = Session.objects.filter(users=session.user).exclude(session_key=session.session_key)
    user_sessions.delete()
