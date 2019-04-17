Example 06: Remote querying with a server-client structure
==========================================================
It might happen that in your specific application of PhenoAI you need to start the
package and load an AInalysis for the prediction of a single data point. If this
happens once that might be fine, but if you need to do this multiple times, the
loading time might become extremely unwanted. For this, you can run PhenoAI in a
server-client set-up, in which a continuous proces (server) has all the AInalyses
in memory and another process (client, not necesarily on the same machine) queries
the datapoints to it.

This example consists out of two scripts:

- a **server** script, to be run on the machine that performs the prediction (i.e. the server);
- a **client** script, to be run on the machine that has to query the server for a prediction (i.e. the client). The client might be the same machine as the server.

Run the server script and let it continue to run (don't stop execution). While it
runs, run the client script.

.. attention:: In order for this example to work, you need to run :download:`the initialisation script <../_static/examples/ex00_RUN_THIS_FIRST.py>` in the folder you will store the example scripts first.

:download:`Download the server script <../_static/examples/ex06a_remote_server.py>`

:download:`Download the client script <../_static/examples/ex06b_remote_client.py>`

The server script
-----------------
.. literalinclude:: ../_static/examples/ex06a_remote_server.py

The client script
-----------------
.. literalinclude:: ../_static/examples/ex06b_remote_client.py


:download:`Download the server script <../_static/examples/ex06a_remote_server.py>`

:download:`Download the client script <../_static/examples/ex06b_remote_client.py>`