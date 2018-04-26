from flask import Flask, render_template, request, make_response
import feedparser
import json
import urllib.request
import urllib.parse
import api_key as ak
import datetime

# init the app
app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'channel':'bbc',
            'city': 'London,UK',
            'cur_frm':'GBP',
            'cur_to':'USD'}

#********************************************************
# VIEWS USING STATIC URL'S
# define the routes
# @app.route('/bbc')
# def bbc():
# 	return get_news(RSS_FEEDS['bbc'])

# @app.route('/cnn')
# def cnn():
# 	return get_news(RSS_FEEDS['cnn'])

# @app.route('/fox')
# def fox():
# 	return get_news(FOX_FEED_URL)

# @app.route('/iol')
# def iol():
# 	return get_news(IOL_FEED_URL)
#**************************************************************

#**************************************************************
# VIEWS USING DYNAMIC URL'S
# @app.route('/')
# @app.route('/<channel>') # using dynamic routing here
# def get_news(channel='bbc'):
# 	feed = feedparser.parse(RSS_FEEDS[channel])
	
	# top_article = feed['entries'][0]

	# return '''
	# 		<html>
	# 		<body>
	# 		<h1>HEADLINES </h1>
	# 		<b>{title}</b>
	# 		<i>{published}</i>
	# 		<p>{desc}</p>
	# 		</body>
	# 		</html>
	# 		'''.format(title=top_article.get('title'),
	# 					published=top_article.get('published'),
	# 					desc=top_article.get('summary'))

	# passing the context to the template
	# return render_template('home.html',
	# 					title=top_article.get('title'),
	# 					published=top_article.get('published'),
	# 					desc=top_article.get('summary'))

	# now handle article via top_article object
	# now we are passing all the news in the rss feeds
	# return render_template('home.html', articles=feed['entries'])
#**********************************************************************

# using GET to request data rather than dynamic urls
@app.route('/')
def home():
	'''
	Route for home page
	# first get the currency data from form
	# if there is no args in get request get data from cookie
	# if the cookie is not set then get the default values
	'''
	# get the news data
	channel = request.args.get('channel')
	if not channel:
		channel = request.cookies.get('channel')
		if not channel:
			channel = DEFAULTS['channel']
	articles = get_news(channel)

	# get the city data
	city = request.args.get('city')
	if not city:
		city = request.cookies.get('city')
		if not city:
			city = DEFAULTS['city']
	weather = get_weather(city)

	# get the currency data
	cur_frm = request.args.get('cur_frm')
	if not cur_frm:
		cur_frm = request.cookies.get('cur_frm')
		if not cur_frm:
			cur_frm = DEFAULTS['cur_frm']

	cur_to = request.args.get('cur_to')
	if not cur_to:
		cur_to = request.cookies.get('cur_to')
		if not cur_to:
			cur_to = DEFAULTS['cur_to']

	rate, currencies = get_conv_rate(cur_frm, cur_to)

	response = make_response(render_template('home.html', articles=articles, weather=weather, cur_frm=cur_frm, cur_to=cur_to, rate=rate, currencies=sorted(currencies)))
	expires = datetime.datetime.now() + datetime.timedelta(days=365)
	response.set_cookie('channel', channel, expires=expires)
	response.set_cookie('city', city, expires=expires)
	response.set_cookie('cur_frm', cur_frm, expires=expires)
	response.set_cookie('cur_to', cur_to, expires=expires)
	return response


def get_news(channel):
	'''
	Get the news data based on channel
	'''
	if not channel or channel.lower() not in RSS_FEEDS:
		channel = DEFAULTS['channel']
	else:
		channel = channel.lower()

	feed = feedparser.parse(RSS_FEEDS[channel])

	return feed['entries']

def get_weather(query):
	'''
	Get the current weather data from using openweather API
	'''
	api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid='+ak.OPENWEATHER_KEY
	query = urllib.parse.quote(query)
	url = api_url.format(query)
	data_ = urllib.request.urlopen(url)
	data = data_.read() # getting the call in bytes
	encoding = data_.info().get_content_charset('utf-8') # getting the charset
	parsed = json.loads(data.decode(encoding)) # decode the charset to str
	weather = None
	if parsed.get("weather"):
		weather = {'description': parsed['weather'][0]['description'],
		'temperature':parsed['main']['temp'],
		'city':parsed['name'],
		'country': parsed['sys']['country']}
	return weather

def get_conv_rate(frm, to):
	'''
	Get the current currency data from using openweather API

	returns the conversion rate and all the currrency keys in the API
	'''
	api_url = 'https://openexchangerates.org//api/latest.json?app_id='+ak.OPENCURRENCY_KEY
	data_ = urllib.request.urlopen(api_url)
	data = data_.read() # getting the call in bytes
	encoding = data_.info().get_content_charset('utf-8') # getting the charset
	parsed = json.loads(data.decode(encoding)).get('rates') # decode the charset to str
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())

	return (to_rate/frm_rate, parsed.keys())

# run the app
if __name__ == '__main__':
	app.run(port=5000, debug=True)