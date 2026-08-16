import pymysql

# Set version info so frameworks see it as MySQLdb
pymysql.version_info = (2, 2, 1, "final", 0)

# Make pymysql act like MySQLdb
pymysql.install_as_MySQLdb()