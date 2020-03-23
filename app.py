from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import pymysql
from pymysql.err import IntegrityError
import datetime
from DButil import getUser, getArticles, getArticle

app = Flask(__name__)
app.secret_key = 'jiselectric'

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='123456789',
                       db='jiselectric',
                       charset='utf8')

RESPONSE_SUCCESS = 'success'
RESPONSE_FAIL = 'fail'

###################################################################################
@app.route('/')
@app.route('/article')
def article():
    user = getUser(conn, session)
    articles = getArticles(conn)
    warning = request.args.get('warning')
    if warning is not None:
        return render_template('article.html', alert=warning, user=user, articles=articles)
    else:
        return render_template('article.html', alert=None, user=user, articles=articles)

@app.route('/show_check', methods=['POST'])
def show_check():
    pw = request.form.get('pw')
    sn = request.form.get('sn')
    sql = "SELECT * FROM article WHERE ARTICLE_SN=%s AND ARTICLE_PW=%s"
    curs = conn.cursor()
    curs.execute(sql, (sn, pw))
    result = curs.fetchall()
    if len(result) > 0:
        session["article"] = sn
        return jsonify({"result" : "success"})
    else:
        return jsonify({"result": "fail"})

@app.route('/myContent')
def myContent():
    sn = request.args.get('article_sn')
    article = getArticle(conn, sn)
    return render_template('myContent.html', article=article)

@app.route('/login_check', methods=['POST'])
def login_check():
    id = request.form.get('id')
    pw = request.form.get('pw')

    curs = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        sql = "SELECT * FROM user WHERE USER_ID=%s AND USER_PW=%s"
        curs.execute(sql, (id, pw))

        result = curs.fetchall()

        if len(result) > 0:
            user_sn = result[0]["USER_SN"]
            session['user'] = user_sn
            return redirect('article')
        else:
            sql = "SELECT * FROM user WHERE USER_ID=%s"
            curs.execute(sql, (id))
            result = curs.fetchall()
            if len(result) > 0:
                return redirect('article?warning=pw')
            else:
                return redirect('article?warning=id')

###################################################################################
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/regist', methods=['GET', 'POST'])
def regist():
    id = request.form.get('id')
    pw = request.form.get('pw')
    username = request.form.get('username')

    curs = conn.cursor()



    if request.method == 'POST':

        #체크
        if username is None or id is None:

            if username is None:
                sql = 'SELECT * FROM user WHERE USER_ID=%s'
                curs.execute(sql, (id))
                returnString = "alreadyID"
            else:
                sql = 'SELECT * FROM user WHERE USER_NAME=%s'
                curs.execute(sql, (username))
                returnString = "alreadyName"
            result = curs.fetchall()
            if len(result) > 0:
                return returnString
            else:
                return "Available"
        #가입
        else:
            sql = 'SELECT * FROM user WHERE USER_ID=%s OR USER_NAME=%s'
            curs.execute(sql, (id, username))
            result = curs.fetchall()
            if len(result) > 0:
                for r in result:
                    if r[0] == id and r[1] == username:
                        return 'alreadyBoth'
                    elif r[0] == id:
                        return 'alreadyID'
                    elif r[1] == username:
                        return 'alreadyName'
            else:
                sql = 'INSERT INTO user(USER_ID, USER_PW, USER_NAME, REGIST_DTM) VALUES(%s, %s, %s, NOW())'
                curs.execute(sql, (id, pw, username))
                conn.commit()
                return redirect('article')
###################################################################################
@app.route('/writer')
def writer():
    return render_template('writer.html')

@app.route('/write', methods=['POST'])
def write():
    title = request.form.get('title')
    content = request.form.get('content')
    user_sn = session["user"]
    sql = "INSERT INTO article(USER_SN, ARTICLE_TITLE, ARTICLE_CONTENT, REGIST_DTM) VALUES (%s, %s, %s, NOW())"
    curs = conn.cursor()
    curs.execute(sql, (user_sn, title, content))
    conn.commit()
    return redirect('article?warning=write')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('article')

########################### DELETE ACCOUNT #########################################
@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    pw = request.form.get('pw')
    user = session['user']

    curs = conn.cursor()

    if request.method == 'POST':
        sql = 'SELECT * FROM user WHERE USER_SN=%s AND USER_PW=%s'
        curs.execute(sql, (user, pw))
        result = curs.fetchall()

        if len(result) > 0:
            sql = 'DELETE FROM user WHERE USER_SN=%s'
            curs.execute(sql, (user))
            conn.commit()
            session.pop('user', None)
            return redirect('article')
        else:
            return render_template('alert.html', message='Wrong Password!', back=True)

try:
    app.run()
except:
    conn.close()