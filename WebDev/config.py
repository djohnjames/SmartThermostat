# Flask Configuration

# SECRET_KEY - assuming this could be used with the .wsgi file?

class Config:
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

class ProdConfig(Config):
    DEBUG = False
    TESTING = False



class DevConfig(Config):
    DEBUG = True
    TESTING = True

    # Datebase
    MYSQL_HOST = '10.0.0.69'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'pmwpmwpmw'
    MYSQL_DB = 'tempLog'
    MYSQL_PORT = 3306
    # MYSQL_CURSORCLASS = ''

    # MQTT
    MQTT_BROKER_URL = '127.0.0.1'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = ''
    MQTT_PASSWORD = ''
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False