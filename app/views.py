from flask import json,url_for,render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User
from newspaper import Article
from xml.etree  import ElementTree
from nytimesarticle import articleAPI
import requests
from itertools import repeat
from elasticsearch import Elasticsearch
import random
import operator
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import httplib2
api = articleAPI('news api key')
apikey='ny times api key'
es = Elasticsearch()
@app.route('/',methods=['GET', 'POST'])
@app.route('/index')
@login_required
def index():
    user = g.user
    name = str(user).split('\'')[1];
    query = es.search(index="user", doc_type=name, body={"size":100,"query": {"match_all": {}}})
    sample = query['hits']['hits']
    dict = {}
    for s in sample:
    		li = str(s).split(",")
		url = "http:"+li[3].split(":")[3].split('\'')[0]
		if not url:
			return redirect(url_for('index'))

		article = Article(url)
		article.download()
		article.parse()

		try:
			html_string = ElementTree.tostring(article.clean_top_node)
		except:
			html_string = "Error converting html to string."

		try:
			article.nlp()
		except:
			artstr="nlp not done"
		total=0;
		for i in article.keywords:
			total = total+1;
			if i in dict:
				dict[i] = dict[i]+1
			else:
				dict[i] = 1
    news = [];
    ct = 0;
    if es.indices.exists(index = "recommend"):
		q = es.search(index="recommend", doc_type=name, body={"size":100,"query": {"match_all": {}}});
		s = q['hits']['hits']
		ct = len(s)
    if ct > 0:
		query_r = es.search(index="recommend", doc_type=name, body={"size":100,"query": {"match_all": {}}})
		sampl_r = query_r['hits']['hits']
		for s in sampl_r:
    			li1 = str(s).split(",")[3].split(":")
			if(len(li1)<3):
				continue;
			dic = {}
			temp1 = li1[2].split("\'")[1];
			dic['headline'] = temp1;
			li2 =  "http:"+str(s).split(",")[4].split(":")[2][:-2]
			dic['url'] = li2;
			news.append(dic);
		
    else:
		for w in sorted(dict, key=dict.get, reverse=True):
		
			try:
				for word in article.keywords:
					articles = api.search( q = article.keywords[4], fq = {'headline':article.keywords[3], 'source':['Reuters','AP', 'The New York Times']},begin_date = 20111231 )
					for i in articles['response']['docs']:
						dic = {}
						dic['id'] = i['_id']
						dic['headline'] = i['headline']['main'].encode("utf8")
						dic['url'] = i['web_url']
						arr = {};
						arr["headline"] = dic['headline']
						arr["url"] = dic['url']
						idd = arr["headline"].replace(" ", "")
						if(dic not in news):
							es.index(index = 'recommend', doc_type = name, id = idd, body = arr);
							news.append(dic)	
						if(len(news)>=5):
							break;
					if(len(news)>=5):
						break;
				if(len(news)>=5):
					break;
			except(KeyError):
				print "key"
				continue;
			except(ValueError):
				print "value"
				continue;
			except(elasticsearch.SerializationError):
				continue;
			if(len(news)>=5):
				break;
    print news;	
    selected = request.form.get('dropdown');
    if(selected == None):
         selected = "technology";
    print selected;
    dict = {};
    dict['technology']="techcrunch";
    dict['business'] = "bloomberg";
    dict['entertainment'] = "buzzfeed";
    dict['gaming'] = "polygon";
    dict['general'] = "reuters";
    dict['music'] = "mtv-news";
    dict['science-and-nature'] = "national-geographic";
    dict['sport'] = "bbc-sport";
    r=requests.get("https://newsapi.org/v1/articles?source="+dict[selected]+"&apiKey="+apikey)

    resp=r.json()
    l=len(resp['articles'])
    d = [[] for i in repeat(None, l)]
    p=0
    for i in resp['articles']:
		d[p].append (i['title'])
		d[p].append (i['url'])
		d[p].append (i['urlToImage'])
		p=p+1
		arr={};
		arr['title']= i['title'];
		arr['url']=i['url']; arr['urlToImage']=i['urlToImage'];
		es.index(index = 'news', doc_type = selected, id = "".join(i['title'].split(' ')), body = arr)
    return render_template('index.html',
                           title='Home',
                           user=user,
                           tags=d, selected = selected, dat = news)

