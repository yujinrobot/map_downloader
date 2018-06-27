# log_aggregator #

* This tool allow to easily aggloremate logging files for support purpose.
* log\_aggregator can send log files to nuc server or create a tarball of log files on local filesystem.
* log\_aggregator can be configured thanks to ~/.log\_to\_nucrc file created automatically if it does not exist.
### Install ###
~~~~
(sudo) pip install log_aggregator
~~~~
### Configure ###
Simply add the path of the files/directories you want to add to the tarball to ~/.log\_to_nucrc configuration file.
 	
~~~~
/path/to/somefile1

~/relative/path/to/somefile2

~/relative/path/to/somedirectory
~~~~

### Usage ###
~~~~
  -h, --help      show this help message and exit
  --show_conf     Show the actual configuration file in use if it exists
  --default_conf  WARNING: Delete your actual conf if it exists and generate
                  the default configuration file
  --local         Create a local tarball under home directory
  --gui           A simple gui to help users
~~~~

### TODO ###
* Write tests
* Release on pip
