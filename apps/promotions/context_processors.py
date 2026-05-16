from .models import SpecialOffer


def active_offer(request):
    """
    Returns the latest active special offer for the global layout.
    """
    offer = SpecialOffer.objects.filter(is_active=True).order_by("-created_at").first()
    return {"special_offer": offer}
