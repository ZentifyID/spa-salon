from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from apps.booking.models import Appointment
from apps.reviews.forms import ReviewForm
from apps.reviews.models import Review

from .models import Master


def master_list(request):
    masters = (
        Master.objects.filter(is_active=True)
        .prefetch_related("services")
        .annotate(
            approved_reviews_count=Count(
                "reviews",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
            average_rating=Avg(
                "reviews__rating",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
        )
    )
    return render(request, "masters/master_list.html", {"masters": masters})


def master_detail(request, pk):
    master = get_object_or_404(Master.objects.prefetch_related("services"), pk=pk, is_active=True)
    reviews = (
        master.reviews.filter(status=Review.Status.APPROVED)
        .select_related("user")
        .order_by("-created_at")
    )
    user_review = None
    review_form = None
    can_leave_review = False
    
    if request.user.is_authenticated:
        # User must have at least one completed appointment with this master to leave a review
        can_leave_review = Appointment.objects.filter(
            user=request.user,
            master=master,
            status=Appointment.Status.COMPLETED
        ).exists()
        
        if can_leave_review:
            user_review = Review.objects.filter(master=master, user=request.user).first()
            review_form = ReviewForm(instance=user_review)

    context = {
        "master": master,
        "reviews": reviews,
        "approved_reviews_count": reviews.count(),
        "average_rating": reviews.aggregate(avg=Avg("rating"))["avg"],
        "review_form": review_form,
        "user_review": user_review,
        "can_leave_review": can_leave_review,
    }
    return render(request, "masters/master_detail.html", context)
