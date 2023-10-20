from datetime import datetime

from app import app
from models import db, Message

class TestApp:
    '''Flask application in app.py'''

    @classmethod
    def setup_class(cls):
        # Delete any existing messages with body "Hello 👋" from Liza
        with app.app_context():
            messages_to_delete = Message.query.filter(
                Message.body == "Hello 👋",
                Message.username == "Liza"
            ).all()
            for message in messages_to_delete:
                db.session.delete(message)
            db.session.commit()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()

            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            app.test_client().post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza"
                }
            )

            new_message = Message.query.filter_by(body="Hello 👋").first()
            assert new_message is not None

            # Clean up: Delete the new message
            db.session.delete(new_message)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self):
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza"
                }
            )

            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

            # Clean up: Delete the new message
            new_message = Message.query.filter_by(body="Hello 👋").first()
            db.session.delete(new_message)
            db.session.commit()

    def test_updates_body_of_message_in_database(self):
        with app.app_context():
            # Create a new message
            new_message = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(new_message)
            db.session.commit()

            # Get the ID of the new message
            id = new_message.id

            # Update the body of the message
            app.test_client().patch(
                f'/messages/{id}',
                json={
                    "body": "Goodbye 👋"
                }
            )

            updated_message = Message.query.filter_by(id=id).first()
            assert updated_message is not None
            assert updated_message.body == "Goodbye 👋"

            # Clean up: Delete the updated message
            db.session.delete(updated_message)
            db.session.commit()

    def test_deletes_message_from_database(self):
        with app.app_context():
            # Create a new message to be deleted
            message_to_delete = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(message_to_delete)
            db.session.commit()

            # Get the ID of the message to be deleted
            id = message_to_delete.id

            # Delete the message
            app.test_client().delete(f'/messages/{id}')

            deleted_message = Message.query.filter_by(id=id).first()
            assert deleted_message is None

