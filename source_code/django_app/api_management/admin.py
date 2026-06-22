from django.contrib import admin

from .models import APIKey, APIUsageLog, ChannelPartner, WebhookEndpoint

admin.site.register(ChannelPartner)
admin.site.register(APIKey)
admin.site.register(APIUsageLog)
admin.site.register(WebhookEndpoint)
