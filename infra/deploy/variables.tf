# App service plan
variable "tier" {
  type = string
}

variable "sku" {
  type = string
}

# Function app
variable always_on {
  type = bool
}

#AZURE VARIABLES
variable "subscription_id" {
  type = string
}

variable "client_id" {
  type = string
}

variable "client_secret" {
  type = string
}

variable "tenant_id" {
  type = string
}


#COMMON VARIABLES
variable "project_id" {
  type = string
}

variable "env" {
  type = string
}