#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from config import app, db, api
from models import User

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

class Signup(Resource):
    def post(self):
        json = request.get_json()
        # Create the new user
        user = User(
            username=json['username']
        )
        # This calls the setter in models.py to hash the password
        user.password_hash = json['password']
        
        db.session.add(user)
        db.session.commit()
        
        # Log them in immediately after signup
        session['user_id'] = user.id
        
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        # Check if a user is logged in via the session cookie
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return user.to_dict(), 200
        
        # If not authenticated, return 204 No Content per instructions
        return {}, 204

class Login(Resource):
    def post(self):
        json = request.get_json()
        # Find user by username
        user = User.query.filter(User.username == json['username']).first()
        
        # Use the authenticate method from your User model
        if user and user.authenticate(json['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        # Return 401 if credentials are wrong
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        # Clear the user_id from the session
        session['user_id'] = None
        return {}, 204

# Registering the resources with the API
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)