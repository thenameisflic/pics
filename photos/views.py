from django.shortcuts import render
from django.http import HttpResponse
from .models import Photo

def index(request):
    latest_photos = Photo.objects.order_by('-uploaded_at')
    context = {'latest_photos': latest_photos}
    return render(request, 'photos/index.html', context)
