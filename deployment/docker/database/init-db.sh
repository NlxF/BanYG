# TODO: remove this line after we fully support mysql 5.7
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL sql_mode = '';"

# TODO: remove this line after we squash our DB updates
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL max_allowed_packet=128*1024*1024;"

echo "Creating DB..."
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS BanYG DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"

mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL innodb_lru_scan_depth=256;"

echo "Set up only local connections..."
echo $(mysql -u root -p$MYSQL_ROOT_PASSWORD -e "DELETE FROM mysql.user where host='%';")
echo $(mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON *.* to root @'172.16.238.%' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';")
echo $(mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGESaa ON *.* to root @'192.168.%.%' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';")
echo $(mysql -u root -p$MYSQL_ROOT_PASSWORD -e "FLUSH PRIVILEGES;")

echo "Done!"
