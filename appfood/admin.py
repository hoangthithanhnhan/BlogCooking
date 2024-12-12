from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Recipe)
admin.site.register(RecipeImage)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Notification)
admin.site.register(UserProfile)


categories = ['Món Ăn Vặt', 'Chay', 'Món Á', 'Món Âu', 'Nướng', 'Khai Vị', 'Tráng Miện']

for category in categories:
    Classify.objects.get_or_create(name=category)


