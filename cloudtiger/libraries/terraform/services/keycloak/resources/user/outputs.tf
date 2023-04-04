output keycloak_user {
  value       = keycloak_user.user_with_initial_password
  sensitive   = true
  description = "description"
  depends_on  = []
}