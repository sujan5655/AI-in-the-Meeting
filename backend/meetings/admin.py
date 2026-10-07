from django.contrib import admin

# Register your models here.
from .models import Topic,TranscriptSegment,Meeting


admin.site.register(Topic)
admin.site.register(TranscriptSegment)
admin.site.register(Meeting)