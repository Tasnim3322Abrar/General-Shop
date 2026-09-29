from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review

        fields = (
            "rating",
            "title",
            "comment",
        )

        widgets = {
            "rating": forms.Select(
                choices=[
                    (5, "★★★★★ - Excellent"),
                    (4, "★★★★☆ - Very Good"),
                    (3, "★★★☆☆ - Good"),
                    (2, "★★☆☆☆ - Fair"),
                    (1, "★☆☆☆☆ - Poor"),
                ]
            ),

            "title": forms.TextInput(
                attrs={
                    "placeholder": "Review title",
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "placeholder": "Write your review...",
                    "rows": 5,
                }
            ),
        }