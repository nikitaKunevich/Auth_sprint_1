import flask_praetorian
import redis

guard = flask_praetorian.Praetorian()

jwt_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
