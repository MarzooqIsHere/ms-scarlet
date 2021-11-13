import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('gacha-bot-firebase-adminsdk-sc887-22f62b65ee.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

