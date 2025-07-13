NAME = transcendence

YAML = ./srcs/docker-compose.yaml

DEVYAML = ./srcs/docker-dev-compose.yaml

$(NAME): build start

transcendence-logs: build start-logs

build:
	@docker-compose -f $(YAML) build

start:
	@docker-compose -f $(YAML) up --detach

start-logs:
	@docker-compose -f $(YAML) up

stop:
	-@docker-compose -f $(YAML) stop

dev-build:
	@docker-compose -f $(DEVYAML) build

dev-start:
	@docker-compose -f $(DEVYAML) up --detach

dev-start-logs:
	@docker-compose -f $(DEVYAML) up

dev-stop:
	-@docker-compose -f $(DEVYAML) stop

restart : stop start

dev-restart : dev-stop dev-start

remove: dev-stop stop
	-@rm -f srcs/services/django/transcendence/media/profile_pic/*

	-@docker rm	django \
				nginx \
				postgres \
				redis \
				elasticsearch \
				kibana \
				logstash \

	-@docker rmi srcs_django \
				srcs_nginx \
				srcs_postgres \
				srcs_redis \
				elasticsearch:8.15.5 \
				kibana:8.15.5 \
				logstash:8.15.5 \

	-@docker volume rm	srcs_static_files \
						srcs_media_files \

	-@docker network rm	srcs_transcendence

remove-all: stop dev-stop
	@echo "Do you really want to delete all your system stopped dockers and all your images ? [y/n]"
	@read -r response; \
	if [ "$$response" = "y" ]; then \
		docker system prune -af ; \
	elif [ "$$response" = "n" ]; then \
		echo "Aborting..." ; \
		exit; \
	else \
		echo "Invalid input. Please enter 'y' or 'n'"; \
		exit; \
	fi

logs:
	@docker-compose -f $(YAML) logs

dev-logs:
	@docker-compose -f $(DEVYAML) logs

docker-list:
	@docker ps -a

docker-image:
	@docker images

re: remove $(NAME)

help:
	@echo "Here's all the avalible make commands:\n\n" \
	"- transcendence: Default rule to build and start the project.\n" \
	"- transcendence-logs: Build and start the containers with real-time logs displayed in your terminal. Press Ctrl + C to stop the project.\n" \
	"- build: Simply builds the project.\n" \
	"- start: Simply starts the project.\n" \
	"- start-logs: Simply starts the project with real-time logs displayed in your terminal. Press Ctrl + C to stop the project.\n" \
	"- stop: Simply stops the project.\n" \
	"- restart: Simply stops and start the project.\n" \
	"- remove: Stops the project and deletes all previously built images.\n" \
	"- remove-all: Stops the project and deletes every images, containers or networks.\n" \
	"- logs: Prints all the logs from the project.\n" \
	"- docker-list: Prints all Docker images found on the system (not only from the project).\n" \
	"- re: Stops the project, removes it, rebuilds it, and starts it again.\n" \
