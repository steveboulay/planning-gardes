from django.contrib import admin

from schedules.models import DayOffRequest, Shift, StaffMember


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ["code", "full_name"]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ["staff", "start", "end", "kind"]
    list_filter = ["kind", "staff"]


@admin.register(DayOffRequest)
class DayOffRequestAdmin(admin.ModelAdmin):
    list_display = ["staff", "day"]
