from flask import Flask, render_template, request,jsonify  #importing libraries 
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)


app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","") #taking input from site and storing into the variable 
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString #creating variable to store url
            uClient = uReq(flipkart_url) #creating variable and using urlopen as uReq to open link in browser
            flipkartPage = uClient.read() #reading data from page and storing it in a variable flipcart page
            uClient.close()  #closing the uClient
            flipkart_html = bs(flipkartPage, "html.parser") #creating a variable and storing it in a variable and using beautiful soap to beautify
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})  #opening big boxes for iterating through elements on html page
        
            del bigboxes[0:3] #deleting big box 
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] #creating a product link 
            prodRes = requests.get(productLink)  #accessing product through link 
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")    #passiiing html to bs for beutification 
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w") 
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            client = pymongo.MongoClient("mongodb+srv://manishkumawat0803:sansad70@cluster0.bmzomyg.mongodb.net/?retryWrites=true&w=majority")
            db = client['review_scrap']
            rewiew_col = db['review_scrap_data']
            review_col.insert_many(reviews)


            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
