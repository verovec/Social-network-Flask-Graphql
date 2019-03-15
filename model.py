#!/usr/bin/env python
# -*- coding=utf-8 -*-

import os
from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime


class DB():
	def db(self):
		try:
			graph = Graph('http://USERNAME:PASSWORD@IP ADDRESS:PORT')
			return graph

		except Exception as e:
			return str(e)


class User():
	def __init__(self):
		self.graph = DB().db()


	def findUserForLogin(self, username):
		matchName = self.graph.find_one('User', 'username', username)
		matchEmail = self.graph.find_one('User', 'email', username)
		if matchName:
			return matchName
		elif matchEmail:
			return matchEmail
		else:
			return False


	def findUserBySession(self, session):
		user = self.graph.find_one('User', 'username', session)
		return user


	def register(self, username, email, password, firstName, lastName, born):
		if not self.findUserForLogin(username) and not self.findUserForLogin(email):
			user = Node('User', username=username, email=email, password=bcrypt.encrypt(password), firstName=firstName, lastName=lastName, born=born, date=str(datetime.today().date()))
			self.graph.create(user)
			return True
		else:
			return False


	def checkUser(self, username, password):
		user = self.findUserForLogin(username)
		if user:
			if bcrypt.verify(password, user['password']):
				return user
		else:
			return False


	def addPost(self, user, title, content):
		try:
			post = Node('Post', title=title, content=content, date=str(datetime.today().date()), unique=str(datetime.now()))
			self.graph.create(post)
			relation = Relationship(user, 'PUBLISHED', post)
			self.graph.create(relation)
			return True

		except:
			return False


	def followWithToUsername(self, userAsk, userTo):
		try:
			query = "MATCH (u:User)-[f:FOLLOW]->(user:User) WHERE u.username={userAsk} AND user.username={userTo} return f"
			run = self.graph.run(query, userAsk=userAsk, userTo=userTo)

			if len(list(run)) > 0:
				return False
			else:
				userAsk = self.graph.find_one('User', 'username', userAsk)
				userTo = self.graph.find_one('User', 'username', userTo)
				relation = Relationship(userAsk, 'FOLLOW', userTo)
				self.graph.create(relation)
				return True

		except:
			return False
