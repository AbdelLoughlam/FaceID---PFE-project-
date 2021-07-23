from typing import Any, Union

from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from recognition.camera import FaceDetect
from django.shortcuts import render
################
################
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView

from .forms import SignUpForm


# Create your views here.
def index(request):
    request.session['model'] = 'false'
    return render(request, 'recognition/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('accounts/login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup_form.html', {'form': form})


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)


class LoginView(FormView):
    form_class = SignUpForm  # instance
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse('face_recognition:index')


class UserRegisterView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup_form.html'
    success_url = reverse_lazy('index')


def gen(request, camera):
    bol: Union[bool, Any] = request.session['model'] == 'true'
    while bol:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    camera.vs.stop()


@login_required
def facecam_feed(request):
    # cam_Obj = request.session['face_Obj']
    request.session['model'] = 'true'
    return StreamingHttpResponse(gen(request, FaceDetect()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


@login_required
def start_training(request):
    # request.session['face_Obj'] = FaceDetect()
    return render(request, 'accounts/detect_face.html')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
