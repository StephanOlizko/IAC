# Counter: IaC lab

Счётчик нажатий: `frontend` (nginx) → `backend` (FastAPI + SQLAlchemy) → `db` (MySQL).

```
app/        приложение, Dockerfile для каждого компонента, compose.yml для локального запуска
ansible/    inventory, роли (docker, app_build, app_deploy) и плейбуки
```

## Локальный запуск

```bash
cd app
cp .env.example .env
docker compose up --build
```

## Деплой

Образы собираются локально, на сервер доставляются архивы образов, где их загружают и запускают через Docker Compose.
Тег образа — короткий хеш текущего git-коммита.

```bash
cd ansible
ansible-galaxy collection install -r requirements.yml
echo "vIhNR7XfgEd0GOHnFD+CcOcbZ8/7yy0CiEfrA4qUdB8=" > .vault_pass

ansible-playbook playbooks/docker.yml      # установить Docker на сервер
ansible-playbook playbooks/build.yml -K    # собрать и экспортировать образы локально
ansible-playbook playbooks/deploy.yml      # доставить образы и запустить приложение
# или всё сразу:
ansible-playbook playbooks/site.yml -K
```

Приложение: http://olizkostepan.shitstudent.com/counter/ (через nginx на сервере, контейнер слушает 127.0.0.1:8088)

Секреты лежат в `inventories/production/group_vars/app_servers/vault.yml` (Ansible Vault):

```bash
ansible-vault edit inventories/production/group_vars/app_servers/vault.yml
```
