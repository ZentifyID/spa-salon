from django.contrib import admin

from .models import Master, MasterDayOff, MasterSchedule


class MasterScheduleInline(admin.TabularInline):
    model = MasterSchedule
    extra = 0


class MasterDayOffInline(admin.TabularInline):
    model = MasterDayOff
    extra = 0


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ("full_name", "is_active", "has_photo")
    list_filter = ("is_active", "services")
    search_fields = ("full_name",)
    filter_horizontal = ("services",)
    inlines = (MasterScheduleInline, MasterDayOffInline)

    @admin.display(description="Фото")
    def has_photo(self, obj):
        return bool(obj.photo)


@admin.register(MasterSchedule)
class MasterScheduleAdmin(admin.ModelAdmin):
    list_display = ("master", "weekday", "work_start", "work_end", "is_working_day")
    list_filter = ("weekday", "is_working_day")
    search_fields = ("master__full_name",)


@admin.register(MasterDayOff)
class MasterDayOffAdmin(admin.ModelAdmin):
    list_display = ("master", "date", "reason")
    list_filter = ("date",)
    search_fields = ("master__full_name", "reason")
