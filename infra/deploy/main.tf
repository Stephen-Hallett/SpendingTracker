data "azurerm_client_config" "current" {}

data "azurerm_subscription" "primary" {}

data "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_id}-${var.env}-eau-001"
}

resource "azurerm_storage_account" "sa" {
  name                     = "sa${var.env}eau001"
  resource_group_name      = data.azurerm_resource_group.rg.name
  location                 = data.azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_service_plan" "asp" {
  name                = "asp-${var.project_id}-${var.env}-eau-001"
  location            = data.azurerm_resource_group.location
  resource_group_name = data.azurerm_resource_group.rg.name
  os_type               = "Linux"
  sku_name            = var.sku
}

resource "azurerm_linux_function_app" "fa" {
  name                       = "fa-${var.project_id}-${var.env}-eau-001"
  location                   = azurerm_service_plan.asp.rg.location
  resource_group_name        = data.azurerm_resource_group.rg.name
  service_plan_id            = azurerm_service_plan.asp.id
  storage_account_name       = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key

  site_config {
    cors {
      allowed_origins = ["*"]
    }
    application_stack {
      python_version = "3.9"
    }
  }

}