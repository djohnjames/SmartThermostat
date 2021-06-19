from flask import Flask, render_template, jsonify, request #, url_for, request, redirect
from flask_mysqldb import MySQL #FOR SOMEREASON THIS CAN'T WORK IN A FUNCTION WITH A MQTT DECORATOR
import mysql.connector
from flask_mqtt import Mqtt

from datetime import datetime


app = Flask(__name__)
app.config.from_object('config.DevConfig')
# mysqlDb = MySQL(app)
mqtt = Mqtt(app)


# TO DO
#  1. Integrate mqtt controller with flask
#     Organize based on this guide: https://exploreflask.com/en/latest/organizing.html
#  2. Add scheduler functionality Aidan made (should be stored in database not a dict)
#  3. Add set temperature functionality to webpage
#  4. Apply css and bootstrap formating
#  5. Graphs of temperature over time with outside weather data
#  6. Should have users for API/database login

# Get socket working for test
# then try and see if it works on apache to trrouble shoot
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/currentStatus', methods=['GET'])
def currentStatus():
    # Connecting to db and getting most recent record
    sql = "SELECT * FROM `thermData` ORDER BY `thermData`.`Date` DESC, `thermData`.`Time` DESC LIMIT 1"

    myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
    cursor = myDb.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    # Formatting some of the data for return
    if result[0][4] == 1:
        furnaceStatus = "ON"
    else:
        furnaceStatus = "OFF"
    date = result[0][0].strftime("%b %-d, %Y")
    time = str(result[0][1])
    
    # The data to be returned as a JSON object
    statusSet = {"setTemp" : result[0][3], "upstairsTemp" : result[0][2], "downstairsTemp" : "coming soon!", "furnaceStatus" : furnaceStatus, "date" : date, "time": time}
    return jsonify(statusSet)

@app.route('/api/setTemp', methods=['POST'])
def setTemp():
    #default user is root, but in future will be diferent (ie Guest, djohnjames, etc.)
    userID = app.config['MYSQL_USER']
    # Get new temperature from form that was sent
    newTemp = request.form["newSetTemp"]

    #Next need to send out this temp on a retained mqtt, then write the record into the database for later viewing
    mqtt.publish('therm/TEMPSET', str(newTemp), qos=0, retain=True)
    # The sql and params
    sql = "INSERT INTO setTempLog (Date, Time, UserId, setTemp) VALUES (%s, %s, %s, %s)"
    val = (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), userID, newTemp)

    # Connecting to db and inserting new data
    # myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
    # cursor = myDb.cursor()
    # cursor.execute(sql, val)
    # myDb.commit()
    # cursor.close()
    
    # cur=mysqlDb.connection.cursor()
    # cur.execute(sql, val)
    # mysqlDb.connection.commit()
    # cur.close()
    return 'Success!'

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    mqtt.subscribe("therm/DATA")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    message.payload = message.payload.decode("utf-8")
    # print("Received message '" + str(message.payload) + "' on topic '"
    #     + message.topic + "' with QoS " + str(message.qos))
    if message.topic == "therm/DATA":
        # The sql and params
        sql = "INSERT INTO thermData (Date, Time, currentTemp, setTemp, heating, battery) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), message.payload.split("/")[0], message.payload.split("/")[1], message.payload.split("/")[2], message.payload.split("/")[3])
        print("Inserting: " + message.payload.split("/")[0] + "/" + message.payload.split("/")[1] + "/" + message.payload.split("/")[2] + "/" + message.payload.split("/")[3])

        # Connecting to db and inserting new data
        myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
        cursor = myDb.cursor()
        cursor.execute(sql, val)
        myDb.commit()
        cursor.close()



if __name__ == "__main__":
    app.run(port=6969, host='0.0.0.0') #0.0.0.0 makes it available to all devices on the network

