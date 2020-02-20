from flask import request,session,redirect,url_for,flash
from flask_login import current_user
from flask_mail import Message
from koala import db,babel,mail,app
from koala.models import Offre,User,Parc,DemandeMobileTemp,DemandeMobilePerm
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin import AdminIndexView
from flask_wtf.file import FileField
from flask_admin.helpers import validate_form_on_submit
from werkzeug.utils import secure_filename

from itsdangerous import URLSafeSerializer
import pandas as pd
import os
from datetime import datetime
import secrets
import io
import base64

groupe_choices = [('Chef Sce','Chef Sce'),('Chef Departement','Chef Departement'),('Directeur','Directeur')]


etat_demande_choices = [('En attente','En attente'),('En cour de Traitement','En cour de Traitement'),
						('Rejete','Rejeté'),('Valider','Valider')]


serializer = URLSafeSerializer('ec469fe94afede3381e93e36bb4e432c')

tmp = 'Temporaire'

perm = 'Permanent'


#retourne le message qu'on envoie à l'agent une fois qu'il à fait une demande
def send_mail(type_demande,numero,nbr_puces,date_demande):
	return ("<p>Votre demande à bien était prise en compte</p>"+\
			"<p><b>Description de la Demande:</b></p>"+\
			"<p><i>Type : Ligne d'exploitation mobile {}</i></p>"+\
			"<p><i>Numéro : {}</i></p>"+\
			"<p><i>Nombre de puces demandés : {}</i></p>"+\
			"<p><i>Date de la demande : {}</i></p>"+\
			"<p><i>Etat de la Demande : En attente de validation</i></p>"+\
			"<p><i>DRH Orange-Sonatel Sénégal</i></p>").format(type_demande,numero,nbr_puces,date_demande)


#retourne le message qu'on envoit au supérieur une fois que la demande est faite par l'utilisateur
def mail_to_n_1(type_demande,numero,nbr_puces,date_demande):
	return ("<p>Nouvelle demande de ligne d'exploitation</p>"+\
			"<p><b>Description de la Demande:</b></p>"+\
			"<p><i>Agent Demandeur : {}</i></p>"+\
			"<p><i>Type : Ligne d'exploitation mobile {}</i></p>"+\
			"<p><i>Numéro : {}</i></p>"+\
			"<p><i>Nombre de puces demandés : {}</i></p>"+\
			"<p><i>Date de la demande : {}</i></p>"+\
			"<p><i>Etat de la Demande : En attente de validation</i></p>"+\
			"<p><i>Veuillez vous connecter pour traiter la demande</i></p>"+\
			"<p><i>DRH Orange-Sonatel Sénégal</i></p>").format(current_user.prenom+'  '+current_user.nom,type_demande,numero,nbr_puces,date_demande)



#retourne le message une fois que le supérieur à traiter (valider,rejetter ou mettre en attente) la demande
def notification_to_user(type_demande,numero,nbr_puces,date_demande,decision):
	return ("<p>Suivi de la demande de ligne d'exploitation</p>"+\
			"<p><b>Description de la Demande:</b></p>"+\
			"<p><i>Type : Ligne d'exploitation mobile {}</i></p>"+\
			"<p><i>Numéro de la Demande : {}</i></p>"+\
			"<p><i>Nombre de puces demandés : {}</i></p>"+\
			"<p><i>Date de la demande : {}</i></p>"+\
			"<p><i>Etat de la Demande : {} par votre supérieur </i></p>"+\
			"<p><i>DRH Orange-Sonatel Sénégal</i></p>").format(type_demande,numero,nbr_puces,date_demande,decision)




#ënvoyer à l'agence une fois que le n+1 valide la demande
def notification_to_agence(type_demande,numero,nbr_puces,date_demande):
	return ("<p>Demande de ligne d'exploitation</p>"+\
			"<p><b>Description de la Demande:</b></p>"+\
			"<p><i>Type : Ligne d'exploitation mobile {}</i></p>"+\
			"<p><i>Numéro de la Demande : {}</i></p>"+\
			"<p><i>Nombre de puces demandés : {}</i></p>"+\
			"<p><i>Date de la demande : {}</i></p>"+\
			"<p><i>DRH Orange-Sonatel Sénégal</i></p>").format(type_demande,numero,nbr_puces,date_demande)



def is_chef_Sce():
	return 'Sce' in current_user.groupe

def is_chef_dep():
	return 'Departement' in current_user.groupe



def get_n_1():
	if is_chef_Sce():
		return User.query.get(current_user.matricule_sup).first()
	else:
		return None



def get_demande(type_demande,num_demande):
	if tmp in type_demande:
		demande = DemandeMobileTemp.query.get(num_demande)
	else:
		demande = DemandeMobilePerm.query.get(num_demande)

	return demande




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




#envoie un mail à l'utilisateur une fois sa demande traité par le n+1
def send_notification_email_after_n_1_decision(type_demande,numero,nbr_puces,date_demande,decision,email_dest):
	message = notification_to_user(type_demande,numero,nbr_puces,date_demande,decision)
	msg = Message('Suivi Demande',sender=('DRH SONATEL','diengdieng941@gmail.com'),recipients=[email_dest])
	msg.html=message
	mail.send(msg)


