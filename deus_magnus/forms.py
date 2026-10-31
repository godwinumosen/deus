
from django import forms
from django.utils.text import slugify
from .models import BlogDeusMagnus



class BlogDeusMagnusForm(forms.ModelForm):

    class Meta:
        model = BlogDeusMagnus
        fields = [
            'blog_deus_magnus_title',
            'blog_deus_magnus_subtitle',
            'blog_deus_magnus_slug',
            'blog_deus_magnus_img',
            'blog_deus_magnus_status',
            'blog_deus_magnus_description',
        ]
        widgets = {
            "blog_deus_magnus_title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter article title",
            }),
            "blog_deus_magnus_subtitle": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter article subtitle",
            }),
            "blog_deus_magnus_slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "article-url-slug",
            }),
            "blog_deus_magnus_img": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "blog_deus_magnus_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 12,
                "id": "id_blog_content",
            }), 
            "blog_deus_magnus_status": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # New articles start as drafts.
        if not self.instance.pk:
            self.fields["blog_deus_magnus_status"].initial = "draft"

        # The image is required for a new article, but not for an edit.
        if self.instance.pk:
            self.fields["blog_deus_magnus_img"].required = False

    def clean_blog_deus_magnus_slug(self):
        slug = self.cleaned_data.get("blog_deus_magnus_slug")
        title = self.cleaned_data.get("blog_deus_magnus_title")
        return slugify(slug or title or "")
