from flask import Flask, render_template, request
import feedparser

# init the app
app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

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
def get_news():
	query = request.args.get('channel')
	if not query or query.lower() not in RSS_FEEDS:
		channel = 'bbc'
	else:
		channel = query.lower()

	feed = feedparser.parse(RSS_FEEDS[channel])
	return render_template('home.html', articles=feed['entries'])


# run the app
if __name__ == '__main__':
	app.run(port=5000, debug=True)