from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        labels = {
            "rating": "Оценка",
            "text": "Ваш отзыв",
        }
        widgets = {
            "rating": forms.Select(
                choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")]
            ),
            "text": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"field-control {css_class}".strip()

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Оценка должна быть от 1 до 5.")
        return rating
