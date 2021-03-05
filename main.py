from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/python_test.db'
db = SQLAlchemy(app)

class Article(db.Model):
    id      = db.Column(db.Integer, primary_key = True)
    author  = db.Column(db.String,  nullable = False)
    created = db.Column(db.Text,    nullable = False, default = datetime.utcnow().isoformat())
    updated = db.Column(db.Text,    nullable = False, default = datetime.utcnow().isoformat())
    content = db.Column(db.Text,    nullable = False)

    def __init__(self, author, content):
        self.author  = author
        self.content = content

    def serialize(self):
        return {"id":self.id, "author":self.author,
                "created":self.created, "updated":self.updated, "content":self.content}


db.create_all()
db.session.query(Article).delete()

Tyutchev = Article('F.I. Tyutchev', 'Lyublyu vesnu v nachale Maya')
Ribkin   = Article('V.V. Ribkin', 'QWERTY')

db.session.add(Tyutchev)
db.session.add(Ribkin)
db.session.commit()
############################################
@app.route("/api/articles", methods=["GET"])
def get_articles():
    articles = db.session.query(Article).all()
    return jsonify(list(map(lambda art: art.serialize(), articles)))

@app.route("/api/articles/<int:id>", methods=["GET"])
def get_article_by_id(id):
    article = db.session.query(Article).get(id)
    if article:
        return jsonify({"article": article.serialize()})
    else:
        return jsonify({'message': "Article " + str(id) + " not found"}), 404

@app.route("/api/articles", methods=["POST"])
def create_article():
    article = Article(request.json['author'], request.json['content'])
    if article is None: return jsonify({'message': "Article " + str(id) + " not found"}), 404
    db.session.add(article)
    db.session.commit()
    return jsonify({"article": article.serialize()})

@app.route("/api/articles/<int:id>", methods=["PUT"])
def update_article(id):
    article = db.session.query(Article).get(id)
    if article is None: return jsonify({'message': "Article " + str(id) + " not found"}), 404
    try:
        if article.author != request.json['author'] or article.content != request.json['content']:
            article.author = request.json['author']
            article.content = request.json['content']
            article.updated = datetime.utcnow().isoformat()
    except KeyError:
        return jsonify({'message': "Incorrect JSON keys or data"}), 400

    db.session.commit()
    return jsonify({'article':article.serialize()})

@app.route("/api/articles/<int:id>", methods=["DELETE"])
def delete_article(id):
    article = db.session.query(Article).get(id)
    if article:
        db.session.delete(article)
        db.session.commit()
        return jsonify({'message': "ok"})
    else:
        return jsonify({'message': "Article " + str(id) + " not found"}), 404

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'message': 'This page does not exist'}),404

@app.errorhandler(400)
def client_issues(error):
    return jsonify({'message': 'Incorrect request or data'}), 400

@app.errorhandler(500)
def service_issues(error):
    return jsonify({'message': 'Service problem'}), 500

if __name__ == '__main__':
    app.run()
