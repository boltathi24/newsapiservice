import configparser

# Config = configparser.ConfigParser()
# Config._interpolation = configparser.ExtendedInterpolation()
#
# Config.read("configuration.ini")
# print(Config.get("newsApi","apiKey"))

if __name__ == "__main__":
    # Configuration.setFile("configuration.ini")
    Config = configparser.ConfigParser()
    Config._interpolation = configparser.ExtendedInterpolation()

    Config.read("configuration.ini")
    print(Config.get("newsApi", "apiKey"))