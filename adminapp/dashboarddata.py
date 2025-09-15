from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils import timezone

from customeruserapp.models import *

def get_monthly_user_stats():
    today = timezone.now()

    # Current month start
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Next month start (to use as current_month_end)
    next_month = (current_month_start.month % 12) + 1
    next_month_year = current_month_start.year + (1 if next_month == 1 else 0)
    current_month_end = current_month_start.replace(year=next_month_year, month=next_month)

    # Last month start and end
    last_month_end = current_month_start
    last_month = (current_month_start.month - 1) or 12
    last_month_year = current_month_start.year - (1 if current_month_start.month == 1 else 0)
    last_month_start = last_month_end.replace(year=last_month_year, month=last_month, day=1)

    # Count users
    last_month_count = ShopperUsers.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=last_month_end
    ).count()

    this_month_count = ShopperUsers.objects.filter(
        created_at__gte=current_month_start,
        created_at__lt=current_month_end
    ).count()

    # Default values
    percentage_change = "0%"
    trend = "flat"

    if last_month_count == 0 and this_month_count > 0:
        percentage_change = "+100%"
        trend = "up"
    elif last_month_count == 0 and this_month_count == 0:
        percentage_change = "0%"
        trend = "flat"
    else:
        change = ((this_month_count - last_month_count) / last_month_count) * 100
        if change > 0:
            percentage_change = f"+{round(change, 2)}%"
            trend = "up"
        elif change < 0:
            percentage_change = f"{round(change, 2)}%"
            trend = "down"
        else:
            percentage_change = "0%"
            trend = "flat"

    return percentage_change, trend


def get_monthly_spent_stats():
    today = timezone.now()

    # Current month start
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Next month start
    next_month = (current_month_start.month % 12) + 1
    next_month_year = current_month_start.year + (1 if next_month == 1 else 0)
    current_month_end = current_month_start.replace(year=next_month_year, month=next_month)

    # Last month start and end
    last_month_end = current_month_start
    last_month = (current_month_start.month - 1) or 12
    last_month_year = current_month_start.year - (1 if current_month_start.month == 1 else 0)
    last_month_start = last_month_end.replace(year=last_month_year, month=last_month, day=1)

    # Aggregate totals
    last_month_total = (
        NotificationActivity.objects.filter(
            created_at__gte=last_month_start,
            created_at__lt=last_month_end
        ).aggregate(total=Sum(Cast("amountSpent", FloatField())))["total"] or 0
    )

    this_month_total = (
        NotificationActivity.objects.filter(
            created_at__gte=current_month_start,
            created_at__lt=current_month_end
        ).aggregate(total=Sum(Cast("amountSpent", FloatField())))["total"] or 0
    )

    # Default values
    percentage_change = "0%"
    trend = "flat"

    if last_month_total == 0 and this_month_total > 0:
        percentage_change = "+100%"
        trend = "up"
    elif last_month_total == 0 and this_month_total == 0:
        percentage_change = "0%"
        trend = "flat"
    else:
        change = ((this_month_total - last_month_total) / last_month_total) * 100
        if change > 0:
            percentage_change = f"+{round(change, 2)}%"
            trend = "up"
        elif change < 0:
            percentage_change = f"{round(change, 2)}%"
            trend = "down"
        else:
            percentage_change = "0%"
            trend = "flat"

    # return {
    #     "last_month_total": last_month_total,
    #     "this_month_total": this_month_total,
    #     "percentage_change": percentage_change,
    #     "trend": trend,
    # }
    return {
        percentage_change, trend,
    }
    


def get_order_pending_stats():
    today = timezone.now()

    # Current month start
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Next month start (for current month end)
    next_month = (current_month_start.month % 12) + 1
    next_month_year = current_month_start.year + (1 if next_month == 1 else 0)
    current_month_end = current_month_start.replace(year=next_month_year, month=next_month)

    # Last month range
    last_month_end = current_month_start
    last_month = (current_month_start.month - 1) or 12
    last_month_year = current_month_start.year - (1 if current_month_start.month == 1 else 0)
    last_month_start = last_month_end.replace(year=last_month_year, month=last_month, day=1)

    # All-time total (not delivered)
    total_pending = OrderStatusTracking.objects.exclude(deliveryStatus="delivered").count()

    # Last month count (not delivered)
    last_month_count = OrderStatusTracking.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=last_month_end
    ).exclude(deliveryStatus="delivered").count()

    # This month count (not delivered)
    this_month_count = OrderStatusTracking.objects.filter(
        created_at__gte=current_month_start,
        created_at__lt=current_month_end
    ).exclude(deliveryStatus="delivered").count()

    # Default values
    percentage_change = "0%"
    trend = "flat"

    if last_month_count == 0 and this_month_count > 0:
        percentage_change = "+100%"
        trend = "up"
    elif last_month_count == 0 and this_month_count == 0:
        percentage_change = "0%"
        trend = "flat"
    else:
        change = ((this_month_count - last_month_count) / last_month_count) * 100
        if change > 0:
            percentage_change = f"+{round(change)}%"
            trend = "up"
        elif change < 0:
            percentage_change = f"{round(change)}%"
            trend = "down"
        else:
            percentage_change = "0%"
            trend = "flat"

    return total_pending, percentage_change, trend



