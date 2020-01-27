from flask import request,session,redirect,url_for
from flask_login import current_user
from koala import db,babel
from koala.models import Offre,User,Parc
import csv
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin import AdminIndexView
from itsdangerous import URLSafeSerializer


groupe_choices = [('Chef Sce','Chef Sce'),('Chef Departement','Chef Departement'),('Directeur','Directeur')]

etat_demande_choices = [('En attente','En attente'),('En cour de Traitement','En cour de Traitement'),
						('Rejete','Rejeté'),('Valider','Valider')]

serializer = URLSafeSerializer('ec469fe94afede3381e93e36bb4e432c')


def send_mail(type_demande,numero,nbr_puces,date_demande):
	return ("Votre demande à bien était prise en compte\n"+\
			"Description de la Demande\n"+\
			"Type : Ligne d'exploitation mobile {}\n"+\
			"Numéro : {}\n"+\
			"Nombre de puces demandés : {}\n"+\
			"Date de la demande : {}\n"+\
			"Etat de la Demande : En attente de validation\n"+\
			"DRH Orange-Sonatel Sénégal").format(type_demande,numero,nbr_puces,date_demande)

def mail_to_n_1(type_demande,numero,nbr_puces,date_demande):
	return ("Nouvelle demande de ligne d'exploitation\n"+\
			"Description\n"+\
			"Agent Demandeur : {}\n"+\
			"Type : Ligne d'exploitation mobile {}\n"+\
			"Numéro : {}\n"+\
			"Nombre de puces demandés : {}\n"+\
			"Date de la demande : {}\n"+\
			"Etat de la Demande : En attente de validation\n"+\
			"Veuillez vous connecter pour valider ou rejetter la demande\n"+\
			"DRH Orange-Sonatel Sénégal").format(current_user.prenom+'  '+current_user.nom,type_demande,numero,nbr_puces,date_demande)


def is_chef_Sce():
	return 'Sce' in current_user.groupe

def get_n_1():
	if is_chef_Sce():
		return User.query.get(current_user.matricule_sup).first()
	else:
		return None


def load_offre():
	list_offre=[]
	for offre in Offre.query.all():
		list_offre.append((offre.id,offre.nom))
	return list_offre

def load_parc():
	list_parc=[]
	for parc in Parc.query.all():
		list_parc.append((parc.id,parc.nom_parc))
	return list_parc

@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'fr')


class MyAdminIndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self,name,**kwargs):
		return redirect(url_for('index'))

class UserView(ModelView):
	form_base_class = SecureForm
	page_size = 20
	can_export = True
	can_create = True
	export_types = ['csv']
	column_exclude_list = ['password']
	column_searchable_list = ['nom','prenom']
	column_filters = ['groupe','code_structure']
	column_editable_list = ['matricule','matricule_sup']
	column_labels = dict(matricule_sup='Matricule N+1')
	create_modal = True
	edit_modal = True
	form_excluded_columns = ['demandeMobileTemp','demandeMobilePerm','password']
	form_choices = {
		'groupe':groupe_choices
	}

	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self,name,**kwargs):
		return redirect(url_for('index'))


class ParcView(ModelView):
	form_base_class = SecureForm
	page_size = 20
	create_modal = True
	edit_modal = True
	can_export = True
	export_types = ['csv']
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self,name,**kwargs):
		return redirect(url_for('index'))


class OffreView(ModelView):
	form_base_class = SecureForm
	page_size = 20
	create_modal = True
	edit_modal = True
	can_export = True
	export_types = ['csv']
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self,name,**kwargs):
		return redirect(url_for('index'))


class DemandeMobileTempView(ModelView):
	page_size = 20
	can_delete = True
	can_create = False
	can_edit = False
	can_export = True
	details_modal=True
	edit_modal = True
	can_view_details = True
	create_modal = True
	export_types = ['csv']
	column_exclude_list = ['motif','caracteristiques','pilote']
	column_searchable_list = []
	column_filters = ['date_demande','date_debut','date_fin','etat_demande']
	column_editable_list = ['etat_demande']
	column_formatters = dict(author=lambda v, c, m, p: m.author.prenom+'  '+m.author.nom+ ' : '+str(m.author.matricule))
	form_base_class = SecureForm
	form_choices = {
		'etat_demande':etat_demande_choices
	}
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self,name,**kwargs):
		return redirect(url_for('index'))


class DemandeMobilePermView(ModelView):
	page_size = 20
	can_delete = True
	can_create = False
	can_edit = False
	can_export = True
	edit_modal = True
	can_view_details = True
	create_modal = True
	details_modal=True
	export_types = ['csv']
	column_exclude_list = ['motif','caracteristiques','pilote']
	column_searchable_list = []
	column_filters = ['date_demande','etat_demande']
	column_editable_list = ['etat_demande']
	column_formatters = dict(author=lambda v, c, m, p: m.author.prenom+'  '+m.author.nom+ ' : '+str(m.author.matricule))
	form_base_class = SecureForm
	form_choices = {
		'etat_demande':etat_demande_choices
	}
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self,name,**kwargs):
		return redirect(url_for('index'))