#envoie un mail à l'agence une fois que le n+1 est validé la demande
def send_notification_to_agence_after_n_1_validation(demande_id,type_demande,nbr_puces,date_demande,email_agence):
	message = notification_to_agence(type_demande,demande_id,nbr_puces,date_demande)
	msg = Message('Suivi Demande',sender=('DRH SONATEL','diengdieng941@gmail.com'),recipients=[email_agence])
	token = serializer.dumps([demande_id,type_demande],salt='validation_agence')
	link = url_for('validating_agence',token=token,_external=True)
	msg.html=message+"<p>Veuillez cliquez sur le lien ci-dessous pour choisir une action concerant la demande</p><a href={}>A propos de la demande</a>".format(link)
	mail.send(msg)


#envoie un message à l'utilisateur une fois que le l'agence est valider la demande
def for_user_after_validation_by_agence(demande_id,demande_type,decision,user_email):
	message = "<p>La demande numero {} de ligne d'exploitation mobile {} à était {}</p>".format(str(demande_id),demande_type,decision)
	msg = Message('Suivi Demande',sender=('DRH SONATEL','diengdieng941@gmail.com'),recipients=[user_email])
	#token = serializer.dumps([demande_id,demande_type],salt='decision_agence')
	link = url_for('info_demande',demande_id=demande_id,demande_type=demande_type,_external=True)
	msg.html=message+"<p>Veuillez cliquez sur le lien ci-dessous pour plus de détails concernant la demande</p><a href={}>A propos de la demande</a>".format(link)
	mail.send(msg)



#envoie un mail ) l'utilisateur une fois qu'il à fait une demande
def send_email_to_user(demande_type,demande_id,puces,date_demande):
	the_message = send_mail(demande_type,str(demande_id),str(puces),str(date_demande))
	msg = Message('Suivi Demande',sender=('DRH SONATEL','diengdieng941@gmail.com'),recipients=[current_user.email])
	msg.html=the_message
	mail.send(msg)



#envoie un mail au supérieur de l'utilisateur avec un lien pour qu'il valide ou non la demande
def send_mail_to_n_1(demande_type,demande_id,puces,date_demande):
	the_message = mail_to_n_1(demande_type,str(demande_id),str(puces),str(date_demande))
	mail_sup = User.query.filter_by(matricule=current_user.matricule_sup).first()
	msg = Message('Demande de ligne d\'exploitation',sender=('DRH SONATEL','diengdieng941@gmail.com'),recipients=[mail_sup.email])
	token = serializer.dumps([demande_id,demande_type,current_user.email],salt='demande_validation')
	link = url_for('validating_demande',token=token,_external=True)
	msg.html=the_message+"<p>Veuillez cliquez sur le lien ci-dessous pour choisir une action concerant la demande</p><a href={}>A propos de la demande</a>".format(link)
	mail.send(msg)


#recupére les données du formulaire de demande, les ajoute dans la base de données et envoie un mail à l'agent qui a fait la demande
def get_add_and_send_email_from_form(form_type,form):
	motif = form.motif.data
	nom_projet = form.nom_projet.data
	puces = form.puces.data
	pilote = form.pilote.data
	caracteristiques = form.caracteristiques.data
	user_id = current_user.id
	parc_id = form.type_parc.data
	offre_id = form.offre.data
	date_debut = datetime.strptime((form.date_debut.data).strftime('%m/%d/%Y'), '%m/%d/%Y')
	if tmp in form_type:
		date_fin = datetime.strptime((form.date_fin.data).strftime('%m/%d/%Y'), '%m/%d/%Y')
		demande = DemandeMobileTemp(motif=motif,nom_projet=nom_projet,puces=int(puces),pilote=pilote,
		caracteristiques=caracteristiques,date_debut=date_debut,date_fin=date_fin,
		user_id=int(user_id),parc_id=int(parc_id),offre_id=int(offre_id))
	else:
		demande = DemandeMobilePerm(motif=motif,nom_projet=nom_projet,puces=int(puces),pilote=pilote,
		caracteristiques=caracteristiques,date_debut=date_debut,user_id=int(user_id),parc_id=int(parc_id),offre_id=int(offre_id))
	db.session.add(demande)
	db.session.commit()
	send_email_to_user(form_type,demande.id,puces,demande.date_demande)

	return demande


def append_in_centrale(model,df,type_dem):
	centrale = pd.read_excel(os.path.join(app.root_path,"static/fichiers/demande_mobile_centrale.xlsx"))
	df['type de parc'] = Parc.query.get(model.parc_id).nom_parc
	df['nom et prenom pilote ou utilisateur'] = model.pilote
	df['Code Structure'] = model.author.code_structure
	df['Nom du Projet'] = model.nom_projet
	df['date de début projet'] = str(model.date_debut)
	if 'temp' in type_dem:
		df['date de fin projet'] = str(model.date_fin)
	else:
		df['date de fin projet'] = ""
	new_centrale = pd.concat([centrale,df],ignore_index=True)
	new_centrale.to_excel(os.path.join(app.root_path,"static/fichiers/demande_mobile_centrale.xlsx"),index=False)
				


