# myapp/middleware.py
from django.http import HttpResponsePermanentRedirect


class PA2FlyRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if any(path.startswith(prefix) for prefix in ["/admin", "/api", "/auth", "/static", "/media", "/account"]):
            return self.get_response(request)

        host = request.get_host().partition(":")[0]
        if host in [
            # "127.0.0.1",
            "oneprep.pythonanywhere.com",
        ]:
            return HttpResponsePermanentRedirect("https://oneprep.fly.dev" + request.get_full_path())
        else:
            return self.get_response(request)
