Creating demo platforms using docker-compose
============================================

Sending applications to production is an area where our team could be greatly improved. 
Without getting into details on how we will be doing this in the near future, I would like people to start
thinking about production the moment they start working on a minimal piece of code.

No matter what is the scope of the demo, the experiment, or the toy library, this code may eventually be used
by real clients who will further design their systems based on this code.

With this project I would like to give you the opportunity to spin up a dockerised environment with as less 
effort as possible while thinking the integration of your applications in the meantime.


Python application
------------------

This simple application consists of a "hello world" type python flask application, which is configured using
an environment variable and a nginx frontend which acts as a proxy to the backend applications.

The python application has just one route, which renders whatever is configured in the environment variable.

.. code-block: python

    @app.route('/')
    def app_root():
        return os.environ.get('APP_NAME', 'no app name')

Important points for this code-block:
* Using the same codebase, allows us to use the same container, in order to server different results. Reusability!
* The environment variable may be set and may be not. Always default your input to a desired state. Never truth the user input! 
Allow the application to be usable even when the desired state is not there!

Navigate to the flask_app folder and build the container.

.. code-block: console

    cd flask_app && docker build -t app:latest .

Important points for this code-block:
* name your images with lower case string only names with no spaces or dashes. docker image names may end us to a url somewhere and we would
like to keep the naming convention
* always add the latest tag unless you release
* access the Dockerfile and make sure you understand the instructions. We would like the image to be as small as possible. A developer must 
be contious of the size of the image. Images must be small most of the times, unless there is a specific reason why it should be 1.5GBs

Nginx web server
----------------

Nginx can be used as a "frontend" to our backend applications. The docker image generated is pretty minimal, just a small alpine base image
with a custom configuration copied in.

There are two ways to forward requests to the application. Using url paths or subdomain. Both of the approaches are demonstrated. If youa
are not sure which one to pick go for the subdomains.

.. code-block: console

    server {
        listen 80;

        server_name all.apps.local

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        location /app1 {
            proxy_pass http://app1:5000/;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }    

.. code-block: console

    server {
        listen 80;

        server_name app1.apps.local;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        location / {
            proxy_pass http://app1:5000/;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

Important points for this code-block:
* For the urls to work you need to add the following entry to your /etc/hosts or c:\Windows\System32\Drivers\etc\hosts 
`127.0.0.1 app1.apps.local app2.apps.local app3.apps.local all.apps.local`. This mimicks the actual DNS entries a live environment
will have in the future. Will be good if you design this demo deployment with actual values like `ui.project-name.local` and `algorithm.project-name.local`
* The flask1:5000 is a name configured in the docker-compose project. It is adviced to use real application names here as well.
* The above configuration makes the app1 available in both app1.apps.local and all.apps.local/app1

Docker-compose project
----------------------

The docker-compose.yaml file brings all the applications together. 

.. code-block: yaml

    version: '3'
    services:
    app1:
        restart: always
        image: app:latest
        expose:
        - "5000"
        environment:
            APP_NAME: "application 1"
    app2:
        restart: always
        image: app:latest
        expose:
        - "5000"
        environment:
            APP_NAME: "application 2"

    nginx:
        restart: always
        image: my-nginx:latest
        ports:
        - 80:80
        links:
        - app1:app1
        - app2:app2

Important points for this code-block:
* We create two backend application using the same codebase and the same container. Response is configure using an environment variable
* Nginx is linked with the two application and this is mapped to the config file we created above. 
* We could dynamically generate the nginx.conf out of this yaml file. But I would like people to get used into configuring this. It will be
handled automatically for you, but you need have to be aware how your code works on production in case you need to debug it.

After all this all you need to do is edit the hosts file and do a `docker-compose up -d`, verify the containers are running with
`docker ps` and access the urls using your browser.

Enjoy
Argiris