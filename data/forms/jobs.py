from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    #id = IntegerField('Номер работы', validators=[DataRequired()])
    job = StringField('Работа', validators=[DataRequired()])
    work_size = IntegerField("Время работы", validators=[DataRequired()])
    team_leader = IntegerField('Ответственный за работу', validators=[DataRequired()])
    is_finished = BooleanField('Закончена работа?')
    collaborators = StringField('Работники', validators=[DataRequired()])
    submit = SubmitField('Применить')