def get_utility_stats():
    today = timezone.now()
    utility_activities = ["Airtime", "Electricity", "Cable", "Data"]

    # Current month start
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Next month start (for current month end)
    next_month = (current_month_start.month % 12) + 1
    next_month_year = current_month_start.year + (1 if next_month == 1 else 0)
    current_month_end = current_month_start.replace(year=next_month_year, month=next_month)

    # Last month range
    last_month_end = current_month_start
    last_month = (current_month_start.month - 1) or 12
    last_month_year = current_month_start.year - (1 if current_month_start.month == 1 else 0)
    last_month_start = last_month_end.replace(year=last_month_year, month=last_month, day=1)

    # All-time total
    total_utility_count = NotificationActivity.objects.filter(
        activityTtile__in=utility_activities
    ).count()

    # Last month
    last_month_count = NotificationActivity.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=last_month_end,
        activityTtile__in=utility_activities
    ).count()

    # This month
    this_month_count = NotificationActivity.objects.filter(
        created_at__gte=current_month_start,
        created_at__lt=current_month_end,
        activityTtile__in=utility_activities
    ).count()

    # Default values
    percentage_change = "0%"
    trend = "flat"

    if last_month_count == 0 and this_month_count > 0:
        percentage_change = "+100%"
        trend = "up"
    elif last_month_count == 0 and this_month_count == 0:
        percentage_change = "0%"
        trend = "flat"
    else:
        change = ((this_month_count - last_month_count) / last_month_count) * 100
        if change > 0:
            percentage_change = f"+{round(change)}%"
            trend = "up"
        elif change < 0:
            percentage_change = f"{round(change)}%"
            trend = "down"
        else:
            percentage_change = "0%"
            trend = "flat"

    return total_utility_count, percentage_change, trend



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# import your SuccessfullDeposites and PotentialDeposites models
from django.db.models import Sum
from django.db.models.functions import ExtractWeek, ExtractWeekDay, ExtractMonth
from datetime import date, timedelta
import calendar



# def build_global_deposit_analytics():
#     today = date.today()
#     current_year = today.year

#     # Query all successful deposits
#     deposits = SuccessfullDeposites.objects.all()

#     # --- DAILY (this week, grouped by weekday) ---
#     start_of_week = today - timedelta(days=today.weekday())  # Monday
#     week_deposits = (
#         deposits.filter(created_at__date__gte=start_of_week)
#         .annotate(weekday=ExtractWeekDay("created_at"))
#         .values("weekday")
#         .annotate(total=Sum("PotentialDeposites__amount"))
#     )
#     weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
#     daily = [
#         {
#             "name": weekdays[i - 1],
#             "amount": next(
#                 (float(item["total"]) for item in week_deposits if item["weekday"] == i),
#                 0,
#             ),
#         }
#         for i in range(1, 8)
#     ]

#     # --- WEEKLY (this month, grouped by week number) ---
#     start_of_month = today.replace(day=1)
#     weekly_deposits = (
#         deposits.filter(created_at__date__gte=start_of_month)
#         .annotate(week=ExtractWeek("created_at"))
#         .values("week")
#         .annotate(total=Sum("PotentialDeposites__amount"))
#         .order_by("week")
#     )
#     weekly = [
#         {"name": f"Week {idx}", "amount": float(entry["total"] or 0)}
#         for idx, entry in enumerate(weekly_deposits, start=1)
#     ]

#     # --- MONTHLY (this year, grouped by month) ---
#     monthly_deposits = (
#         deposits.filter(created_at__year=current_year)
#         .annotate(month=ExtractMonth("created_at"))
#         .values("month")
#         .annotate(total=Sum("PotentialDeposites__amount"))
#         .order_by("month")
#     )
#     monthly = [
#         {
#             "name": calendar.month_abbr[i],
#             "amount": next(
#                 (float(item["total"]) for item in monthly_deposits if item["month"] == i),
#                 0,
#             ),
#         }
#         for i in range(1, 13)
#     ]

#     return {"daily": daily, "weekly": weekly, "monthly": monthly}


def build_global_deposit_analytics():
    today = date.today()
    current_year = today.year

    # Query all successful deposits
    deposits = SuccessfullDeposites.objects.all()

    # --- DAILY (this week, grouped by weekday) ---
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    week_deposits = (
        deposits.filter(created_at__date__gte=start_of_week)
        .annotate(weekday=ExtractWeekDay("created_at"))  # 1=Sunday … 7=Saturday
        .values("weekday")
        .annotate(total=Sum("PotentialDeposites__amount"))
    )
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    daily = [
        {
            "name": weekdays[i - 1],
            "amount": next(
                (float(item["total"]) for item in week_deposits if item["weekday"] == i),
                0,
            ),
        }
        for i in range(1, 8)
    ]

    # --- WEEKLY (always 4 weeks for the month) ---
    start_of_month = today.replace(day=1)
    weekly_deposits = (
        deposits.filter(created_at__date__gte=start_of_month)
        .annotate(week=ExtractWeek("created_at"))
        .values("week")
        .annotate(total=Sum("PotentialDeposites__amount"))
        .order_by("week")
    )

    # Build Week 1–4, filling with 0 if missing
    weekly = []
    for i in range(1, 5):
        amount = next(
            (float(item["total"]) for idx, item in enumerate(weekly_deposits, start=1) if idx == i),
            0,
        )
        weekly.append({"name": f"Week {i}", "amount": amount})

    # --- MONTHLY (Jan–Dec for the year) ---
    monthly_deposits = (
        deposits.filter(created_at__year=current_year)
        .annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(total=Sum("PotentialDeposites__amount"))
        .order_by("month")
    )
    monthly = [
        {
            "name": calendar.month_abbr[i],
            "amount": next(
                (float(item["total"]) for item in monthly_deposits if item["month"] == i),
                0,
            ),
        }
        for i in range(1, 13)
    ]

    return {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
    }