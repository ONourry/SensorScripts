import os
import subprocess


test = subprocess.Popen(["ping","-W","2","-c", "1", "192.168.1.70"], stdout=subprocess.PIPE)
output = test.communicate()[0]

def tmux_setup_env():
    java_home_path = "/usr/lib/jvm/java-1.8.0-openjdk.x86_64/"

    subprocess.call(["export","JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk.x86_64/"])
    subprocess.call(["export", "PATH=$JAVA_HOME/bin:$PATH"])

def generateRMExec():
    subprocess.call(["cd","/home/oliviern/MobileApps/RefactoringMiner"])
    subprocess.call(["git","clone","https://github.com/ONourry/RefactoringMiner.git"])
    subprocess.call(["cd","RefactoringMiner"])
    subprocess.call(["./gradlew","distZip","-Dorg.gradle.java.home=\"/usr/lib/jvm/java-1.8.0-openjdk.x86_64/\""])
    subprocess.call(["cd","build/distributions"])
    subprocess.call(["unzip","RefactoringMiner-1.0.zip"])
    subprocess.call(["cd","RefactoringMiner-1.0/bin"])


#./RefactoringMiner -a /home/oliviern/RefactoringProject/cloned_projects/jdt_core/eclipse.jdt.core master > jdt_core_output.json
def runRM(project_path,json_output_file):
    subprocess.Popen(["./RefactoringMiner","-a",project_path,"master",">",json_output_file])


def deleteRepoClone(project_path):
    subprocess.call(["rm","-rf",project_path])


def main():
    tmux_setup_env()
    generateRMExec()

if __name__ == "__main__":
    main()
#DEFAULT_JVM_OPTS="-Xms256m -Xmx16g"
#-Xms256m -Xmx16g

