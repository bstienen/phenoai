Tutorial: Server-client structure
=================================

PhenoAI is incredibly powerful in its automation. It can make predictions on basically anything as long as an AInalysis is available. These predictions are made in a fraction of a second, opening up the possibility to do e.g. exploratory searches in parameter spaces. If you would like to do something like this, you may have the need to incorporate PhenoAI in your analysis workflow or an existing pipeline. Although it is possible to do this by including the PhenoAI package and initialising an AInalysis from there, this can take up time that you would like to use for something else.

Enter: the server-client structure. PhenoAI has a built-in server-client structure, allowing you to initialise a single PhenoAI instance with a loaded AInalysis (or multiple AInalyses, if you need it) and query this single instance via a light-weight client script. The client then returns the results as if it were the full-fledged PhenoAI instance.

This tutorial gives in-depth explanations on what to do, how to do it and why you need to do it in the first place. If you need a quick-fix for your problems and don't want to read this entire webpage, you are reffered to example scripts 06a and 06b, which implement the intialisation of the server and the usage of the client directly.

Step 1: Setting up the server
-----------------------------
To set up the server, you need to set three values: the IP-address of the server, the PORT over which clients will communicate with the server and the LOGPATH to which the server will output all log information. Your code could therefore look something like this:::

    IP = "localhost"
    PORT = 31415
    LOGPATH = "phenoai_server.log"

Having defined these variables, you initialise a PhenoAI instance with an AInalysis as you would normally:::

    from phenoai.core.PhenoAI import PhenoAI
    master = PhenoAI(dynamic=False)
    master.add("./example_ainalysis", "example")

At this moment you have a PhenoAI instance that is fully configured. You could use the `.run(...)` method to query it for a prediction within the current code, but this will not make it a server. To make it a server, you need just one single command:::

    master.run_as_server(IP, PORT, logging_path=LOGPATH)

This command will immediately make the PhenoAI instance behave as a server, with as result that it will start and wait for requests coming over the indicated port. Any commands that follow the `.run_as_server(...)` line will not be executed as a result of this. To close the server, you can press `CTRL+C` in the terminal you are running it in.

Step 2: Setting up the client
-----------------------------
To use the client, it needs to know where the server is located (its IP-address) and over which channel to communicate with it (its PORT). These values should match the values set within the server (see above). These variables (and any other code below) needs to be put in a seperate, new, file.::

    IP = "localhost"
    PORT = 31415

The client class (called `PhenoAIClient` is implemented in the client module of the PhenoAI package. It is basically a light-weight PhenoAI class that outsources any form of computation and due to the lack of heavy dependencies it is very fast to import in your workflow scripts.::

    from phenoai.client import PhenoAIClient
    client = PhenoAIClient(IP, PORT)

Step 3: Using the client
------------------------
Using the client you just set up as as easy as asking it for a prediction:::

    import numpy as np
    X = np.random.rand(5,3)
    results = client.predict(data=X, map_data=False, data_ids=['a','b','c','e','d'])

Help! It does not work for me!
------------------------------
Did you check the following:
- The server script should be running when the client queries for a prediction.
- Do the servers allow for HTTP communication between them? (i.e. is there a too restrictive firewall?)