from flask import redirect,url_for,render_template,flash,request
from flask_login import login_user,logout_user,current_user,login_required

from koala import app,db,bcrypt,mail
from koala.forms import LoginForm,MobileTemporaireForm,MobilePermanentForm
from flask_mail import Message
from koala.models import User,Offre,Parc,DemandeMobileTemp,DemandeMobilePerm
from koala.config import load_offre,groupe_choices,load_parc,send_mail,is_chef_Sce,get_n_1,mail_to_n_1,serializer

import os
from datetime import datetime
from itsdangerous import SignatureExpired



@app.route('/validating_demande/<token>')
def validating_demande(token):
	try:
		info = serializer.loads(token,salt='validating-demande')
	except SignatureExpired:
		flash("Date d'expiration dépassé! Veuillez envoyez un mail à la DRH pour validation de la demande")
		return redirect(url_for('index'))
	num_demande = int(info[0])
	type_demande = info[1]
	user_email = info[2]

	if 'temp' in type_demande:
		demande = DemandeMobileTemp.query.get(num_demande)
	else:
		demande = DemandeMobilePerm.query.get(num_demande)
	demande.etat_demande = 'Valider'
	db.session.commit()
	msg = Message('Demande de ligne d\'exploitation',sender=('DRH SONATEL','diengdieng@gmail.com'),recipients=['ousseynou.dieng@univ-thies.sn'])
	msg.body="Votre demande de ligne d'exploitation du {}, à été valider".format(demande.date_demande)
	mail.send(msg)
	flash("Un email de notification de la validation de la demande a été envoyer à {} {}. Au revoir".format(demande.author.prenom,demande.author.nom),'success')
	return redirect(url_for('index'))



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
	parcs = db.session.query(Parc.nom_parc)
	offres = db.session.query(Offre.nom)
	parc_str,offre_str = "",""
	for p in parcs:
		parc_str+=p[0]+' - '
	for o in offres:
		offre_str+=o[0]+' - '
	return render_template('demande.html',dmt=dmt,dmp=dmp,parc_str=parc_str,offre_str=offre_str)



@app.route("/mobile_temporaire",methods=['GET','POST'])
def mobile_temporaire():
	form = MobileTemporaireForm()
	if form.validate_on_submit():
		motif = form.motif.data
		nom_projet = form.nom_projet.data
		puces = form.puces.data
		pilote = form.pilote.data
		caracteristiques = form.caracteristiques.data
		date_debut = datetime.strptime((form.date_debut.data).strftime('%m/%d/%Y'), '%m/%d/%Y')
		date_fin = datetime.strptime((form.date_fin.data).strftime('%m/%d/%Y'), '%m/%d/%Y')
		user_id = current_user.id
		parc_id = form.type_parc.data
		offre_id = form.offre.data
		demande = DemandeMobileTemp(motif=motif,nom_projet=nom_projet,puces=int(puces),pilote=pilote,
		caracteristiques=caracteristiques,date_debut=date_debut,date_fin=date_fin,
		user_id=int(user_id),parc_id=int(parc_id),offre_id=int(offre_id))
		db.session.add(demande)
		db.session.commit()
		the_message = send_mail('Temporaire',str(demande.id),str(puces),str(demande.date_demande))
		msg = Message('Accusé de Réception',sender=('DRH SONATEL','diengdieng@gmail.com'),recipients=['ousseynou.dieng@univ-thies.sn'])
		msg.html=the_message
		mail.send(msg)
		if is_chef_Sce():
			the_message = mail_to_n_1('Temporaire',str(demande.id),str(puces),str(demande.date_demande))
			msg = Message('Demande de ligne d\'exploitation',sender=('DRH SONATEL','diengdieng@gmail.com'),recipients=['diengdieng941@hotmail.com'])
			token = serializer.dumps([demande.id,'temp',current_user.email],salt='validating-demande')
			link = url_for('validating_demande',token=token,_external=True)
			msg.body=the_message+"\nVeuillez cliquez sur le lien ci-dessous pour valider la demande\n{}".format(link)
			mail.send(msg)
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
		motif = form.motif.data
		nom_projet = form.nom_projet.data
		puces = form.puces.data
		pilote = form.pilote.data
		caracteristiques = form.caracteristiques.data
		user_id = current_user.id
		parc_id = form.type_parc.data
		offre_id = form.offre.data
		demande = DemandeMobilePerm(motif=motif,nom_projet=nom_projet,puces=int(puces),pilote=pilote,
		caracteristiques=caracteristiques,
		user_id=int(user_id),parc_id=int(parc_id),offre_id=int(offre_id))
		db.session.add(demande)
		db.session.commit()
		the_message = send_mail('Permanent',str(demande.id),str(puces),str(demande.date_demande))
		msg = Message('Demande de ligne',sender=('DRH SONATEL','diengdieng@gmail.com'),recipients=['ousseynou.dieng@univ-thies.sn'])
		msg.html=the_message
		mail.send(msg)
		if is_chef_Sce():
			the_message = mail_to_n_1('Temporaire',str(demande.id),str(puces),str(demande.date_demande))
			msg = Message('Demande de ligne d\'exploitation',sender=('DRH SONATEL','diengdieng@gmail.com'),recipients=['diengdieng941@hotmail.com'])
			msg.html=the_message
			token = serializer.dumps([demande.id,'perm',current_user.email],salt='validating-demande')
			link = url_for('validating_demande',token=token,_external=True)
			msg.html=the_message+"\nVeuillez cliquez sur le lien ci-dessous pour valider la demande\n{}".format(link)
			mail.send(msg)
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





# @app.route('/demande_inf')
# @login_required
# def all_demande_inf():
# 	#Demande des colaborateurs
# 	all_users_colab = User.query.filter_by(matricule_sup=current_user.matricule)
# 	demandes_colab_mob_perm = []
# 	u_perm = []

# 	demandes_colab_mob_temp = []
# 	u_temp = []

# 	for u in all_users_colab:
# 		demande_ = DemandeMobilePerm.query.filter_by(author=u)
# 		if demande_.first():
# 			demandes_colab_mob_perm.append(demande_)
# 			u_perm.append(u)

# 	for u in all_users_colab:
# 		demande_ = DemandeMobileTemp.query.filter_by(author=u)
# 		if demande_.first():
# 			demandes_colab_mob_temp.append(demande_)
# 			u_temp.append(u)

# 	zip_perm = zip(demandes_colab_mob_perm,u_perm)
# 	zip_temp = zip(demandes_colab_mob_perm,u_temp)

# 	return render_template('demande_colab.html',zip_perm=zip_perm,zip_temp=zip_temp)