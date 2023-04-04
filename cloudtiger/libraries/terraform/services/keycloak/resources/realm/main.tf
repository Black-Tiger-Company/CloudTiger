terraform {
  required_providers {
    keycloak = {
      source = "mrparkers/keycloak"
      version = "4.2.0"
    }
  }
}

resource "keycloak_realm" "realm" {
  realm             = var.realm_config.name
  enabled           = true
  display_name      = var.realm_config.name
  display_name_html = "<b>my realm</b>"

  login_theme = "base"

  access_code_lifespan = "1h"

  ssl_required    = "external"
  password_policy = "upperCase(1) and length(8) and forceExpiredPasswordChange(365) and notUsername"
  # attributes      = {
  #   mycustomAttribute = "myCustomValue"
  # }

  # The smtp_server block can be used to configure the realm's SMTP settings, which can be found in the "Email" tab in the GUI. This block supports the following arguments:
  # smtp_server {
  #   host = "smtp.example.com"
  #   from = "example@example.com"

  #   auth {
  #     username = "tom"
  #     password = "password"
  #   }
  # }

  # internationalization {
  #   supported_locales = [
  #     "en",
  #     "de",
  #     "es"
  #   ]
  #   default_locale    = "en"
  # }

  # security_defenses {
  #   headers {
  #     x_frame_options                     = "DENY"
  #     content_security_policy             = "frame-src 'self'; frame-ancestors 'self'; object-src 'none';"
  #     content_security_policy_report_only = ""
  #     x_content_type_options              = "nosniff"
  #     x_robots_tag                        = "none"
  #     x_xss_protection                    = "1; mode=block"
  #     strict_transport_security           = "max-age=31536000; includeSubDomains"
  #   }
  #   brute_force_detection {
  #     permanent_lockout                 = false
  #     max_login_failures                = 30
  #     wait_increment_seconds            = 60
  #     quick_login_check_milli_seconds   = 1000
  #     minimum_quick_login_wait_seconds  = 60
  #     max_failure_wait_seconds          = 900
  #     failure_reset_time_seconds        = 43200
  #   }
  # }

  # web_authn_policy {
  #   relying_party_entity_name = "Example"
  #   relying_party_id          = "keycloak.example.com"
  #   signature_algorithms      = ["ES256", "RS256"]
  # }
}