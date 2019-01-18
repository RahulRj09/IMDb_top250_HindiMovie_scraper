import requests
from bs4 import BeautifulSoup as bs
import html5lib
from pprint import pprint 
import json
import pathlib
import os
from random import randint
from time import sleep


IMDB_URL = "https://www.imdb.com/india/top-rated-indian-movies/"
imdb_data = requests.get(IMDB_URL).text
imdb_data = bs(imdb_data,'html5lib')

def folderr():
	folder ="moviefile"
	folderpath = pathlib.Path(folder)
	if folderpath.exists():
		folder +="/"
		return folder
	else:
		os.mkdir(folder)
		folder +="/" 
		return folder

def castfolderr():
	castfolder ="castfolder"
	folderpath = pathlib.Path(castfolder)
	if folderpath.exists():
		castfolder +="/"
		return castfolder
	else:
		os.mkdir(castfolder)
		castfolder +="/" 
		return castfolder

#function 1
def scrape_top_list(imdb_data):
	allmovie_list = []
	tbody = imdb_data.find('tbody',{'class': 'lister-list'})
	i = 1
	for tr in tbody.find_all('tr'):
		movie_url = "https://www.imdb.com"
		all_movie_list = {}
		movieNameYear = tr.find('td', {'class': 'titleColumn'})
		all_movie_list['name'] = movieNameYear.find('a').text
		year = movieNameYear.find('span',{'class': 'secondaryInfo'}).text
		year = year.replace("(","")
		year = year.replace(")","")
		year = int(year)
		all_movie_list["year"] = year
		rating = tr.find('td',{'class': 'ratingColumn imdbRating'}).strong.text
		rating = float(rating)
		all_movie_list["rating"] = rating
		all_movie_list["position"] = i
		url = tr.find('a')
		url = url.get('href')
		for j in range(len(url)):
			if url[j] == '?':
				break
			else:
				movie_url += url[j]
		all_movie_list["url"] = movie_url
		i +=1
		allmovie_list.append(all_movie_list)
	return allmovie_list

#function 2
def group_by_year(all_movie):
	group_by_year_movie_list = {}
	for movie in range(len(all_movie)):
		if all_movie[movie]['year'] in group_by_year_movie_list:
			group_by_year_movie_list[all_movie[movie]["year"]].append(all_movie[movie])
		else:
			group_by_year_movie_list[all_movie[movie]["year"]] = [all_movie[movie]]
	return group_by_year_movie_list

# function 3 task 3
def group_by_decade(all_movie):
	movies_by_decade = {}

	for movies_by_de in range(len(all_movie)):
		year = all_movie[movies_by_de]['year'] % 10
		year_decade = all_movie[movies_by_de]['year'] - year
		if year_decade in movies_by_decade:
			movies_by_decade[year_decade].append(all_movie[movies_by_de])
		else:
			movies_by_decade[year_decade] = [all_movie[movies_by_de]]
	return movies_by_decade

# function 4 task 4
def scrape_movie_details(url):
	movie_details = {}
	folder = folderr()
	jsonurl = url
	jsonurl = jsonurl.split('/')
	jsonfilename = jsonurl[-2]
	jsonfilename +='.json'
	filepath = pathlib.Path(folder+jsonfilename)
	if filepath.exists():
		exercisesdata = open(folder+jsonfilename,"r")
		exercisesdata = exercisesdata.read()
		movie_details = json.loads(exercisesdata)
		caste=scrape_movie_cast(url)
		movie_details['caste'] = caste
		return movie_details
	else:
		movie_details_data = requests.get(url).text
		movie_details_data = bs(movie_details_data,'html5lib')
		title_bar_wrapper = movie_details_data.find('div',{'class': 'title_bar_wrapper'})
		movie_name = title_bar_wrapper.find('h1').text
		movie_name = movie_name.split()
		movie_name.pop()
		movie_name = ' '.join(movie_name)
		bio = movie_details_data.find('div',{'class': 'summary_text'}).text
		bio = bio.strip()
		poster = movie_details_data.find('div',{'class': 'poster'})
		poster = poster.find('img')
		poster = poster.get('src')
		subtext = movie_details_data.find('div',{'class': 'subtext'}).text
		subtext = subtext.strip()
		subtext = subtext.split()
		if subtext[0][0].isnumeric():
			time = subtext[0:2]
		elif len(subtext[0]) == 3:
			subtext = subtext[3:]
			time = subtext[0:2]
		else:
			subtext = subtext[2:-5]
			time = subtext[0:2]
		time1 = int(time[0][0])
		runtime = time1*60
		if len(time[1]) == 5:
			runtime +=int((time[1][0])+(time[1][1]))
		elif len(time[1]) == 4:
			runtime +=int(time[1][0])
		else:
			pass	
		genr = subtext[3:]
		genres = []
		for i in range(len(genr)):
			if genr[i] == '|':
				break
			else:
				genres.append(genr[i])
		genre = ([genre.strip(',') for genre in genres])
		plot_summaryDirector = movie_details_data.find('div',{'class': 'plot_summary'})
		Director = []
		for director in plot_summaryDirector.find_all('div',{'class': 'credit_summary_item'}):
			director = director.text
			director=director.strip()
			# director = director.split()
			# print(director)
			if "Director:" in director:
				director = director[10:]
				director = director.split(',')
				Director = director
			elif "Directors:" in director:
				director = director[11:]
				director = director.split(',')
				Director = director
		txtblock = movie_details_data.find('div',{'id': 'titleDetails'}) 
		for i in txtblock.find_all('div',{'class': 'txt-block'}):
			i = i.text
			i=i.strip()
			if "Country:" in i:
				country = i.split()
				country = country[1]
			elif "Language:" in i:
				language = i.split()
				language = language[1:]
				s = ([s.strip('|') for s in language])
				language =([x for x in s if x])
		movie_details['name'] = movie_name
		movie_details['director'] = Director
		movie_details['country'] = country
		movie_details['language'] = language
		movie_details['poster_image_url'] = poster
		movie_details['bio'] = bio
		movie_details['runtime'] = runtime
		movie_details['genre'] = genre
		with open(folder+jsonfilename, "w") as f:
			f.write(json.dumps(movie_details))
		caste=scrape_movie_cast(url)
		movie_details['caste'] = caste
		return movie_details


