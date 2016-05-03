#!/usr/bin/env python
# coding: utf-8
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
from sqlalchemy.orm import sessionmaker
from PIL import Image
import models
app = Flask(__name__)
app.debug = True
Session = sessionmaker(bind=models.engine)
image_dir = 'image/'
available_mimetypes = ['image/gif', 'image/png', 'image/jpeg']


@app.route('/')
def index():
    session = Session()
    images = session.query(models.Image).order_by(models.Image.created_at)
    return render_template('index.html', images=images)


@app.route('/upload', methods=['POST'])
def upload():
    session = Session()
    new_id = session.query(models.Image).order_by(models.Image.created_at.desc()).first().id + 1
    image_path = '{}{}.png'.format(image_dir, new_id)
    f = request.files['file']
    if f.mimetype not in available_mimetypes:
        return redirect(url_for('index'))
    image = models.Image(id=new_id, created_at=datetime.now())
    f.save(image_path)
    img = Image.open(image_path)
    thumbnail_path = '{}thumbnail/{}.png'.format(image_dir, new_id)
    img.thumbnail((128, 128))
    img.save(thumbnail_path)
    session.add(image)
    session.commit()
    return redirect(url_for('show_image_page', id=new_id))


@app.route('/{}<id>.png'.format(image_dir))
def show_image(id):
    mode = request.args.get('mode', '')
    if mode == 'thumbnail':
        image_path = '{}thumbnail/{}.png'.format(image_dir, id)
    else:
        image_path = '{}{}.png'.format(image_dir, id)
    return send_file(image_path)


@app.route('/{}<id>'.format(image_dir))
def show_image_page(id):
    session = Session()
    images = session.query(models.Image).filter(models.Image.id == id).one()
    return render_template('show_image.html', id=id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

