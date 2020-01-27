from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,SubmitField,IntegerField,PasswordField,DateTimeField,SelectField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError

from koala.models import User,Offre

from koala.config import groupe_choices,load_offre,load_parc


class LoginForm(FlaskForm):
	identifiant = StringField('Identifiant',validators=[DataRequired()])
	password = PasswordField('Mot de Pass',validators=[DataRequired()])
	remember = BooleanField('Se Souvenir de Moi')
	submit = SubmitField('Se connecter')


class MobileTemporaireForm(FlaskForm):
	offre = SelectField("Offre à paramétrer",coerce=int,choices=load_offre(),validators=[DataRequired()])
	motif = TextAreaField('Motif de la demande',validators=[DataRequired()])
	nom_projet = StringField('Nom du projet',validators=[DataRequired()])
	puces = IntegerField("Nombre de puces",validators=[DataRequired()])
	pilote = StringField('Pilote',validators=[DataRequired()])
	type_parc = SelectField("Type de Parc",coerce=int,choices=load_parc(),validators=[DataRequired()])
	caracteristiques = TextAreaField("Caractéristiques",validators=[DataRequired()])
	date_debut = DateTimeField("Date de début d'utilisation",validators=[DataRequired()],format='%m/%d/%Y')
	date_fin = DateTimeField("Date de fin d'utilisation",validators=[DataRequired()],format='%m/%d/%Y')
	submit = SubmitField("Soumettre")

class MobilePermanentForm(FlaskForm):
	offre = SelectField("Offre à paramétrer",coerce=int,choices=load_offre(),validators=[DataRequired()])
	motif = TextAreaField('Motif de la demande',validators=[DataRequired()])
	nom_projet = StringField('Nom du projet',validators=[DataRequired()])
	puces = IntegerField("Nombre de puces",validators=[DataRequired()])
	pilote = StringField('Pilote',validators=[DataRequired()])
	type_parc = SelectField("Type de Parc",coerce=int,choices=load_parc(),validators=[DataRequired()])
	caracteristiques = TextAreaField("Caractéristiques",validators=[DataRequired()])
	submit = SubmitField("Soumettre")