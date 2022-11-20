# blocklist-toulouse1-netskope
Ingest blocklist from http://dsi.ut-capitole.fr/blacklists/ into Netskope tenant

usage: netskope-toulouse1.py [-h] -t TENANT -k APIKEY -a {test,prod} [-v]
options:
  -h, --help            show this help message and exit
  -t TENANT, --tenant TENANT
                        Tenant name. Without '.goskope.com' suffix. Required.
  -k APIKEY, --apikey APIKEY
                        APIv2 key. Required.
  -a {test,prod}, --action {test,prod}
                        Options to choose from
  -v, --verbose         Verbose output