@app.route('/recommendation', methods=['POST'])
def recommendation():
    from_url = request.form.get('from_url')
    to_url = request.form.get('to_url')
    checked = request.form.getlist('channel')
    password = request.form.get('password')
    to_cell = request.form.get('to_cell')
    print from_url;
    print to_url;
    msg = MIMEMultipart()
    msg['From'] = from_url
    msg['To'] = to_url
    msg['Subject'] = "You would like to read this news"
    body = "Click on this link: "+checked[0]
    msg.attach(MIMEText(body, 'plain'))
	# Use sms gateway provided by mobile carrier:
	# at&t:     number@mms.att.net
	# t-mobile: number@tmomail.net
	# verizon:  number@vtext.com
	# sprint:   number@page.nextel.com
    try:
		if from_url!="" and to_url!="" and checked[0]!=None:
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login(from_url, password)
			text = msg.as_string()
			server.sendmail(from_url, to_url, text)
			server.quit()
		if from_url!="" and to_cell!="":
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login(from_url, password)
			text = msg.as_string()
			server.sendmail( from_url, to_cell+'@tmomail.net', text )
			server.quit()
    except:
		print "Authentication Error";
    
    user = g.user
    name = str(user).split('\'')[1];
    selected = request.form.get('dropdown')
    idd = str(checked).split('\'')[1]
    list = idd.split('/');
    i = list[2].split('.')[1]
    arr={}; arr["type"] = i;
    arr["url"]=idd;
    num = random.randint(0,1000);
    es.index(index = 'user', doc_type = name, id = num, body=arr)
    url_to_clean = checked[0]
    if not url_to_clean:
        return redirect(url_for('index'))

    article = Article(url_to_clean)
    article.download()
    article.parse()

    try:
      html_string = ElementTree.tostring(article.clean_top_node)
    except:
      html_string = "Error converting html to string."

    try:
      article.nlp()
    except:
      artstr="nlp not done"

    a = {
          
         'keywords': str(', '.join(article.keywords)),
         
         }
		# do something with checked array
    articles = api.search( q = article.keywords[1], fq = {'headline':article.keywords[1], 'source':['Reuters','AP', 'The New York Times']},begin_date = 20111231 )
    
    news = []
    for i in articles['response']['docs']:
		try:
			dic = {}
			dic['id'] = i['_id']
			if i['abstract'] is not None:
				dic['abstract'] = i['abstract'].encode("utf8")
			dic['headline'] = i['headline']['main'].encode("utf8")
			dic['desk'] = i['news_desk']
			dic['date'] = i['pub_date'][0:10] # cutting time of day.
			dic['section'] = i['section_name']
			if i['snippet'] is not None:
				dic['snippet'] = i['snippet'].encode("utf8")
			dic['source'] = i['source']
			dic['type'] = i['type_of_material']
			dic['url'] = i['web_url']
			dic['word_count'] = i['word_count']
			# locations
			locations = []
			for x in range(0,len(i['keywords'])):
				if 'glocations' in i['keywords'][x]['name']:
					locations.append(i['keywords'][x]['value'])
			dic['locations'] = locations
			# subject
			subjects = []
			for x in range(0,len(i['keywords'])):
				if 'subject' in i['keywords'][x]['name']:
					subjects.append(i['keywords'][x]['value'])
			dic['subjects'] = subjects   
			news.append(dic)
		except(ValueError):
			continue;
    return render_template('recommendation.html',tags = checked,dat=news)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == "__main__":
    h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
    resp, content = h.request("https://site/whose/certificate/is/bad/", "GET")	