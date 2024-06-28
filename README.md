Implementation of a config file parser intended to parse a config file in a format similar to srvSettings.conf, where:
[group] denotes the start of a group of related config options, 
setting = value denotes a standard setting name and associated default value, and 
setting<override> = value2 denotes the value for the setting if the given override is enabled. 
If multiple enabled overrides are defined on a setting, the one defined last will have priority. Overrides can be passed either as strings or as symbols
The parsed files will be stored in a dictionary named CONFIG and can be accessed using dotted notation.
Code also includes the implementation of a custom cache and an alternative commented built-in LRU cache to access CONFIG dictionary values      

Sample outputs for accessing the dictionary object containing the parsed files contents:
>>> CONFIG.common.paid_users_size_limit
# returns 2147483648
>>> CONFIG.ftp.name
# returns "hello there, ftp uploading"
>>> CONFIG.http.params
# returns ["array", "of", "values"]
>>> CONFIG.ftp.lastname
# returns None
>>> CONFIG.ftp.enabled
# returns false (permitted bool values are "yes", "no", "true", "false", 1, 0)
>>> CONFIG.ftp['path'] 
# returns "/etc/var/uploads"
>>> CONFIG.ftp
# returns a dict: 
# {'name' => "hello there, ftp uploading", 
# 'path' => "/etc/var/uploads",
# 'enabled' => False}


