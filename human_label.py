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


def init_log(log_path, log_name):
    logging.basicConfig(
        filename=os.path.join(log_path, log_name),
        format='%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s',
        level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    return logging.getLogger()


@app.route('/label')
def label():
    return app.send_static_file('label.html')


@app.route('/search')
def search():
    return app.send_static_file('search.html')


@app.route('/book_tag', methods=['GET'])
def book_tag():
    if request.args.get('bookId') is not None:
        book_id = int(request.args.get('bookId'))
    else:
        book_id = ''
    return render_template('book.html', pre_book_id=str(book_id))


@app.route('/get_tag', methods=['GET'])
def get_tag():
    if request.args.get('pageIndex') is not None:
        page_index = int(request.args.get('pageIndex'))
    else:
        page_index = 1
    if request.args.get('pageSize') is not None:
        page_size = int(request.args.get('pageSize'))
    else:
        page_size = 10
    if request.args.get('keyword') is not None and request.args.get('keyword') != '':
        search_word = request.args.get('keyword')
    else:
        search_word = ''
    try:
        db = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset=settings.MYSQL_CHARSET
        )
        cursor = db.cursor()
        if search_word != '':
            cursor.execute('SELECT tag_name, type FROM standard_tag WHERE tag_name LIKE %s',
                           '%' + search_word + '%')
        else:
            cursor.execute('SELECT tag_name, type FROM standard_tag')
        result = cursor.fetchall()
        system_tags = []
        human_tags = []
        for row in result:
            tag_name = row[0]
            typ = row[1]
            if typ == 'Human':
                human_tags.append({'name': tag_name, 'type': '人工添加'})
            elif typ == 'Topic':
                system_tags.append({'name': tag_name, 'type': '主题（系统自带）'})
            elif typ == 'Genre':
                system_tags.append({'name': tag_name, 'type': '体裁（系统自带）'})
            else:
                system_tags.append({'name': tag_name, 'type': '其他（系统自带）'})
        cursor.close()
        db.close()
        show_tags = human_tags + system_tags
        result_dict = {
            'status': 'success',
            'tags': show_tags[(page_index - 1) * page_size:page_index * page_size],
            'total': len(show_tags),
        }
        return jsonify(result_dict)
    except Exception:
        logger.error('获取标签体系出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/add_tag', methods=['GET'])
def add_tag():
    if request.args.get('addTag') is not None and request.args.get('addTag') != '':
        tag = request.args.get('addTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏要添加的标签名'})
    try:
        db = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset=settings.MYSQL_CHARSET
        )
        cursor = db.cursor()
        cursor.execute('SELECT count(*) FROM standard_tag WHERE tag_name = %s', tag)
        res = cursor.fetchone()[0]
        if res > 0:
            return jsonify({'status': 'failed', 'msg': '已经存在该标签！'})

        g = py2neo.Graph(
            settings.NEO4J_URL,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD
        )
        g.run('MERGE (t:Tag:Human{name:{tag}})', tag=tag)
        g.run('MATCH (t:Tag{name:{tag}}) SET t.update_time=timestamp()', tag=tag)
        result_count = cursor.execute('INSERT INTO standard_tag(tag_name, type) VALUES(%s,\'Human\')', tag)

        db.commit()
        cursor.close()
        db.close()
        result_dict = {'status': 'success', 'msg': '添加' + str(result_count) + '条标签记录！'}
        print(result_dict)
        logger.info('人工添加1个标签[' + tag + ']！')
        return jsonify(result_dict)
    except Exception:
        logger.error('人工添加标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/del_tag', methods=['GET'])
def del_tag():
    if request.args.get('delTag') is not None and request.args.get('delTag') != '':
        tag = request.args.get('delTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏要删除的标签名'})
    try:
        db = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset=settings.MYSQL_CHARSET
        )
        cursor = db.cursor()

        g = py2neo.Graph(
            settings.NEO4J_URL,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD
        )
        g.run('MATCH(n:Tag{name:{tag}}) DETACH DELETE n', tag=tag)
        result_count = cursor.execute('DELETE FROM standard_tag WHERE type = \'Human\' AND tag_name = %s', tag)
        db.commit()
        cursor.close()
        db.close()
        result_dict = {'status': 'success', 'msg': '本次删除' + str(result_count) + '条标签记录！'}
        logger.info('人工删除1个标签[' + tag + ']！')
        return jsonify(result_dict)
    except Exception:
        logger.error('人工删除标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/get_book_tag', methods=['GET'])
