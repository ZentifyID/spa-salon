from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from apps.masters.models import Master

from .forms import ReviewForm
from .models import Review


@login_required
def create_or_update_review(request, master_id):
    master = get_object_or_404(Master, pk=master_id, is_active=True)
    review = Review.objects.filter(master=master, user=request.user).first()

    if request.method != "POST":
        return redirect("masters:detail", pk=master.id)

    form = ReviewForm(request.POST, instance=review)
    if not form.is_valid():
        messages.error(request, "Проверьте поля формы отзыва.")
        return redirect("masters:detail", pk=master.id)

    review = form.save(commit=False)
    review.master = master
    review.user = request.user
    review.status = Review.Status.PENDING
    review.moderated_at = None
    review.save()

    messages.success(
        request,
        "Отзыв отправлен на модерацию. После проверки он появится на странице мастера.",
    )
    return redirect("masters:detail", pk=master.id)
