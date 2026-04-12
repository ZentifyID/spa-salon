from datetime import datetime, timedelta

from django.utils import timezone

from apps.booking.models import Appointment
from apps.masters.models import Master
from apps.services.models import Service

SLOT_STEP_MINUTES = 15


def _to_aware_local(date_value, time_value):
    naive_dt = datetime.combine(date_value, time_value)
    return timezone.make_aware(naive_dt, timezone.get_current_timezone())


def _iter_slots(start_dt, end_dt, step_minutes):
    current = start_dt
    step = timedelta(minutes=step_minutes)
    while current <= end_dt:
        yield current
        current += step


def get_master_schedule_for_date(master: Master, date_value):
    if master.days_off.filter(date=date_value).exists():
        return None

    weekday = date_value.weekday()
    schedule = master.schedules.filter(weekday=weekday, is_working_day=True).first()
    return schedule


def get_master_busy_intervals(master: Master, date_value, exclude_appointment_id=None):
    appointments = (
        Appointment.objects.filter(
            master=master,
            appointment_at__date=date_value,
            status__in=[Appointment.Status.NEW, Appointment.Status.CONFIRMED],
        )
        .exclude(pk=exclude_appointment_id)
        .select_related("service")
    )

    intervals = []
    for appt in appointments:
        start = appt.appointment_at
        end = start + timedelta(minutes=appt.service.duration_minutes)
        intervals.append((start, end))
    return intervals


def is_interval_free(start_dt, end_dt, busy_intervals):
    for busy_start, busy_end in busy_intervals:
        if busy_start < end_dt and busy_end > start_dt:
            return False
    return True


def get_available_slots(master: Master, service: Service, date_value):
    today = timezone.localdate()
    if date_value < today:
        return []

    schedule = get_master_schedule_for_date(master, date_value)
    if not schedule:
        return []

    work_start = _to_aware_local(date_value, schedule.work_start)
    work_end = _to_aware_local(date_value, schedule.work_end)
    duration = timedelta(minutes=service.duration_minutes)
    last_possible_start = work_end - duration
    if last_possible_start < work_start:
        return []

    now_local = timezone.localtime()
    slot_start = work_start
    if date_value == now_local.date():
        min_start = now_local.replace(second=0, microsecond=0)
        remainder = min_start.minute % SLOT_STEP_MINUTES
        if remainder:
            min_start += timedelta(minutes=SLOT_STEP_MINUTES - remainder)
        if min_start > slot_start:
            slot_start = min_start

    busy_intervals = get_master_busy_intervals(master, date_value)

    slots = []
    for candidate in _iter_slots(slot_start, last_possible_start, SLOT_STEP_MINUTES):
        candidate_end = candidate + duration
        if is_interval_free(candidate, candidate_end, busy_intervals):
            slots.append(candidate)
    return slots


def validate_master_slot(master: Master, service: Service, start_dt, exclude_appointment_id=None):
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())

    schedule = get_master_schedule_for_date(master, start_dt.date())
    if not schedule:
        return False, "У мастера нет рабочего графика на выбранную дату."

    work_start = _to_aware_local(start_dt.date(), schedule.work_start)
    work_end = _to_aware_local(start_dt.date(), schedule.work_end)
    end_dt = start_dt + timedelta(minutes=service.duration_minutes)

    if start_dt < work_start or end_dt > work_end:
        return False, "Время выходит за рамки рабочего графика мастера."

    busy_intervals = get_master_busy_intervals(
        master,
        start_dt.date(),
        exclude_appointment_id=exclude_appointment_id,
    )
    if not is_interval_free(start_dt, end_dt, busy_intervals):
        return False, "Этот мастер уже занят в выбранный промежуток времени."

    return True, ""
