from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    

class Drone(models.Model):
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    quantity = models.DecimalField(max_digits=3, decimal_places=0)
    image = models.ImageField(upload_to='drone_img/')
    specifications = models.TextField()
    manufacturer = models.CharField(max_length=255)
    battery = models.CharField(max_length=255, null=True)
    connection = models.CharField(max_length=255, null=True)
    maximum_take_off_weight = models.CharField(max_length=255, null=True)
    flight_radius = models.IntegerField(null=True)
    maximum_flight_time  = models.IntegerField(null=True)
    cruising_speed  = models.IntegerField(null=True)
    iso = models.CharField(max_length=255, null=True)
    focal_length = models.IntegerField(null=True)
    field_of_view = models.IntegerField(null=True)
    size_of_the_image_sensor = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    POLAND = 'Poland'
    UKRAINE = 'Ukraine'

    COUNTRY = (
        (POLAND, 'Poland'),
        (UKRAINE, 'Ukraine')
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_order')
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name='drone_order')
    date = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=255, choices=COUNTRY, default=UKRAINE)
    city = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    number_of_phone = models.IntegerField(null=True)

    def __str__(self) -> str:
        return str(self.drone)
    

