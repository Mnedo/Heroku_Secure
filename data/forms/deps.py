from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class DepsForm(FlaskForm):
    id = IntegerField('Номер')
    title = StringField('Департамент', validators=[DataRequired()])
    members = StringField('Сотрудники', validators=[DataRequired()])
    chief = StringField('Ответственный', validators=[DataRequired()])
    email = StringField('Почта для обращения', validators=[DataRequired()])
    submit = SubmitField('Применить')
