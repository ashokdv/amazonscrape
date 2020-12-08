from bs4 import BeautifulSoup # BeautifulSoup is in bs4 package 
import requests
from flask import Flask,request ,jsonify
import uuid ,json
from pyshorteners import Shortener 
  


app = Flask(__name__)   
@app.route('/') 
def home():
    return "<h1>Welcome to our server !!</h1>"
#    return render_template("home.html")


@app.route('/users',methods=['POST'])
def users():
      


    usercontent = request.get_json()
    if usercontent is None:
        name = request.form['name']
        URL = request.form['URL']
        mobilenumber = request.form['mobilenumber']
        yourprice = request.form['yourprice']
    else:
        name = usercontent['name']
        URL = usercontent['URL']
        mobilenumber = usercontent['mobilenumber']
        yourprice = usercontent['yourprice']
    uuid_user = uuid.uuid1()
    product_details = json.loads(sampletrigger(URL))

    linkRequest = {"destination": URL, "domain": { "fullName": "rebrand.ly" }}
    requestHeaders = {"Content-type": "application/json","apikey": "5c0a9490877942ecb3538236c7ec3ee6"}

    try:
        r = requests.post("https://api.rebrandly.com/v1/links", data = json.dumps(linkRequest),headers=requestHeaders)
        if (r.status_code == requests.codes.ok):
            link = r.json()
            short_url = link["shortUrl"]
    except Exception as e:
        print(e)
    
    

    def write_json(data, filename='users.json'): 
        with open(filename,'w') as f: 
            json.dump(data, f, indent=4) 
    
    with open('users.json') as json_file: 
        data = json.load(json_file) 
        temp = data['users'] 
  
        # python object to be appended 
        y = {
            "name" : name,
            "title" : product_details['title'],
            "URL" : URL,
            "mobilenumber" : mobilenumber,
            "yourprice" : yourprice,
            "UUID": str(uuid_user),
            "subscribe": "Y",
            "actual_price":product_details['ourprice'],
            "deal_price":product_details['dealprice'],
            "sale_price":product_details['saleprice'],
            "stock":product_details['stock'],
            "short_url":short_url

            } 
        temp.append(y) 
        
    write_json(data)
    # print ("SHORT URL is {}".format(url_shortener.short(url))) 

    message = "Hi "+ name + " , You have subscribed to a Product  "+ product_details['title'] + " .Thanks for your subscription. Your product id is "+str(uuid_user)
    sms = sms_trigger(message,mobilenumber)
    return "Thanks for the subscription"
    # return render_template("subscribe.html")


        

def sampletrigger(URL):
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    URL = URL
    content = requests.get(URL , headers= HEADERS)
    soup = BeautifulSoup(content.text, 'lxml')
    try:
        title = soup.find(id='productTitle').get_text().strip()
    except Exception as e:
        title = 'Not found'
    # print(title)
   
    if len(title) > 100:
        title = title[0:70]

    try:
        try:
            ourprice = float(soup.find(id='priceblock_ourprice').get_text().replace('₹','').replace(',','').strip())
            print(ourprice)
        except Exception as e :
            print(e)
            ourprice = 0

        try:
            dealprice = float(soup.find(id='priceblock_dealprice').get_text().replace('₹','').replace(',','').strip())
            print(dealprice)
        except Exception as e:
            print(e)
            dealprice = 0

        try:
            saleprice = float(soup.find(id='priceblock_saleprice').get_text().replace('₹','').replace(',','').strip())
            print(saleprice)
        except Exception as e:
            print(e)
            saleprice = 0
                
        if ourprice == 0 and dealprice == 0 and saleprice ==0 :
            msg = 'Unable to load product'
        
                    
    except Exception as e:
        print(e)


    try:
        soup.select('#availability .a-color-state')[0].get_text().strip()
        print(soup.select('#availability .a-color-state')[0].get_text().strip())
        stock = 'Out of Stock'
    except:
        stock = 'Available'

    # print(stock)
    return json.dumps({'ourprice':ourprice,"dealprice":dealprice,"saleprice":saleprice,'title':title,'stock':stock})

