from django.shortcuts import render, redirect

def login_required(function):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            print("%"*12121)
            return redirect('loginPage')
        return function(request, *args, **kwargs)
    return wrapper