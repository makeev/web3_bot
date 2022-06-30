from hashlib import sha1

from umongo import Document, fields

from app import get_app
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
class User(Document):
    name = fields.StringField(allow_none=True)
    email = fields.EmailField(unique=True, required=True)
    password = fields.StringField()

    permissions = fields.ListField(fields.StringField(), default=list)

    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

    class Meta:
        collection_name = 'users'

    def set_password(self, password):
        self.password = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        return sha1((password + 'my f#cking salt').encode()).hexdigest()

    @classmethod
    async def authenticate(cls, email, password):
        user = await cls.find_one({"email": email})
        if user and user.password == cls.hash_password(password):
            return user

    @classmethod
    async def create_user(cls, email, password):
        user = cls(
            email=email
        )
        user.set_password(password)
        await user.commit()

        return user


@app.ctx.umongo.register
@add_timestamp
class UserLog(Document):
    user = fields.ReferenceField(User)
    action = fields.StringField()
    path = fields.StringField()
    details = fields.StringField()

    class Meta:
        collection_name = 'user_logs'
        indexes = ['user']