def sms_trigger(message,number):
    print('----------------',message)
    print('---------------',number)
    url = "https://www.fast2sms.com/dev/bulk"


    # create a dictionary
    my_data = {
    	'sender_id': 'FSTSMS',
    	'message': message,
    	'language': 'unicode',
    	'route': 'p',
    	'numbers': number
    }

    # create a dictionary
    headers = {
    	'authorization': 'bh4NsVrzJa9vQjZFHWlx36PoOqefnGBw7pmTdY8t1uIK0XCS5DUrQCk9N1hxmMtyKAwoa540VZfzWOnX',
    	'Content-Type': "application/x-www-form-urlencoded",
    	'Cache-Control': "no-cache"
    }

    response = requests.request("POST",
                                url,
                                data = my_data,
                                headers = headers)
    # load json data from source
    returned_msg = json.loads(response.text)

    # print the send message
    print(returned_msg['message'])
    return returned_msg['message']


    
@app.route('/alert-sms',methods=['POST'])
def alerts():
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    with open('users.json') as f:
        data = json.load(f)


    # print(data['users'][1])
    for users in data['users']:
        # print(users)

        # for product_details in users:
        print(users['URL'])
        print(users['yourprice'])
        content = requests.get(users['URL'] , headers= HEADERS)
        soup = BeautifulSoup(content.text, 'lxml')

        try:
            try:
                ourprice = float(soup.find(id='priceblock_ourprice').get_text().replace('₹','').replace(",",'').strip())
            except:
                ourprice = 0    
            try:
                dealprice = float(soup.find(id='priceblock_dealprice').get_text().replace('₹','').replace(",",'').strip())
            except:
                dealprice = 0
            try:
                saleprice = float(soup.find(id='priceblock_saleprice').get_text().replace('₹','').replace(",",'').strip())
            except:
                saleprice = 0

            print('--------ourprice-------',ourprice)
            print('--------dealprice-------',dealprice)
            print('--------saleprice-------',type(saleprice))

            print('-----------Oldourprice----',users['actual_price'])
            print('--------olddealprice-------',users['deal_price'])
            print('--------oldsaleprice-------',users['sale_price'])


            if ourprice == 0 and dealprice == 0 and saleprice==0:
                msg = 'Unable to load product'
            
        except Exception as e:
            print(e)

        message = "Hi "+ users['name'] + " , Your subscription Product  "+ users['title'] + " is available at lower price,  "


        try:
            soup.select('#availability .a-color-state')[0].get_text().strip()
            stock = 'Out of Stock'
        except:
            stock = 'Available On Stock'
      
        if dealprice > 0 and ( dealprice < users['deal_price'] or dealprice < users['sale_price'] or dealprice < users['actual_price']) :
            message = message + 'Price : '+str(dealprice) + ". Product is "+stock +".Deal is Available on this  Product"+ "link:" + users['short_url']
            sms = sms_trigger(message,users['mobilenumber'])


        elif saleprice > 0 and ( saleprice < users['deal_price'] or saleprice < users['sale_price'] or saleprice < users['actual_price']):
            message = message + 'Price : '+str(saleprice) + ". Product is "+stock +". Sale is going on." + "link:" + users['short_url']
            sms = sms_trigger(message,users['mobilenumber'])

        elif ourprice > 0 and ( ourprice < users['deal_price'] or ourprice < users['sale_price'] or ourprice < users['actual_price']):
            message = message + 'Price : '+str(ourprice) + ". Product is "+stock +". No Deal Available and Not on sale.  " + "link:" + users['short_url']
            sms = sms_trigger(message,users['mobilenumber'])

        else :
            pass
       
    return "Sms triggered"



if __name__ == '__main__': 
    app.run(threaded=True)
