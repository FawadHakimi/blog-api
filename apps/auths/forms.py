from unfold.forms import UserChangeForm, UserCreationForm

from apps.auths.models import User

NEW_USER_FIELDS = ("email", "first_name", "last_name")

class UserAdminChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        field_classes: dict = {}

class UserAdminCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = NEW_USER_FIELDS
        field_classes: dict = {}

    def clean_email(self) -> str:
        return self.cleaned_data["email"].lower()
