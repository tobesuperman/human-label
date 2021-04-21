import json
import requests
import logging
import os
import traceback

import py2neo
from flask import Flask, request, render_template
from flask import jsonify
import pymysql
import settings

app = Flask(__name__, static_folder='static/', static_url_path='')


def init_log(LOG_PATH, LOG_NAME):
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, LOG_NAME),
        format='%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s',
        level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger()
    return logger


@app.route('/label')
def label():
    return app.send_static_file('label.html')


@app.route('/search')
def search():
    return app.send_static_file('search.html')


@app.route('/song_label', methods=['GET'])
def song_label():
    if request.args.get('songid') is not None:
        song_id = int(request.args.get('songid'))
    else:
        song_id = ''
    return render_template('song.html', pre_song_id=str(song_id))


@app.route('/get_label', methods=['GET'])
def get_label():
    if request.args.get('PageIndex') is not None:
        page_index = int(request.args.get('PageIndex'))
    else:
        page_index = 1
    if request.args.get('PageSize') is not None:
        page_size = int(request.args.get('PageSize'))
    else:
        page_size = 8
    if request.args.get('SearchWord') is not None and request.args.get('SearchWord') != '':
        # search_word = pymysql.escape_string(request.args.get('SearchWord'))
        search_word = request.args.get('SearchWord')
    else:
        search_word = ''
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        if search_word != '':
            cursor.execute('SELECT tagname,type FROM standard_label WHERE tagname LIKE %s', '%' + search_word + '%')
        else:
            cursor.execute('SELECT tagname,type FROM standard_label')
        result = cursor.fetchall()
        system_labels = []
        human_labels = []
        for row in result:
            tag_name = row[0]
            typ = row[1]
            if typ == 'Human':
                human_labels.append({'name': tag_name, 'type': '人工添加'})
            else:
                system_labels.append({'name': tag_name, 'type': '系统自带'})
        cursor.close()
        db.close()
        show_labels = human_labels + system_labels
        result_dict = {'status': 'success'}
        result_dict['labels'] = show_labels[(page_index - 1) * page_size:page_index * page_size]
        result_dict['total'] = len(show_labels)
        return jsonify(result_dict)
    except Exception:
        logger.error('获取标签体系出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/add_label', methods=['GET'])
