from django.shortcuts import render, redirect
from .models import Drone
from .forms import OrderForm

def home(request):
    return render(request, 'shop/index.html')


def product(request):
    drones = Drone.objects.all()
    context = {
        'drones': drones
        }
    return render(request, 'shop/product.html', context)


def detail_drone(request, pk):
    drone = Drone.objects.get(id=pk)

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            order.drone = drone
            order.save()
            return redirect('home')
    else:
        form = OrderForm()

    context = {
        'drone': drone,
        'form': form
    }
    return render(request, 'shop/detail.html', context)
