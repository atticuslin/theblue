./start_neo4j.sh
gunicorn api:app --chdir ../api &
