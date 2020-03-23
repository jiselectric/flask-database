import pymysql

def getUser(conn, session):
    if "user" in session:
        user_sn = session["user"]
        sql = "SELECT * FROM user WHERE USER_SN=%s"
        curs = conn.cursor(pymysql.cursors.DictCursor)
        curs.execute(sql, (user_sn))
        user = curs.fetchone()
        return user
    else:
        return None

def getArticles(conn):
    sql = "SELECT * FROM article a JOIN user u ON a.USER_SN = u.USER_SN"
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute(sql)
    articles = curs.fetchall()
    return articles

def getArticle(conn, article_sn):
    sql = "SELECT * FROM article WHERE ARTICLE_SN=%s"
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute(sql, (article_sn))
    article = curs.fetchone()
    return article
