FAQ
===

**Using PhenoAI**

- `I try to get the server-client structure to work, but i cant connect let them connect.`_

**Contribute**

- `How can i contribute to PhenoAI?`_

**Other**

- `How do i cite/reference PhenoAI?`_
- `How can i contact you?`_

---------

Using PhenoAI
-------------

I try to get the server-client structure to work, but i cant connect let them connect.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Although it is difficult to give a precise explanation for this problem without knowing the details, most of the time this is caused by the configuration of the firewall. The server-client communication takes place over HTTP channels and although these should not be blocked by default, some sysadmins like to be better-safe-than-sorry.
In order to test if this is indeed the issue, try to run the server and client on the same machine and link them together not by IP address, but by the location identifier localhost (as is done in the example scripts).
If the problem persists, check if you have provided the correct IP address and port. Note that the port and ip of the server should be known to both the server and the client (and that these should match).
AInalyses

---------

Contribute
----------

How can i contribute to PhenoAI?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We are always happy if people want to contribute to the PhenoAI project! The easiest way to contribute is to create AInalyses and make them available for distribution through the AInalysis library. You can do this by contact us.
If you want to go a step further and have a great idea that should absolutely be implemented in PhenoAI, you can always contact us.
Other

---------

Other
-----

How do i cite/reference PhenoAI?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
At the moment we are busy writing the PhenoAI paper, so as soon as it is ready we will provide you with the full reference to that paper. For now, you can reference the software package itself.

How can i contact you?
^^^^^^^^^^^^^^^^^^^^^^
You can contact us on b.stienen@science.ru.nl.