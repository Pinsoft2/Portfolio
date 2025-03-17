from django.shortcuts import render, redirect
from django.http import HttpResponse
from .project import main
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User
from .models import UploadedDocument
from django.http import JsonResponse


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("jj_no_fish"))
        else:
            return render(request, "capstone/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "capstone/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("jj_no_fish"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "capstone/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "capstone/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("jj_no_fish"))
    else:
        return render(request, "capstone/register.html")

def jj_no_fish(request):
    try:
        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'Upload & Replace' and 'document' in request.FILES:
                old_words = request.POST.getlist('old_word')
                new_words = request.POST.getlist('new_word')
                word_pairs = dict(zip(old_words, new_words))
                user = request.user

                # Process document
                context = main(action, request, word_pairs, user)

                # Check if it's an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'original_preview': context.get('original_preview', ''),
                        'modified_preview': context.get('modified_preview', ''),
                        'upload_completed': True
                    })

                return render(request, 'capstone/jj_no_fish.html', context)

            elif action == 'Export':
                context = main(action, request)
                modified_doc = context.get('modified_doc')
                new_file_name = context.get('new_file_name')
                response = HttpResponse(
                    modified_doc,
                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = f'attachment; filename="{new_file_name}"'
                return response

        # For GET requests, bypass the main() call for debugging
        # context = main('jj_no_fish', request)  # This line is likely causing the error
        context = {'debug_message': 'Main function call bypassed for debugging'}
        return render(request, 'capstone/jj_no_fish.html', context)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return HttpResponse(f"<h1>Error in view:</h1><p>{str(e)}</p><pre>{error_details}</pre>")

def history(request, user_id):

    profile_user = User.objects.get(id=user_id)
    # Get the posts of the user
    histories = UploadedDocument.objects.filter(user=profile_user)
    histories =  histories.order_by("-created_time").all()
    return render(request, 'capstone/history.html', {"histories": histories})


def debug_view(request):
    return HttpResponse("Debug view is working!")