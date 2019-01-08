from django.contrib import admin

# Register your models here.
from .models import Block, Activity, Place

admin.site.register(Block)
admin.site.register(Activity)
admin.site.register(Place)
