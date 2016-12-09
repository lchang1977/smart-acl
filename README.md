# Smart-ACL
Network context aware RYU application that secures SDN for critical networks that require high availablity.


##Experimentation
For the creating of Smart-ACL we created various attack scenarios and meseaured the quality of critical services, with the aim to hold a minimum standard for such services.

Firslty experiementation start with viewing possible attack types and how they might be mitigated with the network abstractions provided by REF [?] and thus OpenFlow. This research led us to using metering, dropping and monitoring of flows. After the application was created, REF was finding approiate thresholds and finaly to verifiy that the application worked as expected at scale. The final experiement included a small business network with network and controller DoS attacks taking place, this was ran 100 times to ensure consitency in results.

##Quick start

Install python

`$ sudo apt-get install python`

Install pip

`$ sudo apt-get install python-pip`

Install ryu

`$ sudo pip install ryu`

Clone REF

`$ git clone https://github.com/lyndon160/REF.git`

Run REF controller (Choose test manifest)

`$ ryu-manager bandwidth_control.py`

Run Smart-ACL

`$ ./Smart-ACL.py`

##Results

Smart-ACL protecting against a network DoS.
TODO paste results

No Smart-ACL against network DoS.
TODO paste results

Smart-ACL protecting against controller DoS.
TODO paste results

No Smart-ACL against controller DoS.
TODO paste results

TODO add results from other experiments mitigating other attacks.
