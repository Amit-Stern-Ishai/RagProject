This is a recipe helper rag project that allows the user to request recipes or any kind of query regarding recipes. 

To run from pycharm:
1. Configure aws cli
2. run app.py

To run the docker image:
1. Configure aws cli
2. Install docker
3. docker pull amitishai/flask-docker-app:0.0.3
4. docker run -it   -p 80:8000   -e GOOGLE_API_KEY="api token"   -v ~/.aws:/root/.aws   -v $(pwd)/data:/app/data   amitishai/flask-docker-app:0.0.3
