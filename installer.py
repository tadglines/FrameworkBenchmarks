import subprocess
import os

class Installer:

  ############################################################
  # install_software
  ############################################################
  def install_software(self):
    if self.benchmarker.install == 'all' or self.benchmarker.install == 'server':
        self.__install_server_software()    

    if self.benchmarker.install == 'all' or self.benchmarker.install == 'client':
        self.__install_client_software()
  ############################################################
  # End install_software
  ############################################################

  ############################################################
  # __install_server_software
  ############################################################
  def __install_server_software(self):
    #######################################
    # Prerequisites
    #######################################
    self.__run_command("sudo apt-get update", True)
    self.__run_command("sudo apt-get upgrade", True)    
    self.__run_command("sudo apt-get install build-essential libpcre3 libpcre3-dev libpcrecpp0 libssl-dev zlib1g-dev python-software-properties unzip git-core libcurl4-openssl-dev libbz2-dev libmysqlclient-dev libreadline6-dev libyaml-dev libsqlite3-dev sqlite3 libxml2-dev libxslt-dev libgdbm-dev ncurses-dev automake libffi-dev htop libtool bison libevent-dev libgstreamer-plugins-base0.10-0 libgstreamer0.10-0 liborc-0.4-0 libwxbase2.8-0 libwxgtk2.8-0 libgnutls-dev libjson0-dev libmcrypt-dev libicu-dev cmake gettext", True)

    self.__run_command("cp ../config/benchmark_profile ../../.bash_profile")
    self.__run_command("sudo sh -c \"echo '*               soft    nofile          8192' >> /etc/security/limits.conf\"")

    #######################################
    # Languages
    #######################################

    #
    # Java
    #

    self.__run_command("sudo apt-get install openjdk-7-jdk", True)
    self.__run_command("sudo apt-get remove --purge openjdk-6-jre openjdk-6-jre-headless", True)

    #
    # go
    #
    
    self.__run_command("curl http://go.googlecode.com/files/go1.1rc3.linux-amd64.tar.gz | tar xvz")

    #######################################
    # Webservers
    #######################################

    #
    # Resin
    #

    self.__run_command("sudo cp -r /usr/lib/jvm/java-1.7.0-openjdk-amd64/include /usr/lib/jvm/java-1.7.0-openjdk-amd64/jre/bin/")
    self.__run_command("curl http://www.caucho.com/download/resin-4.0.34.tar.gz | tar xvz")
    self.__run_command("./configure --prefix=`pwd`", cwd="resin-4.0.34")
    self.__run_command("make", cwd="resin-4.0.34")
    self.__run_command("make install", cwd="resin-4.0.34")
    self.__run_command("mv conf/resin.properties conf/resin.properties.orig", cwd="resin-4.0.34")
    self.__run_command("cat ../config/resin.properties > resin-4.0.34/conf/resin.properties")

    ##############################################################
    #
    # Frameworks
    #
    ##############################################################

    ##############################################################
    #
    # System Tools
    #
    ##############################################################

    ##############################
    # Maven
    ##############################
    self.__run_command("sudo apt-get install maven2", send_yes=True)

    ##############################
    # Leiningen
    ##############################
    self.__run_command("mkdir -p bin")
    self.__run_command("wget https://raw.github.com/technomancy/leiningen/stable/bin/lein")
    self.__run_command("mv lein bin/lein")
    self.__run_command("chmod +x bin/lein")
  ############################################################
  # End __install_server_software
  ############################################################

  ############################################################
  # __install_client_software
  ############################################################
  def __install_client_software(self):
    subprocess.call(self.benchmarker.sftp_string(batch_file="config/client_sftp_batch"), shell=True)

    remote_script = """

    ##############################
    # Prerequisites
    ##############################
    yes | sudo apt-get update
    yes | sudo apt-get install build-essential git libev-dev libpq-dev libreadline6-dev postgresql
    sudo sh -c "echo '*               soft    nofile          8192' >> /etc/security/limits.conf"

    ##############################
    # MySQL
    ##############################
    sudo sh -c "echo mysql-server mysql-server/root_password_again select secret | debconf-set-selections"
    sudo sh -c "echo mysql-server mysql-server/root_password select secret | debconf-set-selections"

    yes | sudo apt-get install mysql-server

    # use the my.cnf file to overwrite /etc/mysql/my.cnf
    sudo mv /etc/mysql/my.cnf /etc/mysql/my.cnf.orig
    sudo mv my.cnf /etc/mysql/my.cnf
    sudo restart mysql

    # Insert data
    mysql -uroot -psecret < create.sql
    
    ##############################
    # Postgres
    ##############################
    sudo useradd benchmarkdbuser -p benchmarkdbpass
    sudo -u postgres psql template1 < create-postgres-database.sql
    sudo -u benchmarkdbuser psql hello_world < create-postgres.sql
    
    sudo mv postgresql.conf /etc/postgresql/9.1/main/postgresql.conf
    sudo mv pg_hba.conf /etc/postgresql/9.1/main/pg_hba.conf
    sudo -u postgres -H /etc/init.d/postgresql restart

    ##############################
    # Weighttp
    ##############################

    git clone git://git.lighttpd.net/weighttp
    cd weighttp
    ./waf configure
    ./waf build
    sudo ./waf install
    cd ~

    ##############################
    # wrk
    ##############################

    git clone https://github.com/wg/wrk.git
    cd wrk
    make
    sudo cp wrk /usr/local/bin
    cd ~
    """
    p = subprocess.Popen(self.benchmarker.ssh_string.split(" "), stdin=subprocess.PIPE)
    p.communicate(remote_script)

  ############################################################
  # End __parse_results
  ############################################################

  ############################################################
  # __run_command
  ############################################################
  def __run_command(self, command, send_yes=False, cwd=None):
    try:
      cwd = os.path.join(self.install_dir, cwd)
    except AttributeError:
      cwd = self.install_dir

    if send_yes:
      subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, cwd=cwd).communicate("yes")
    else:
      subprocess.call(command, shell=True, cwd=cwd)
  ############################################################
  # End __run_command
  ############################################################

  ############################################################
  # __init__(benchmarker)
  ############################################################
  def __init__(self, benchmarker):
    self.benchmarker = benchmarker
    self.install_dir = "installs"

    try:
      os.mkdir(self.install_dir)
    except OSError:
      pass
  ############################################################
  # End __init__
  ############################################################

