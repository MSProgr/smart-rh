from flask import redirect,url_for,render_template,flash,request
from flask_login import login_user,logout_user,current_user,login_required

from koala import app,db,bcrypt,mail

from koala.forms import LoginForm,MobileTemporaireForm,MobilePermanentForm

from flask_mail import Message

from koala.models import User,Offre,Parc,DemandeMobileTemp,DemandeMobilePerm,Agence

from koala.config import load_offre,groupe_choices,load_parc,send_email_to_user,is_chef_Sce,get_n_1,\
send_mail_to_n_1,serializer,is_chef_dep

from koala.config import get_add_and_send_email_from_form,send_notification_email_after_n_1_decision,tmp,perm,get_demande

from koala.config import send_notification_to_agence_after_n_1_validation,for_user_after_validation_by_agence


import os
from datetime import datetime


#cette méthode est appelé quand le n+1 click sur le line qui lui est envoyer pour prendre une décision sur la demande
@app.route('/validating_demande/<token>')
def validating_demande(token):
	#the token contain the [demande_id,type_demande,'current_user.email']
	try:
		info = serializer.loads(token,salt='demande_validation')
	except:
		flash("Il se peut que le lien cliquez ne soit plus disponible. Veuillez contacter l'administrateur pour plus d'info","warning")
		return redirect(url_for('index'))

	num_demande = int(info[0])
	type_demande = info[1]

	demande = get_demande(type_demande,num_demande)

	return render_template('decision.html',demande=demande,type_demande=type_demande)


#Cettes méthode est appelé une fois que le n+1 à cliquez sur une decision
#on envoie un mail à l'agent demandeur et à l'agence
@app.route('/decision_sup/<demande_id>/<user_matricule>/<type_demande>/<decision>')
def decision_sup(demande_id,user_matricule,type_demande,decision):
	demande_id = int(demande_id)
	user_matricule = int(user_matricule)
	type_demande = type_demande
	decision = decision
	try:
		demande = get_demande(type_demande,demande_id)
	except:
		return render_template('error.html')

	if 'valide' in decision:
		send_notification_email_after_n_1_decision(type_demande,demande_id,demande.puces,demande.date_demande,"VALIDER",demande.author.email)
		email_agence = Agence.query.first().email
		send_notification_to_agence_after_n_1_validation(demande_id,type_demande,demande.puces,demande.date_demande,email_agence)
	elif 'rejetter' in decision:
		send_notification_email_after_n_1_decision(type_demande,demande_id,demande.puces,demande.date_demande,"REJETTER",demande.author.email)
	else:
		send_notification_email_after_n_1_decision(type_demande,demande_id,demande.puces,demande.date_demande,"MISE EN ATTENTE",demande.author.email)

	return redirect(url_for('index'))


#cette méthode redigire l'agence aprés click sur le line pour qu'il prennne sa decision sur la demande
@app.route('/validating_agence/<token>')
def validating_agence(token):
	#[demande_id,type_demande],
	try:
		info = serializer.loads(token,salt='validation_agence')
	except:
		flash("La Demande n'est pas disponible. Veuillez contacter l'administrateur pour plus d'information","warning")
		return redirect(url_for('index'))

	demande_id = int(info[0])
	type_demande = info[1]

	demande = get_demande(type_demande,demande_id)

	return render_template('decision_agence.html',demande=demande,type_demande=type_demande)



