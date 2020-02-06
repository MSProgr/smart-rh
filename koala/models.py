from flask_login import UserMixin,current_user
from koala import db,login_manager,bcrypt

from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model,UserMixin):
	id = db.Column(db.Integer,unique=True,primary_key=True)
	matricule = db.Column(db.Integer,unique=True,nullable=False)
	nom = db.Column(db.String(50),nullable=False)
	prenom = db.Column(db.String(120),nullable=False)
	email = db.Column(db.String(120))
	code_structure = db.Column(db.String(50),nullable=False)
	groupe = db.Column(db.String(30),nullable=False)
	identifiant = db.Column(db.String(120),nullable=False,unique=True)
	password = db.Column(db.String(60),nullable=False,default=bcrypt.generate_password_hash('123456').decode('utf-8'))
	matricule_sup = db.Column(db.Integer)
	demandeMobileTemp = db.relationship('DemandeMobileTemp',backref='author',lazy=True)
	demandeMobilePerm = db.relationship('DemandeMobilePerm',backref='author',lazy=True)


class Parc(db.Model):
	id = db.Column(db.Integer,unique=True,nullable=False,primary_key=True)
	nom_parc = db.Column(db.String(120),unique=True,nullable=False)
	detail_parc = db.Column(db.Text,nullable=True)

class Offre(db.Model):
	id = db.Column(db.Integer,unique=True,nullable=False,primary_key=True)
	nom = db.Column(db.String(120),unique=True,nullable=False)
	description = db.Column(db.Text)

class DemandeMobileTemp(db.Model):
	id = db.Column(db.Integer,unique=True,nullable=False,primary_key=True)
	motif = db.Column(db.Text,nullable=False)
	nom_projet = db.Column(db.String(120),nullable=False)
	puces = db.Column(db.Integer,nullable=False)
	pilote = db.Column(db.String(120),nullable=False)
	caracteristiques = db.Column(db.Text,nullable=False)
	etat_demande = db.Column(db.String(30),default="En attente")
	date_demande = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	date_debut = db.Column(db.DateTime,nullable=False)
	date_fin = db.Column(db.DateTime,nullable=False)
	complement_demande = db.Column(db.String(20),nullable=True,default='')
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
	parc_id = db.Column(db.Integer,db.ForeignKey('parc.id'),nullable=False)
	offre_id = db.Column(db.Integer,db.ForeignKey('offre.id'),nullable=False)

class DemandeMobilePerm(db.Model):
	id = db.Column(db.Integer,unique=True,nullable=False,primary_key=True)
	motif = db.Column(db.Text,nullable=False)
	nom_projet = db.Column(db.String(120),nullable=False)
	puces = db.Column(db.Integer,nullable=False)
	pilote = db.Column(db.String(120),nullable=False)
	caracteristiques = db.Column(db.Text,nullable=False)
	etat_demande = db.Column(db.String(30),default="En attente")
	date_demande = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	date_debut = db.Column(db.DateTime,nullable=False)
	complement_demande = db.Column(db.String(20),nullable=True,default='')
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
	parc_id = db.Column(db.Integer,db.ForeignKey('parc.id'),nullable=False)
	offre_id = db.Column(db.Integer,db.ForeignKey('offre.id'),nullable=False)

class Agence(db.Model):
	id = db.Column(db.Integer,unique=True,nullable=False,primary_key=True)
	nom = db.Column(db.String(120),unique=True,nullable=False)
	email = db.Column(db.String(120))

