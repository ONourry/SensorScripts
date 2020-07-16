import os
import requests
import psycopg2
import subprocess


connection = None
cursor = None
try:
    connection = psycopg2.connect(user=os.environ.get('POSTGRES_REFACTORING_USER'),
                                  password=os.environ.get('POSTGRES_REFACTORING_PW'),
                                  host="127.0.0.1",
                                  port="5432",
                                  database="EnergyConsumption")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(), "\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception) as error:
    print("Error while connecting to PostgreSQL", error)


def downloadAPK(apkName,apkDir):
    url = "https://f-droid.org/repo/" + apkName
    req = requests.get(url,allow_redirects=True)

    savePath = os.path.join(apkDir,apkName)

    open(savePath, 'wb').write(req.content)


def updateConfigFile(configFile,apkName,apkDir,outputDir):
    """
    apkLocation = /apk/apkName.apk
    outputLocation = /outputDir/apkName
    powerProfileFile = /path/power_profile.xml
    runs = 2
    trials = 100
    interactions = 200
    timeBetweenInteractions = 100
    scriptLocationPath =
    scriptTime = 10
    """
    with open(configFile,"r+") as f:
        content = f.read()
        fields = content.split("\n")

        apkLocation = os.path.join(apkDir,apkName)
        outputDir = os.path.join(outputDir,apkName+"/")

        fields[0] = apkLocation
        fields[1] = outputDir
        updatedContent = '\n'.join(fields)

        f.seek(0)
        f.write(updatedContent)
        f.truncate()


def runPetra(petraJarDir):
    process = subprocess.Popen(['java','-jar','PETrA.jar','--batch','config.properties'],stdout=subprocess.PIPE,
                               cwd=petraJarDir)
    output = process.communicate()[0]


def main():
    # query = "SELECT apk_name from app_data where list_id is not null" #apps with >= 1 android manifests, >= 500 commits
    # cursor.execute(query)
    # apk_list = cursor.fetchall #[(apk,),(apk,)]

    apkDir = '/home/olivier/petra/apkdir/'
    outputDir = '/home/olivier/petra/outputdir/'
    powerProfileFile = '/home/olivier/petra/PETrA/power_profile.xml'
    configFile = '/home/olivier/petra/PETrA/config.properties'
    petraJarDir = '/home/olivier/petra/PETrA/'

    # for tuple in apk_list:
        # apkName = tuple[0]

        # downloadAPK(apkName,apkDir)

    for apk in apkDir:
        updateConfigFile(configFile,apk,apkDir,outputDir)

        #The emulator must be running before running Petra
        runPetra(petraJarDir)


    pass


if __name__ == "__main__":
    main()