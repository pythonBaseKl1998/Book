from django.shortcuts import render

def base(request):
    return render(request,'book_app/base.html')