def add_label():
    if request.args.get('AddTag') is not None and request.args.get('AddTag') != '':
        add_tag = request.args.get('AddTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏要添加的标签名'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        cursor.execute('SELECT count(*) FROM standard_label WHERE tagname = %s', add_tag)
        tag_count = cursor.fetchone()[0]
        print(tag_count)
        if tag_count > 0:
            return jsonify({'status': 'failed', 'msg': '已经存在该标签！'})
        for url in settings.NEO4J_URLS:
            g = py2neo.Graph(url)
            g.run('MERGE (t:Label:Human{ name:{tag}})', tag=add_tag)
            g.run('MATCH (t:Label{ name:{tag}}) SET t.update_time=timestamp()', tag=add_tag)
        result_count = cursor.execute('INSERT INTO standard_label(tagname,type) VALUES(%s,\'Human\')', add_tag)
        db.commit()
        cursor.close()
        db.close()
        result_dict = {'status': 'success', 'msg': '添加' + str(result_count) + '条标签记录！'}
        print(result_dict)
        logger.info('人工添加1个标签[' + add_tag + ']！')
        return jsonify(result_dict)
    except Exception:
        logger.error('人工添加标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/del_label', methods=['GET'])
def del_label():
    if request.args.get('DelTag') is not None and request.args.get('DelTag') != '':
        del_tag = request.args.get('DelTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏要删除的标签名'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        for url in settings.NEO4J_URLS:
            g = py2neo.Graph(url)
            g.run('MATCH(n:Label{name:{tag}}) DETACH DELETE n', tag=del_tag)
        result_count = cursor.execute('DELETE FROM standard_label WHERE type = \'Human\' AND tagname = %s', del_tag)
        db.commit()
        cursor.close()
        db.close()
        result_dict = {'status': 'success', 'msg': '本次删除' + str(result_count) + '条标签记录！'}
        logger.info('人工删除1个标签[' + del_tag + ']！')
        return jsonify(result_dict)
    except Exception:
        logger.error('人工删除标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/get_song_label', methods=['GET'])
def get_song_label():
    if request.args.get('SongId') is not None and request.args.get('SongId') != '':
        song_id = request.args.get('SongId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲ID'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        cursor.execute('SELECT id,title,actor,final_tag,final_tag_pro,movie_tag FROM multimodal_tag WHERE id = %s',
                       song_id)
        result = cursor.fetchone()
        if result is None:
            cursor.execute('SELECT songid FROM search_content WHERE songid = %s', int(song_id))
            result = cursor.fetchone()
            # search_content中没有
            if result is None:
                return jsonify({'status': 'failed', 'msg': 'search_content中找不到该歌曲！'})
            # search_content中有但是multimodal_tag没有，添加进去
            else:
                update_mysql = '''INSERT IGNORE INTO multimodal_tag(id,title,actor,final_tag,final_tag_pro,movie_tag)
                                SELECT t1.songid, t1.title, t1.singer, '', '{}', ''
                                FROM search_content AS t1 WHERE t1.songid = %s'''
                cursor.execute(update_mysql, int(song_id))
                db.commit()
                cursor.execute(
                    'SELECT id,title,actor,final_tag,final_tag_pro,movie_tag FROM multimodal_tag WHERE id = %s',
                    song_id)
                result = cursor.fetchone()
        idx = result[0]
        title = result[1]
        actor = result[2]
        final_tag = result[3]
        final_tag_pro_text = result[4]
        final_tag_pro = json.loads(final_tag_pro_text)
        movie_tag = result[5].split(',')
        movie_tag = set(movie_tag)
        movie_tag.discard('')
        cursor.close()
        db.close()
        result_dict = {'status': 'success',
                       'song_id': idx,
                       'title': title,
                       'actor': actor,
                       'song_label_pro': final_tag_pro_text,
                       'song_label': list(final_tag_pro.keys()),
                       'human_label': final_tag,
                       'movie_tag': list(movie_tag)}
        return jsonify(result_dict)
    except Exception:
        logger.error('获取歌曲标签出错!')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/add_song_label', methods=['GET'])
def add_song_label():
    if request.args.get('SongId') is not None and request.args.get('SongId') != '':
        song_id = request.args.get('SongId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲ID'})
    if request.args.get('SongTag') is not None and request.args.get('SongTag') != '':
        song_tag = request.args.get('SongTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲标签'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        cursor.execute('SELECT id FROM standard_label WHERE tagname = %s', song_tag)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签体系尚未有该标签，请先添加！'})
        cursor.execute('SELECT id,title,actor,final_tag,final_tag_pro FROM multimodal_tag WHERE id = %s', song_id)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '找不到该歌曲的标签！'})
        else:
            song_id = result[0]
            title = result[1]
            actor = result[2]
            human_final_tag_text = result[3]
            if human_final_tag_text is not None and human_final_tag_text != '':
                human_final_tag = json.loads(human_final_tag_text)
            else:
                human_final_tag = {}
            final_tag_pro_text = result[4]
            final_tag_pro = json.loads(final_tag_pro_text)
            if song_tag in final_tag_pro:
                return jsonify({'status': 'failed', 'msg': '该歌曲已经有[' + song_tag + ']标签！'})
            else:
                final_tag_pro[song_tag] = 1
                human_final_tag['normal_tag'] = final_tag_pro
                new_human_final_tag_text = json.dumps(human_final_tag, ensure_ascii=False)
                new_final_tag_pro_text = json.dumps(final_tag_pro, ensure_ascii=False)
                new_final_tag_text = ','.join(final_tag_pro.keys())
        cursor.execute('UPDATE multimodal_tag SET final_tag = %s , final_tag_pro = %s WHERE id = %s'
                       , (new_human_final_tag_text, new_final_tag_pro_text, song_id))
        for url in settings.NEO4J_URLS:
            g = py2neo.Graph(url)
            g.run('MERGE (s:Song {songid:{id}}) '
                  'ON CREATE SET s.name={title},s.update_time=timestamp() '
                  'ON MATCH SET s.name={title},s.update_time=timestamp()', id='song' + str(song_id), title=title)
            g.run('MATCH (s:Song{songid:{id}}) MATCH (t:Label{name:{tag}}) MERGE (s)-[:R_HasLabel]->(t)',
                  id='song' + str(song_id), tag=song_tag)

        db.commit()
        cursor.close()
        db.close()
        # 通知solr
        requests.post(settings.UPDATE_SOLR_URL, data=json.dumps([str(song_id)]),
                      headers={'Content-Type': 'application/json'})

        result_dict = {'status': 'success',
                       'msg': '[' + actor + ']的[' + title + ']成功添加了[' + song_tag + ']标签！'}
        logger.info(actor + '的' + title + '成功添加了[' + song_tag + ']标签！')
        return jsonify(result_dict)
    except Exception:
        logger.error('增加歌曲标签出错!')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/del_song_label', methods=['GET'])
def del_song_label():
    if request.args.get('SongId') is not None and request.args.get('SongId') != '':
        song_id = request.args.get('SongId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲ID'})
    if request.args.get('SongTag') is not None and request.args.get('SongTag') != '':
        song_tag = request.args.get('SongTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲标签'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        cursor.execute('SELECT id FROM standard_label WHERE tagname = %s', song_tag)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签体系尚未有该标签，请先添加！'})
        cursor.execute('SELECT id,title,actor,final_tag,final_tag_pro FROM multimodal_tag WHERE id = %s', song_id)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签表中暂时还没有这首歌，请先查询一次！'})
        else:
            song_id = result[0]
            title = result[1]
            actor = result[2]
            human_final_tag_text = result[3]
            if human_final_tag_text is not None and human_final_tag_text != '':
                human_final_tag = json.loads(human_final_tag_text)
            else:
                human_final_tag = {}
            final_tag_pro_text = result[4]
            final_tag_pro = json.loads(final_tag_pro_text)
            if song_tag not in final_tag_pro:
                return jsonify({'status': 'failed', 'msg': '该歌曲没有该标签！'})
            else:
                del final_tag_pro[song_tag]
                human_final_tag['normal_tag'] = final_tag_pro
                new_human_final_tag_text = json.dumps(human_final_tag, ensure_ascii=False)
                new_final_tag_pro_text = json.dumps(final_tag_pro, ensure_ascii=False)
        cursor.execute('UPDATE multimodal_tag SET final_tag = %s,final_tag_pro = %s WHERE id = %s',
                       (new_human_final_tag_text, new_final_tag_pro_text, song_id))
        for url in settings.NEO4J_URLS:
            g = py2neo.Graph(url)
            query = 'MATCH (s:Song{songid:{id}})-[r:R_HasLabel]->(t:Label{name:{tag}}) DELETE r'
            g.run(query, id='song' + str(song_id), tag=song_tag)
        db.commit()
        cursor.close()
        db.close()
        # 通知solr
        requests.post(settings.UPDATE_SOLR_URL, data=json.dumps([str(song_id)]),
                      headers={'Content-Type': 'application/json'})
        result_dict = {'status': 'success',
                       'msg': '[' + actor + ']的[' + title + ']成功删除了[' + song_tag + ']标签！'}
        logger.info(actor + '的' + title + '成功删除了[' + song_tag + ']标签！')
        return jsonify(result_dict)
    except Exception:
        logger.error('删除歌曲标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/add_movie_label', methods=['GET'])
def add_movie_label():
    if request.args.get('SongId') is not None and request.args.get('SongId') != '':
        song_id = request.args.get('SongId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲ID'})
    if request.args.get('MovieTag') is not None and request.args.get('MovieTag') != '':
        add_movie_tag = request.args.get('MovieTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏影视剧标签'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        cursor.execute('SELECT id,title,actor,final_tag,movie_tag FROM multimodal_tag WHERE id = %s', song_id)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签表中暂时还没有这首歌，请先查询一次！'})
        else:
            song_id = result[0]
            title = result[1]
            actor = result[2]
            human_final_tag_text = result[3]
            if human_final_tag_text is not None and human_final_tag_text != '':
                human_final_tag = json.loads(human_final_tag_text)
            else:
                human_final_tag = {}
            movie_tag_text = result[4]
            movie_tag = movie_tag_text.split(',')
            if add_movie_tag in movie_tag:
                return jsonify({'status': 'failed', 'msg': '该歌曲已经有[' + add_movie_tag + ']影视剧标签！'})
            else:
                movie_tag = set(movie_tag)
                movie_tag.discard('')
                movie_tag.add(add_movie_tag)
                new_movie_tag_text = ','.join(movie_tag)
                movie_tag_dict = {}
                for i in movie_tag:
                    movie_tag_dict[i] = 1
                human_final_tag['movie_tag'] = movie_tag_dict
                new_human_final_tag_text = json.dumps(human_final_tag, ensure_ascii=False)
        cursor.execute('UPDATE multimodal_tag SET final_tag = %s,movie_tag = %s WHERE id = %s',
                       (new_human_final_tag_text, new_movie_tag_text, song_id))
        for url in settings.NEO4J_URLS:
            g = py2neo.Graph(url)
            query = '''
                    MATCH (a:Song{songid:{id}})
                    MERGE (b:MovieLabel{name:{tag}})
                    ON CREATE SET b.update_time=timestamp()
                    ON MATCH SET b.update_time=timestamp()
                    MERGE (a)-[:R_HasLabel]->(b)
                    '''
            g.run(query, id='song' + str(song_id), tag=add_movie_tag)
        db.commit()
        cursor.close()
        db.close()
        # 通知solr
        requests.post(settings.UPDATE_SOLR_URL, data=json.dumps([str(song_id)]),
                      headers={'Content-Type': 'application/json'})
        result_dict = {'status': 'success',
                       'msg': '[' + actor + ']的[' + title + ']成功添加了[' + add_movie_tag + ']影视标签！'}
        logger.info(actor + '的' + title + '成功添加了[' + add_movie_tag + ']影视标签！')
        return jsonify(result_dict)
    except Exception:
        logger.error('添加歌曲影视标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/del_movie_label', methods=['GET'])
def del_movie_label():
    if request.args.get('SongId') is not None and request.args.get('SongId') != '':
        song_id = request.args.get('SongId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏歌曲ID'})
    if request.args.get('MovieTag') is not None and request.args.get('MovieTag') != '':
        del_movie_tag = request.args.get('MovieTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏影视剧标签'})
    try:
        db = pymysql.connect(host=settings.MUSIC_MYSQL_HOST, port=settings.MUSIC_MYSQL_PORT, user=settings.MUSIC_MYSQL_USER,
                             password=settings.MUSIC_MYSQL_PASSWORD, database=settings.MUSIC_MYSQL_DB)
        cursor = db.cursor()
        cursor.execute('SELECT id,title,actor,final_tag,movie_tag FROM multimodal_tag WHERE id = %s', song_id)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '找不到该歌曲的影视标签！'})
        else:
            song_id = result[0]
            title = result[1]
            actor = result[2]
            human_final_tag_text = result[3]
            if human_final_tag_text is not None and human_final_tag_text != '':
                human_final_tag = json.loads(human_final_tag_text)
            else:
                human_final_tag = {}
            movie_tag_text = result[4]
            movie_tag = movie_tag_text.split(',')
            if del_movie_tag not in movie_tag:
                return jsonify({'status': 'failed', 'msg': '该歌曲没有[' + del_movie_tag + ']标签！'})
            else:
                movie_tag = set(movie_tag)
                movie_tag.discard(del_movie_tag)
                new_movie_tag_text = ','.join(movie_tag)
                movie_tag_dict = {}
                for i in movie_tag:
                    movie_tag_dict[i] = 1
                human_final_tag['movie_tag'] = movie_tag_dict
                new_human_final_tag_text = json.dumps(human_final_tag, ensure_ascii=False)
        cursor.execute('UPDATE multimodal_tag SET final_tag = %s, movie_tag = %s WHERE id = %s',
                       (new_human_final_tag_text, new_movie_tag_text, song_id))
        for url in settings.NEO4J_URLS:
            g = py2neo.Graph(url)
            query = 'MATCH (s:Song{songid:{id}})-[r:R_HasLabel]->(t:MovieLabel{name:{tag}}) DELETE r'
            g.run(query, id='song' + str(song_id), tag=del_movie_tag)
        db.commit()
        cursor.close()
        db.close()
        # 通知solr
        requests.post(settings.UPDATE_SOLR_URL, data=json.dumps([str(song_id)]),
                      headers={'Content-Type': 'application/json'})
        result_dict = {'status': 'success',
                       'msg': '[' + actor + ']的[' + title + ']成功删除了[' + del_movie_tag + ']标签！'}
        logger.info(actor + '的' + title + '成功删除了[' + del_movie_tag + ']标签！')
        return jsonify(result_dict)
    except Exception:
        logger.error('删除歌曲影视标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/search_song', methods=['GET'])
def search_song():
    if request.args.get('keyword') is not None and request.args.get('keyword') != '':
        keyword = request.args.get('keyword')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏搜索关键词'})
    if request.args.get('pagenum') is not None and request.args.get('pagenum') != '':
        page_num = request.args.get('pagenum')
    else:
        page_num = 0
    if request.args.get('pagesize') is not None and request.args.get('pagenum') != '':
        page_size = request.args.get('pagesize')
    else:
        page_size = 8
    search_result = requests.get(
        settings.SEARCH_URL + '?Keyword=' + keyword + '&PageIndex=' + str(page_num) + '&PageSize=' + str(
            page_size) + '&channel=THIRDPARTY&biz=qu')
    search_result_dict = search_result.json()
    logger.info('搜索"' + keyword + '"')
    return jsonify(search_result_dict)


if __name__ == '__main__':
    logger = init_log(os.getcwd() + '/log', 'human_label_log')
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=settings.APP_PORT)
