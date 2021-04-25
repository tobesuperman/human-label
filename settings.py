# app端口
APP_PORT = 7070

# 音乐的mysql配置
MUSIC_MYSQL_HOST = '110.64.66.207'
MUSIC_MYSQL_PORT = 3306
MUSIC_MYSQL_USER = 'root'
MUSIC_MYSQL_PASSWORD = '198720'
MUSIC_MYSQL_DB = 'musiclib_200508'

# 图书的mysql配置
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'ibm198720'
MYSQL_DB = 'booklib'
MYSQL_CHARSET = 'utf8mb4'

# neo4j地址
NEO4J_URL = 'http://127.0.0.1:7474'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = '123456'

# 更新solr地址
UPDATE_SOLR_URL = 'http://110.64.66.208:8081/putIndex'

# 单句搜索地址
SEARCH_URL = 'http://110.64.66.207:8181/scut/search/v1/QueryMusic'

# 数据文件配置
DATE = "210121"
# 知识图谱实体表和关系表存放路径
NEO4J_DIR = '/home/zouchao/neo4j/import/update_' + DATE
