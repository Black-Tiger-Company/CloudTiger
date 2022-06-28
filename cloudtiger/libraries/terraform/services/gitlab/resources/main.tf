resource "gitlab_user" "users" {
  count            = len(var.gitlab_config.users)
  name             = var.gitlab_config.privileges[count.index].name
  username         = var.gitlab_config.privileges[count.index].username
  password         = var.gitlab_config.privileges[count.index].password
  email            = var.gitlab_config.privileges[count.index].email
  is_admin         = var.gitlab_config.privileges[count.index].is_admin
  projects_limit   = var.gitlab_config.privileges[count.index].projects_limit
  can_create_group = var.gitlab_config.privileges[count.index].can_create_group
  is_external      = var.gitlab_config.privileges[count.index].is_external
  reset_password   = var.gitlab_config.privileges[count.index].reset_password
}

resource "gitlab_project" "projects" {
  count            = len(var.gitlab_config.users)
  name             = var.gitlab_config.privileges[count.index].name
  username         = var.gitlab_config.privileges[count.index].username
  password         = var.gitlab_config.privileges[count.index].password
  email            = var.gitlab_config.privileges[count.index].email
  is_admin         = var.gitlab_config.privileges[count.index].is_admin
  projects_limit   = var.gitlab_config.privileges[count.index].projects_limit
  can_create_group = var.gitlab_config.privileges[count.index].can_create_group
  is_external      = var.gitlab_config.privileges[count.index].is_external
  reset_password   = var.gitlab_config.privileges[count.index].reset_password
}