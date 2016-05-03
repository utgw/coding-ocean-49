#!/usr/bin/env python
# coding: utf-8
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
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
    sort_by = request.args.get('sort_by', 'date')
    if sort_by == 'date':
        images = session.query(models.Image).order_by(models.Image.created_at.desc())
    elif sort_by == 'star':
        images = session.query(models.Image).order_by(models.Image.star.desc())
    return render_template('index.html', images=images)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    result, poe = __upload__(f)
    if result['ok']:
        return redirect(url_for('image_controller', id=result['id']))
    else:
        return redirect(url_for('index'))


@app.route('/upload.json', methods=['POST'])
def upload_json():
    f = request.files['file']
    result, status_code = __upload__(f)
    return jsonify(result=result), status_code


def __upload__(f):
    if f.mimetype not in available_mimetypes:
        result = {
            'ok': False,
            'error': 'Invalid file type'
        }
        status_code = 400
    else:
        try:
            session = Session()
            try:
                new_id = session.query(models.Image).order_by(models.Image.created_at.desc()).first().id + 1
            except:
                new_id = 1
            image_path = '{}{}.png'.format(image_dir, new_id)
            image = models.Image(id=new_id, created_at=datetime.now(), star=0)
            f.save(image_path)
            img = Image.open(image_path)
            thumbnail_path = '{}thumbnail/{}.png'.format(image_dir, new_id)
            img.thumbnail((128, 128))
            img.save(thumbnail_path)
            session.add(image)
            session.commit()
            result = {
                'ok': True,
                'id': new_id,
                'created_at': image.created_at
            }
            status_code = 201
        except Exception as e:
            result = {
                'ok': False
            }
            status_code = 500
    return result, status_code


@app.route('/{}<id>.png'.format(image_dir))
def show_image(id):
    mode = request.args.get('mode', '')
    if mode == 'thumbnail':
        image_path = '{}thumbnail/{}.png'.format(image_dir, id)
    else:
        image_path = '{}{}.png'.format(image_dir, id)
    return send_file(image_path)


@app.route('/{}<id>'.format(image_dir), methods=['GET', 'DELETE'])
def image_controller(id):
    if request.method == 'GET':
        session = Session()
        image = session.query(models.Image).filter(models.Image.id == id).one()
        return render_template('show_image.html', id=id, image=image)
    elif request.method == 'DELETE':
        session = Session()
        image = session.query(models.Image).filter(models.Image.id == id).one()
        session.delete(image)
        session.commit()
        image_path = '{}{}.png'.format(image_dir, id)
        thumbnail_path = '{}thumbnail/{}.png'.format(image_dir, id)
        os.remove(image_path)
        os.remove(thumbnail_path)
        result = {
            'ok': True
        }
        return jsonify(result=result)


@app.route('/star/<id>', methods=['POST'])
def star_image(id):
    try:
        session = Session()
        image = session.query(models.Image).filter(models.Image.id == id).one()
        image.star += 1
        session.commit()
        result = {
            'ok': True,
            'star': image.star
        }
        status_code = 200
    except Exception as e:
        result = {
            'ok': False
        }
        status_code = 500
    return jsonify(result=result), status_code


if __name__ == '__main__':
    if not os.path.isdir('./image'):
        os.mkdir('image')
    if not os.path.isdir('./image/thumbnail'):
        os.mkdir('image/thumbnail')
    app.run(host='0.0.0.0', port=8901)

