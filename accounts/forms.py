from django import forms

class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")

        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False, label="Phone Number", 
                          widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password (leave blank to keep current)")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password or password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Passwords do not match")
        return cleaned_data 