from django.http import JsonResponse

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.TOKEN = "xyz123"  # Token esperado en el header 'Authorization'

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != self.TOKEN:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        return self.get_response(request)
