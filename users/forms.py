from django import forms
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    """
    Standalone form for creating users. 
    Inherits from ModelForm to avoid conflict with default UserCreationForm.
    """
    password_1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Required. Minimum 8 characters."
    )
    password_2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role", "created_by_user", "is_active", "is_staff")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password_1")
        p2 = cleaned_data.get("password_2")
        
        if p1 and p2 and p1 != p2:
            self.add_error('password_2', "Passwords do not match.")
        
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("User with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password_1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"