#cette méthode est appelé une fois que l'agence à prit sa decision
#on envoie un mail à l'agent demandeur et à son supérieur
@app.route('/decision_age/<demande_id>/<user_matricule>/<type_demande>/<decision>')
def decision_age(demande_id,user_matricule,type_demande,decision):
	demande_id = int(demande_id)
	user_matricule = int(user_matricule)
	demande_type = type_demande
	decision = decision
	try:
		demande = get_demande(demande_type,demande_id)
	except:
		return render_template('error.html')

	chief = User.query.filter_by(matricule=demande.author.matricule_sup).first()

	if 'valide' in decision:
		demande.etat_demande='Valider'
		db.session.commit()
		for_user_after_validation_by_agence(demande_id,demande_type,'VALIDER',demande.author.email)
		for_user_after_validation_by_agence(demande_id,demande_type,'VALIDER',chief.email)
	elif 'rejetter' in decision:
		demande.etat_demande='Rejete'
		db.session.commit()
		for_user_after_validation_by_agence(demande_id,demande_type,'REJETTER',demande.author.email)
		for_user_after_validation_by_agence(demande_id,demande_type,'REJETTER',chief.email)
	else:
		for_user_after_validation_by_agence(demande_id,demande_type,'MISE EN ATTENTE',demande.author.email)
		for_user_after_validation_by_agence(demande_id,demande_type,'MISE EN ATTENTE',chief.email)

	flash("Un email de notification a été envoyer à l'agent demandeur! Merci","warning")
	return redirect(url_for('index'))

#cette méthode est appelé pour  consulter la demande aprés la decision de l'agence: on y accéde en cliquant sur le lien envoyé par mail
@app.route('/after_decision_agence/<demande_id>/<demande_type>')
def info_demande(demande_id,demande_type):
	try:
		demande = get_demande(demande_type,int(demande_id))
	except:
		flash("Nous rencontrons des difficultés pour trouver la demande! Veuillez consulter l'admin pour plus d'infos","warning")
		return redirect(url_for('index'))

	return render_template('view_agence_decision.html',demande=demande,type_demande=demande_type)



@app.route("/index",methods=['GET','POST'])
@app.route("/",methods=['GET','POST'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('demande'))

	form = LoginForm()
	parcs = Parc.query.all()
	offres = Offre.query.all()
	if form.validate_on_submit():
		user = User.query.filter_by(identifiant=form.identifiant.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user,remember=form.remember.data)
			return redirect(url_for('demande'))
		else:
			flash('Identifiant ou mot de pass incorrect',"warning")
			return redirect(url_for('index'))

	return render_template('hello.html',form=form,parcs=parcs,offres=offres)



@app.route("/demande",methods=['GET','POST'])
@login_required
def demande():
	dmt = DemandeMobileTemp.query.filter_by(author=current_user)
	dmp = DemandeMobilePerm.query.filter_by(author=current_user)
	return render_template('demande.html',dmt=dmt,dmp=dmp)



@app.route("/mobile_temporaire",methods=['GET','POST'])
def mobile_temporaire():
	form = MobileTemporaireForm()
	if form.validate_on_submit():
		demande = get_add_and_send_email_from_form(tmp,form)
		
		if is_chef_Sce() or is_chef_dep():
			send_mail_to_n_1(tmp,demande.id,demande.puces,demande.date_demande)

		flash('Nous avons pris en compte votre demande. Vous serez notifié une fois qu\'elle sera traitée !','primary' )
		return redirect(url_for('demande'))
	elif request.method == 'GET':
		form.offre.choices = load_offre()
		form.type_parc.choices = load_parc()

	return render_template('mobile_temporaire.html',form=form)



@app.route("/mobile_permanent",methods=['GET','POST'])
def mobile_permanent():
	form = MobilePermanentForm()
	if form.validate_on_submit():
		demande=get_add_and_send_email_from_form(perm,form)

		if is_chef_Sce() or is_chef_dep():
			send_mail_to_n_1(perm,demande.id,demande.puces,demande.date_demande)

		flash('Nous avons pris en compte votre demande. Vous serez notifié une fois qu\'elle sera traitée !','primary' )
		return redirect(url_for('demande'))
	elif request.method == 'GET':
		form.offre.choices = load_offre()
		form.type_parc.choices = load_parc()

	return render_template('mobile_permanent.html',form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/test/<test_f>')
def test(test_f):
	return render_template('test.html',test_f=test_f)