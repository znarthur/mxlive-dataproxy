MxLIVE Data Proxy
=================

The MxLIVE data proxy is a tool to provide secure access to users' data and results through MxLIVE.

The main features are:
- Maps files paths with secure keys so that MxLIVE does not know where files are stored.
- Provides files and archives to MxLIVE so that MxLIVE does not need direct access to any file storage systems.
- No accessible interface to the web; only able to be accessed directly from MxLIVE.

Deploying for Development
=========================

To deploy the test environment do the following:
------------------------------------------------
1. Copy settings_local.py.example in the "local/" folder to settings_local.py and customize it according to your environment.
   * Note: if you plan to run with Docker and a database other than postgresql, be sure to modify the imports 
     in the Dockerfile (eg. for MySQL, you will need to add python-mysql)
2. Run ./manage.py migrate
3. Run ./manage.py runserver 0:8080
4. Update your MxLIVE settings_local.py "IMAGE_PREPEND" setting to point to http://localhost:8080.

To add mxlive-dataproxy to your full MxLIVE docker deployment:
--------------------------------------------------------------
1. Build the docker image with the command: 

        sudo docker build --rm -t mxlive-dataproxy:latest .

2. In the top-level of your mxlive docker deployment directory, place your settings_local.py file in data-local/.
   * Create a logs/ directory in data-local/, if it does not already exist.

3. In the top-level of your mxlive docker deployment directory, customize the dataproxy section in docker-compose.yml:
   * Be sure to include volumes pointing to the data directories your dataproxy will need access to.
   * If using an external database, delete the database link within the dataproxy section.
   
4. Restart your MxLIVE deployment for the changes to take effect.

        sudo docker-compose down
        sudo docker-compose up -d