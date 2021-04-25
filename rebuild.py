import pymysql
import os
import pandas as pd
import settings


def get_tags_from_csv(filename: str) -> (str, set):
    content = pd.read_csv(filename, low_memory=False)
    result = set(content['name'].astype(str))
    label = list(content[':LABEL'].astype(str))[0]
    return label, result


def update_tag():
    item_dict = dict()
    items = ["topic", "genre"]

    certain_tags = set()
    for i in items:
        filename = os.path.join(settings.NEO4J_DIR, "%s.csv" % i)
        label, item_tags = get_tags_from_csv(filename)
        item_dict[label] = item_tags
        certain_tags = certain_tags | item_tags

    tag_file = os.path.join(settings.NEO4J_DIR, "tag.csv")
    _, all_tags = get_tags_from_csv(tag_file)
    other_tags = all_tags - certain_tags
    item_dict['Other'] = other_tags

    db = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB,
        charset=settings.MYSQL_CHARSET,
    )

    data = list()
    for key, value in item_dict.items():
        for v in value:
            data.append([v, key])
    cursor = db.cursor()
    truncate_sql = 'TRUNCATE standard_tag'
    insert_sql = 'INSERT INTO standard_tag(tag_name, type) VALUES(%s, %s)'
    try:
        res = cursor.execute(truncate_sql)
        res = cursor.executemany(insert_sql, data)
        db.commit()
        print("执行sql语句成功，共插入了%d条数据！" % res)
    except IOError:
        print("执行sql语句失败！")
        db.rollback()
    else:
        cursor.close()
        db.close()


if __name__ == '__main__':
    update_tag()
