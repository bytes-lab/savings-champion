from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


@csrf_exempt
def check_duplicate_email(request):
    message = ""
    if request.is_ajax():
        if request.method == 'POST':
            if User.objects.filter(email=request.POST["email"]).exists():
                if not User.objects.filter(email=request.POST["email"])[0].profile.skeleton_user:
                    message = "false"
                else:
                    message = "true"
            else:
                message = "true"
    return HttpResponse(message)