def get_book_tag():
    if request.args.get('bookId') is not None and request.args.get('bookId') != '':
        book_id = request.args.get('bookId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏图书ID'})
    try:
        db = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset=settings.MYSQL_CHARSET
        )
        cursor = db.cursor()
        cursor.execute('SELECT id, title, actor, final_tag, final_tag_pro, movie_tag FROM multimodal_tag WHERE id = %s',
                       book_id)
        result = cursor.fetchone()
        if result is None:
            cursor.execute('SELECT book_id FROM search_content WHERE book_id = %s', int(book_id))
            result = cursor.fetchone()
            # search_content中没有
            if result is None:
                return jsonify({'status': 'failed', 'msg': '数据库中找不到图书！'})
            # search_content中有但是multimodal_tag没有，添加进去
            else:
                update_mysql = '''INSERT IGNORE INTO multimodal_tag(id,title,actor,final_tag,final_tag_pro,movie_tag)
                                SELECT t1.book_id, t1.title, t1.singer, '', '{}', ''
                                FROM search_content AS t1 WHERE t1.book_id = %s'''
                cursor.execute(update_mysql, int(book_id))
                db.commit()
                cursor.execute(
                    'SELECT id, title, actor, final_tag, final_tag_pro, movie_tag FROM multimodal_tag WHERE id = %s',
                    book_id)
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
        result_dict = {
            'status': 'success',
            'book_id': idx,
            'title': title,
            'actor': actor,
            'book_tag_pro': final_tag_pro_text,
            'book_tag': list(final_tag_pro.keys()),
            'human_tag': final_tag,
            'movie_tag': list(movie_tag)
        }
        return jsonify(result_dict)
    except Exception:
        logger.error('获取图书标签出错!')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/add_book_tag', methods=['GET'])
def add_book_tag():
    if request.args.get('bookId') is not None and request.args.get('bookId') != '':
        book_id = request.args.get('bookId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏图书ID'})
    if request.args.get('bookTag') is not None and request.args.get('bookTag') != '':
        tag = request.args.get('bookTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏图书标签'})
    try:
        db = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset=settings.MYSQL_CHARSET
        )
        cursor = db.cursor()
        cursor.execute('SELECT id FROM standard_tag WHERE tag_name = %s', tag)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签体系尚未有该标签，请先添加！'})
        cursor.execute('SELECT id, title, actor, final_tag, final_tag_pro FROM multimodal_tag WHERE id = %s', book_id)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '找不到该图书的标签！'})
        else:
            book_id = result[0]
            title = result[1]
            actor = result[2]
            human_final_tag_text = result[3]
            if human_final_tag_text is not None and human_final_tag_text != '':
                human_final_tag = json.loads(human_final_tag_text)
            else:
                human_final_tag = {}
            final_tag_pro_text = result[4]
            final_tag_pro = json.loads(final_tag_pro_text)
            if tag in final_tag_pro:
                return jsonify({'status': 'failed', 'msg': '该图书已经有[' + tag + ']标签！'})
            else:
                final_tag_pro[tag] = 1
                human_final_tag['normal_tag'] = final_tag_pro
                new_human_final_tag_text = json.dumps(human_final_tag, ensure_ascii=False)
                new_final_tag_pro_text = json.dumps(final_tag_pro, ensure_ascii=False)
                new_final_tag_text = ','.join(final_tag_pro.keys())
        cursor.execute('UPDATE multimodal_tag SET final_tag = %s , final_tag_pro = %s WHERE id = %s'
                       , (new_human_final_tag_text, new_final_tag_pro_text, book_id))

        g = py2neo.Graph(
            settings.NEO4J_URL,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD
        )
        g.run(
            'MERGE (b:Book {bookId:{id}}) '
            'ON CREATE SET b.name={title},b.update_time=timestamp() '
            'ON MATCH SET b.name={title},b.update_time=timestamp()',
            id='book' + str(book_id),
            title=title
        )
        g.run(
            'MATCH (b:Book{BookId:{id}}) MATCH (t:Tag{name:{tag}}) MERGE (s)-[:R_BookTag]->(t)',
            id='book' + str(book_id),
            tag=tag
        )

        db.commit()
        cursor.close()
        db.close()
        # 通知solr
        requests.post(
            settings.UPDATE_SOLR_URL,
            data=json.dumps([str(book_id)]),
            headers={'Content-Type': 'application/json'}
        )

        result_dict = {
            'status': 'success',
            'msg': '[' + actor + ']的[' + title + ']成功添加了[' + tag + ']标签！'
        }
        logger.info(actor + '的' + title + '成功添加了[' + tag + ']标签！')
        return jsonify(result_dict)
    except Exception:
        logger.error('增加图书标签出错!')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/del_book_tag', methods=['GET'])