# function 5 task 5
def get_movie_list_details(all_movie):
	movies_detail_list = []
	for i in range(len(all_movie)):
	#for i in range(10):
		#sleep(randint(1,3))
		url = all_movie[i]['url']
		#function 4
		movie_details =scrape_movie_details(url)
		pprint(movie_details)
		movies_detail_list.append(movie_details)
	return movies_detail_list

# function 6 task 6
def analyse_movies_language(movies_detail_list):
	languages = {}
	for language in range(len(movies_detail_list)):
		for lang in range(len(movies_detail_list[language]['language'])):
			if movies_detail_list[language]['language'][lang] in languages:
				languages[movies_detail_list[language]['language'][lang]] +=1 
			else:
				languages[movies_detail_list[language]['language'][lang]] = 1
	return languages

# function 7 task 7
def analyse_movies_directors(movies_detail_list):
	directors = {}
	for director in range(len(movies_detail_list)):
		for direct in range(len(movies_detail_list[director]['director'])):
			if movies_detail_list[director]['director'][direct] in directors:
				directors[movies_detail_list[director]['director'][direct]] +=1 
			else:
				directors[movies_detail_list[director]['director'][direct]] = 1
	return directors


# function 8 task 10
def analyse_language_and_directors(movies_detail_list):
	directorLanguageMovie = {}
	for director in range(len(movies_detail_list)):
		for direct in range(len(movies_detail_list[director]['director'])):
			if movies_detail_list[director]['director'][direct] in directorLanguageMovie:
				for lang in range(len(movies_detail_list[director]['language'])):
					if movies_detail_list[director]['language'][lang] in directorLanguageMovie[movies_detail_list[director]['director'][direct]]:
						directorLanguageMovie[movies_detail_list[director]['director'][direct]][movies_detail_list[director]['language'][lang]] +=1
					else:
						directorLanguageMovie[movies_detail_list[director]['director'][direct]][movies_detail_list[director]['language'][lang]] =1
			else:
				directorLanguageMovie[movies_detail_list[director]['director'][direct]] = {}
				for lang in range(len(movies_detail_list[director]['language'])):
					directorLanguageMovie[movies_detail_list[director]['director'][direct]][movies_detail_list[director]['language'][lang]] = 1
	return directorLanguageMovie

# function 9 task 11
def analyse_movies_genre(movies_detail_list):
	genres = {}
	for genre in range(len(movies_detail_list)):
		for g in range(len(movies_detail_list[genre]['genre'])):
			if movies_detail_list[genre]['genre'][g] in genres:
				genres[movies_detail_list[genre]['genre'][g]] +=1 
			else:
				genres[movies_detail_list[genre]['genre'][g]] = 1
	return genres

# function 10 task 12
def scrape_movie_cast(url):
	castfolder = castfolderr()
	movie_caste = []
	cfile = url
	cfile= cfile.split('/')
	cfile = cfile[-2] + '_cast.json'
	filepath = pathlib.Path(castfolder+cfile)
	if filepath.exists():
		castedata = open(castfolder+cfile,"r")
		castedata = castedata.read()
		castedata = json.loads(castedata)
		return castedata
	else:
		movie_caste_url = url+'fullcredits?ref_=tt_cl_sm#cast'
		movie_caste_detail = requests.get(url).text
		movie_caste_detail = bs(movie_caste_detail,'html5lib')
		caste_table = movie_caste_detail.find('table', {'class': 'cast_list'})
		caste_tbody = caste_table.find('tbody')
		for caste_td in caste_tbody.find_all('td' , {'class': ''}):
			caste = {}
			caste_a = caste_td.find('a')
			caste_href = caste_a.get('href')
			caste_href = caste_href.split('/')
			caste['imdb_id'] = caste_href[2]
			caste_name = caste_a.text
			caste['name'] = caste_name[:-1]
			movie_caste.append(caste)
		with open(castfolder+cfile, "w") as f:
				f.write(json.dumps(movie_caste))
		return movie_caste
#function 1
all_movie = scrape_top_list(imdb_data)

#function 2
groupByYear=group_by_year(all_movie)

#function 3
movies_by_decade = group_by_decade(all_movie)

#function 5
movies_detail_list =get_movie_list_details(all_movie)

# function 6 
languages = analyse_movies_language(movies_detail_list)

# function 7
directors=analyse_movies_directors(movies_detail_list)

# function 8
directorLanguageMovie=analyse_language_and_directors(movies_detail_list)

# function 9
genres = analyse_movies_genre(movies_detail_list)


# movie_caste_url = "https://www.imdb.com/title/tt0066763/"
# scrape_movie_cast(movie_caste_url)