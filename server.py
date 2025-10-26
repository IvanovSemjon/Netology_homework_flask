import json

from aiohttp import web
from aiohttp.web import Application, Request, json_response, run_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession as SessType

from auth import hash_password
from model import AsyncSession, User, close_db, init_db


app = Flask("app")
app.config["JSON_AS_ASCII"] = False


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def check_auth():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        raise HttpError(401, "Authorization required")

    try:
        credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
        email, password = credentials.split(":", 1)

        user = request.session.query(User).filter(User.email == email).first()
        if not user or user.password_hash != hash_password(password):
            raise HttpError(401, "Invalid credentials")

        return user
    except Exception:
        raise HttpError(401, "Invalid authorization format")


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    http_response = jsonify({"Error": error.message})
    http_response.status_code = error.status_code
    return http_response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


def get_ad_by_id(ad_id: int):
    ad = request.session.get(Bulletin_board, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


def add_ad(ad: Bulletin_board):
    request.session.add(ad)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "ad creation failed")


def add_user(user: User):
    request.session.add(user)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "user already exists")


class UserView(MethodView):
    def post(self):
        json_data = validate(CreateUserRequest, request.json)
        user = User(
            email=json_data["email"], password_hash=hash_password(json_data["password"])
        )
        add_user(user)
        return jsonify(user.id_json)


class AdView(MethodView):
    def get(self, ad_id: int):
        ad = get_ad_by_id(ad_id)
        return jsonify(ad.json)

    def post(self):
        user = check_auth()  # Только авторизованные пользователи
        json_data = validate(CreateAdsRequest, request.json)
        ad = Bulletin_board(
            title=json_data["title"], text=json_data["text"], user_id=user.id
        )
        add_ad(ad)
        return jsonify(ad.id_json)

    def patch(self, ad_id: int):
        user = check_auth()  # Только авторизованные пользователи
        ad = get_ad_by_id(ad_id)

        if ad.user_id != user.id:  # Только владелец может редактировать
            raise HttpError(403, "Access denied")

        json_data = validate(UpdateAdsRequest, request.json)
        if "title" in json_data:
            ad.title = json_data["title"]
        if "text" in json_data:
            ad.text = json_data["text"]
        add_ad(ad)
        return jsonify(ad.json)

    def delete(self, ad_id: int):
        user = check_auth()  # Только авторизованные пользователи
        ad = get_ad_by_id(ad_id)

        if ad.user_id != user.id:  # Только владелец может удалять
            raise HttpError(403, "Access denied")

        request.session.delete(ad)
        request.session.commit()
        return jsonify({"status": "ad deleted"})


user_view = UserView.as_view("user_view")
ad_view = AdView.as_view("ad_view")

app.add_url_rule("/users", view_func=user_view, methods=["POST"])
app.add_url_rule(
    "/ads/<int:ad_id>", view_func=ad_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/ads", view_func=ad_view, methods=["POST"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
