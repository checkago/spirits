from django import forms
from datetime import datetime
from .models import Order
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'

    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    comment = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'rows': '4'})
    )

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'buying_type', 'order_date', 'comment'
        )


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()

        if not user:
            raise forms.ValidationError(f'Пользователь с логином {username} не найден')

        if not user.check_password(password):
            raise forms.ValidationError(f'Неверный пароль')
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=False, widget=forms.EmailInput)
    agreement = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['birth_date'].label = 'Дата рождения'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтверждение пароля'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['email'].label = 'E-mail'

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('.')[-1]
        if domain in ['com', 'net', 'org', 'xyz']:
            raise forms.ValidationError(f'Использование почтового ящика в домене .{domain} не разрешена')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Данный почтовый ящик уже зарегистрирован')
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        age = int((datetime.now().date() - birth_date).days / 365.25)
        if age < 18:
            raise forms.ValidationError(f"Указанный вами возраст меньше 18 лет. Регистрация не возможна")
        return birth_date

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Имя {username} занято')
        return username

    def clean_agreement(self):
        agreement = self.cleaned_data['agreement']
        if agreement == False:
            raise forms.ValidationError(f'Вы не подтвердили свое согласие с правилами обработки персональных данных')
        return agreement

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'birth_date', 'first_name', 'last_name', 'phone', 'email']