def del_book_tag():
    if request.args.get('bookId') is not None and request.args.get('bookId') != '':
        book_id = request.args.get('bookId')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏图书ID'})
    if request.args.get('bookTag') is not None and request.args.get('bookTag') != '':
        tag = request.args.get('bookTag')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏图书标签'})
    try:
        db = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset=settings.MYSQL_CHARSET
        )
        cursor = db.cursor()
        cursor.execute('SELECT id FROM standard_tag WHERE tag_name = %s', tag)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签体系尚未有该标签，请先添加！'})
        cursor.execute('SELECT id, title, actor, final_tag, final_tag_pro FROM multimodal_tag WHERE id = %s', book_id)
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 'failed', 'msg': '标签表中暂时还没有这首歌，请先查询一次！'})
        else:
            book_id = result[0]
            title = result[1]
            actor = result[2]
            human_final_tag_text = result[3]
            if human_final_tag_text is not None and human_final_tag_text != '':
                human_final_tag = json.loads(human_final_tag_text)
            else:
                human_final_tag = {}
            final_tag_pro_text = result[4]
            final_tag_pro = json.loads(final_tag_pro_text)
            if tag not in final_tag_pro:
                return jsonify({'status': 'failed', 'msg': '该图书没有该标签！'})
            else:
                del final_tag_pro[tag]
                human_final_tag['normal_tag'] = final_tag_pro
                new_human_final_tag_text = json.dumps(human_final_tag, ensure_ascii=False)
                new_final_tag_pro_text = json.dumps(final_tag_pro, ensure_ascii=False)
        cursor.execute('UPDATE multimodal_tag SET final_tag = %s,final_tag_pro = %s WHERE id = %s',
                       (new_human_final_tag_text, new_final_tag_pro_text, book_id))

        g = py2neo.Graph(
            settings.NEO4J_URL,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD
        )
        query = 'MATCH (b:Book{bookId:{id}})-[r:R_BookTag]->(t:Tag{name:{tag}}) DELETE r'
        g.run(query, id='book' + str(book_id), tag=tag)
        db.commit()
        cursor.close()
        db.close()
        # 通知solr
        requests.post(
            settings.UPDATE_SOLR_URL,
            data=json.dumps([str(book_id)]),
            headers={'Content-Type': 'application/json'}
        )
        result_dict = {'status': 'success',
                       'msg': '[' + actor + ']的[' + title + ']成功删除了[' + tag + ']标签！'}
        logger.info(actor + '的' + title + '成功删除了[' + tag + ']标签！')
        return jsonify(result_dict)
    except Exception:
        logger.error('删除图书标签出错！')
        logger.error(traceback.format_exc())
        return jsonify({'status': 'failed', 'msg': '未知错误'})


@app.route('/search_book', methods=['GET'])
def search_book():
    if request.args.get('keyword') is not None and request.args.get('keyword') != '':
        keyword = request.args.get('keyword')
    else:
        return jsonify({'status': 'failed', 'msg': '缺乏搜索关键词'})
    if request.args.get('pageIndex') is not None and request.args.get('pageIndex') != '':
        page_index = request.args.get('pageIndex')
    else:
        page_index = 0
    if request.args.get('pageSize') is not None and request.args.get('pageSize') != '':
        page_size = request.args.get('pageSize')
    else:
        page_size = 10
    search_result = requests.get(
        settings.SEARCH_URL + '?Keyword=' + keyword + '&PageIndex=' + str(page_index) + '&PageSize=' + str(
            page_size) + '&channel=THIRDPARTY&biz=qu')
    search_result_dict = search_result.json()
    logger.info('搜索"' + keyword + '"')
    return jsonify(search_result_dict)


if __name__ == '__main__':
    logger = init_log(os.getcwd() + '/log', 'human_label.log')
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=settings.APP_PORT)
