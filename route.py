#!/usr/bin/env python
# -*- coding=utf-8 -*-

from flask import Flask, request, session, render_template, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from py2neo import Relationship
from model import DB, User
import time

app = Flask(__name__)
Bootstrap(app)

if __name__ == "__main__":
    app.run(debug=True)


@app.route('/')
def accueil():
	try:
		user = User().findUserBySession(session['user'])
		if user:
			return render_template('accueil.html', user=user.get('username'))
	except:
		return render_template('accueil.html', user=None)


@app.route('/home/<username>', methods=['GET'])
def home(username):
	if User().findUserForLogin(username):
		graph = DB().db()
		queryDisplayPosts = "MATCH (user:User)-[relP:PUBLISHED]->(post:Post) WHERE user.username = {username} RETURN post ORDER BY post.date"
		posts = graph.run(queryDisplayPosts, username=username)
		try:
			if session['user'] == username:
				return render_template('home.html', type='owner', username=username, user=session['user'], posts=posts)
			else:
				return render_template('home.html', type='visitor', username=username, user=session['user'], posts=posts)
		except:
			return render_template('home.html', type='guest', username=username, user=None, posts=posts)

	return abort(404)


@app.route('/home/news/<username>', methods=['GET'])
def news(username):
	if session['user'] == username:
		graph = DB().db()
		queryDisplayUsers = "MATCH (user:User)-[relFollow:FOLLOW]->(u:User)-[relFollow2:FOLLOW]->(sugUser:User) WHERE NOT (user)-[relFollow]->(sugUser) AND user.username={username} AND NOT sugUser.username={username} RETURN sugUser"
		displayUsers = graph.run(queryDisplayUsers, username=username)

		if len(list(displayUsers)) < 2:
			queryDisplayUsers2 = "MATCH (sugUser:User) WHERE NOT sugUser.username={username} RETURN sugUser LIMIT 5"
			displayUsers = graph.run(queryDisplayUsers2, username=username)
		else:
			displayUsers = graph.run(queryDisplayUsers, username=username)

		queryDisplayPosts = "MATCH (user:User)-[relFollow:FOLLOW]->(u:User)-[relPublished:PUBLISHED]->(p:Post) WHERE user.username={username} RETURN u, p ORDER BY p.unique DESC"
		displayPosts = graph.run(queryDisplayPosts, username=username)
		return render_template('news.html', user=session['user'], displayUsers=displayUsers, displayPosts=displayPosts)

	return abort(404)


@app.route('/register/', methods=['POST', 'GET'])
def register():
	if request.method == 'POST':
		username = request.form['username'].replace(' ','').encode('utf-8')
		email = request.form['mail'].encode('utf-8')
		password = request.form['password'].encode('utf-8')
		confirmPassword = request.form['confirmPassword'].encode('utf-8')
		firstName = request.form['firstName'].encode('utf-8')
		lastName = request.form['lastName'].encode('utf-8')
		born = request.form['born'].encode('utf-8')

		if confirmPassword == password:
			if User().register(username, email, password, firstName, lastName, born) == True:
				return redirect(url_for('login'))
			else:
				return render_template('register.html', create='none')
		else:
			return render_template('register.html', samePassword='none')

	return render_template('register.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':

		username = request.form['username'].replace(' ','').encode('utf-8')
		password = request.form['password'].encode('utf-8')

		user = User().checkUser(username, password)
		if user:
			session['user'] = user.get('username')
			time.sleep(2)
			return redirect(url_for('home', username=session['user']))

		return render_template('login.html', connected='none')

	return render_template('login.html')


@app.route('/logout/')
def logout():
	session.pop('user', None)
	return redirect(url_for('login'))


@app.route('/addPost/', methods=['GET', 'POST'])
def addPost():
	try:
		user = User().findUserBySession(session['user'])
		if request.method == 'POST':
			title = request.form['title'].encode('utf-8')
			content = request.form['content'].encode('utf-8')
			addPost = User().addPost(user, title, content)
			return redirect(url_for('home', username=user.get('username')))

		return render_template('addPost.html', user=user.get('username'))

	except:
		return redirect(url_for('login'))


@app.route('/follow/<userAsk>/<userTo>', methods=['GET'])
def follow(userAsk, userTo):
	if session['user'] == userAsk:
		if User().followWithToUsername(userAsk, userTo):
			return redirect(url_for('news', username=userAsk))
		else:
			return 'error'
	return abort(404)


@app.route('/like/<username>/<unique>', methods=['GET'])
def likePost(username, unique):
	if session['user'] == username:
		graph = DB().db()
		query = "MATCH (u:User)-[l:LIKE]->(p:Post) WHERE u.username={username} AND p.unique={unique} RETURN l"
		run = graph.run(query, username=username, unique=unique)
		if len(list(run)) > 0:
			return 'error'
		else:
			user = graph.find_one('User', 'username', username)
			post = graph.find_one('Post', 'unique', unique)
			relation = Relationship(user, 'LIKE', post)
			graph.create(relation)
			return redirect(url_for('news', username=username))
	return abort(404)