class MyAdminIndexView(AdminIndexView):
	def is_accessible(self):
		return (current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
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
		#return current_user.is_authenticated
		return (current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
		return redirect(url_for('index'))




class ParcView(ModelView):
	form_base_class = SecureForm
	page_size = 20
	create_modal = True
	edit_modal = True
	can_export = True
	export_types = ['csv']

	def is_accessible(self):
		return (current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
		return redirect(url_for('index'))



class OffreView(ModelView):
	form_base_class = SecureForm
	page_size = 20
	create_modal = True
	edit_modal = True
	can_export = True
	export_types = ['csv']
	def is_accessible(self):
		return (current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
		return redirect(url_for('index'))




class DemandeMobileTempView(ModelView):
	page_size = 20
	can_delete = True
	can_create = False
	can_export = True
	details_modal=True
	edit_modal = True
	can_view_details = True
	create_modal = True
	export_types = ['csv']
	column_exclude_list = ['motif','caracteristiques','pilote']
	column_searchable_list = []
	column_filters = ['date_demande','date_debut','date_fin','etat_demande']
	#column_editable_list = ['etat_demande','date_fin','puces','date_debut']
	column_editable_list = []
	column_formatters = dict(author=lambda v, c, m, p: m.author.prenom+'  '+m.author.nom+ ' : '+str(m.author.matricule))
	form_base_class = SecureForm
	form_overrides = dict(complement_demande=FileField)
	form_choices = {
		'etat_demande':etat_demande_choices
	}

	def on_model_change(self,form, model, is_created):
		if not is_created:
			try:
				file = request.files.get('complement_demande')
				df = pd.read_excel(file,error_bad_lines=True)
			except:
				return

			if df.shape[0] == int(model.puces):
				_, f_ext = os.path.splitext(form.complement_demande.data.filename)
				fichier_fn = model.author.nom+"_"+model.author.prenom+"_"+str(model.date_demande)+f_ext
				fichier_path = os.path.join(app.root_path,"static/fichiers",fichier_fn)
				df.to_excel(fichier_path,index=False)
				model.complement_demande = fichier_fn
				#On concaténe les données avec le fichier de nessico
				append_in_centrale(model,df,"temp")
				db.session.commit()
				return
			else:
				flash('Le nombre de numéro dans le fichier est different du nombre de puces de la demande','danger')
				model.complement_demande = ""
				return

		
	def is_accessible(self):
		return (current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
		return redirect(url_for('index'))

#num_ligne, periode, traffic_voix_sortant, traffic_data,ca_recharge,date_dernier_appel

class DemandeMobilePermView(ModelView):
	page_size = 20
	can_delete = True
	can_create = False
	can_export = True
	edit_modal = True
	can_view_details = True
	create_modal = True
	details_modal=True
	export_types = ['csv']
	column_exclude_list = ['motif','caracteristiques','pilote']
	column_searchable_list = []
	column_filters = ['date_demande','etat_demande']
	#column_editable_list = ['etat_demande','puces','date_debut']
	column_editable_list = []
	column_formatters = dict(author=lambda v, c, m, p: m.author.prenom+'  '+m.author.nom+ ' : '+str(m.author.matricule))
	form_base_class = SecureForm
	form_overrides = dict(complement_demande=FileField)
	form_choices = {
		'etat_demande':etat_demande_choices
	}
			
	def is_accessible(self):
		return(current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
		return redirect(url_for('index'))

	def on_model_change(self,form, model, is_created):
		if not is_created:
			try:
				file = request.files.get('complement_demande')
				df = pd.read_excel(file,error_bad_lines=True)
			except:
				return

			if df.shape[0] == int(model.puces):
				_, f_ext = os.path.splitext(form.complement_demande.data.filename)
				fichier_fn = model.author.nom+"_"+model.author.prenom+"_"+str(model.date_demande)+f_ext
				fichier_path = os.path.join(app.root_path,"static/fichiers",fichier_fn)
				df.to_excel(fichier_path,index=False)
				model.complement_demande = fichier_fn
				#Ici on concaténe le fichier centrale et le fichier qui vient de nessico
				append_in_centrale(model,df,'perm')
				db.session.commit()
				return
			else:
				flash('Le nombre de numéro dans le fichier est different du nombre de puces de la demande','danger')
				model.complement_demande = ""
				return



class AgenceView(ModelView):
	form_base_class = SecureForm
	page_size = 20
	create_modal = True
	edit_modal = True
	can_export = True
	export_types = ['csv']
	def is_accessible(self):
		return (current_user.is_authenticated and ("admin" in current_user.profile))

	def inaccessible_callback(self,name,**kwargs):
		flash("Vous n'étes pas autorisez à accéder à cette page","danger")
		return redirect(url_for('index'))