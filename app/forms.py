"""Manage the renedering of forms, with data validation."""

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, IntegerField,
                     TextAreaField)
from wtforms.validators import (DataRequired, Length, ValidationError,
                                NumberRange, Optional)
import re


class SignupForm(FlaskForm):
    """Define the form and validators for sign up."""

    def validate_username(self, field):
        """Check that username has no whitespace."""
        if re.search("\s", field.data):
            raise ValidationError('Invalid username.'
                                  + ' Must not have whitespace.')

    first_name = StringField('First Name', validators=[DataRequired(),
                                                       Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(),
                                                     Length(max=50)])
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(max=40)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=12)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 Length(min=12)])


class LoginForm(FlaskForm):
    """Define the form for logging in."""

    username = StringField('Username', validators=[DataRequired(),
                                                   Length(max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class EditProfileForm(FlaskForm):
    """Define form for editing user's profile."""

    def validate_password(self, field):
        """Check password length."""
        if field.data != "" and len(field.data) < 12:
            raise ValidationError('Password must be at least'
                                  + ' 12 characters long.')

    first_name = StringField('First Name', validators=[DataRequired(),
                                                       Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(),
                                                     Length(max=50)])
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(max=40)])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    bio = StringField('Bio', validators=[Length(max=50)])


class SearchForm(FlaskForm):
    """Define form for search bar."""

    search = StringField('Search', validators=[DataRequired(),
                                               Length(max=200)])


class PostForm(FlaskForm):
    """Define form editing a post."""

    rating = IntegerField('Rating',
                          validators=[Optional(True),
                                      NumberRange(min=0, max=100,
                                                  message='Rating must be'
                                                  + ' between 0 and 100')])
    review = TextAreaField('Review', validators=[Optional(True),
                                                 Length(max=500)])
