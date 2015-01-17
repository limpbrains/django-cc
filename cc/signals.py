import django.dispatch


post_deposite = django.dispatch.Signal(providing_args=["instance"])
