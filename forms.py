from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
                       DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    apartment = StringField('Apartment Number', validators=[
                            DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')


class NoticeForm(FlaskForm):
    title = StringField('Notice Title', validators=[
                        DataRequired(), Length(min=5, max=200)])
    content = TextAreaField('Notice Content', validators=[
                            DataRequired(), Length(min=10)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    submit = SubmitField('Post Notice')


class ServiceRequestForm(FlaskForm):
    title = StringField('Request Title', validators=[
                        DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[
                                DataRequired(), Length(min=10)])
    category = SelectField('Category', choices=[
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('carpentry', 'Carpentry'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit Request')


class ChatMessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
                            DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send')


class UpdateRequestStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')


class UserProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[
                       DataRequired(), Length(min=2, max=50)])
    apartment = StringField('Apartment Number', validators=[
                            DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
                                 DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
                                     DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[Length(max=100)])
    submit = SubmitField('Search')


class FilterForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('carpentry', 'Carpentry'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('other', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('', 'All Status'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled')
    ])
    priority = SelectField('Priority', choices=[
        ('', 'All Priorities'),
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ])
    submit = SubmitField('Apply Filters')

# Custom validators


def validate_apartment_format(form, field):
    """Validate apartment number format"""
    apartment = field.data
    # Basic validation - can be customized based on your apartment numbering system
    if not any(char.isdigit() for char in apartment):
        raise ValidationError(
            'Apartment number must contain at least one digit.')

    if len(apartment) < 2:
        raise ValidationError('Apartment number is too short.')


def validate_password_strength(form, field):
    """Validate password strength"""
    password = field.data
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long.')

    # Check for at least one letter and one number
    has_letter = any(char.isalpha() for char in password)
    has_number = any(char.isdigit() for char in password)

    if not (has_letter and has_number):
        raise ValidationError(
            'Password must contain both letters and numbers.')


# Add custom validators to forms
RegistrationForm.apartment.validators.append(validate_apartment_format)
RegistrationForm.password.validators.append(validate_password_strength)
ChangePasswordForm.new_password.validators.append(validate_password_strength)
