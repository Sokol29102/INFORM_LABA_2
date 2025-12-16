from django.shortcuts import render, redirect
from .models import Drone
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import redirect_to_login



def home(request):
    return render(request, 'shop/index.html')


def product(request):
    drones = Drone.objects.all()
    context = {
        'drones': drones
        }
    return render(request, 'shop/product.html', context)


def detail_drone(request, pk):
    drone = get_object_or_404(Drone, id=pk)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            order.drone = drone
            order.save()
            return redirect("home")
    else:
        form = OrderForm()

    return render(request, "shop/detail.html", {"drone": drone, "form": form})
