OPENAPI_DOCUMENT = {
    "openapi": "3.0.3",
    "info": {
        "title": "Custom API Authentication Demo",
        "version": "1.0.0",
        "description": (
            "Demo API with both custom header authentication and standard "
            "JWT bearer authentication."
        ),
    },
    "servers": [
        {"url": "http://api.adn.f5demo.io", "description": "Published API endpoint"},
        {"url": "http://localhost:8080", "description": "Local Docker Compose"},
    ],
    "tags": [
        {"name": "Customers"},
        {"name": "Orders"},
        {"name": "Invoices"},
        {"name": "Payments"},
        {"name": "Sessions"},
        {"name": "Reports"},
        {"name": "Security"},
        {"name": "Health"},
    ],
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check",
                "security": [],
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Health"}
                            }
                        },
                    }
                },
            }
        },
        "/api/v1/customers": {
            "get": {
                "tags": ["Customers"],
                "summary": "List customers",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "schema": {"type": "string", "example": "active"},
                    },
                    {
                        "name": "region",
                        "in": "query",
                        "schema": {"type": "string", "example": "emea"},
                    },
                ],
                "responses": {
                    "200": {"$ref": "#/components/responses/CustomerListResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            }
        },
        "/api/v1/customers/{customerId}": {
            "get": {
                "tags": ["Customers"],
                "summary": "Get customer",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [
                    {"$ref": "#/components/parameters/CustomerId"},
                ],
                "responses": {
                    "200": {"$ref": "#/components/responses/CustomerResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                    "404": {"$ref": "#/components/responses/NotFoundError"},
                },
            }
        },
        "/api/v1/customers/{customerId}/orders": {
            "get": {
                "tags": ["Customers", "Orders"],
                "summary": "List customer orders",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [
                    {"$ref": "#/components/parameters/CustomerId"},
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {"type": "integer", "example": 10},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Customer orders",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "customerId": {"type": "string"},
                                        "orders": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Order"},
                                        },
                                        "count": {"type": "integer"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            }
        },
        "/api/v1/orders": {
            "post": {
                "tags": ["Orders"],
                "summary": "Create order",
                "security": [{"CustomHeaderAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateOrderRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"$ref": "#/components/responses/OrderResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            }
        },
        "/api/v1/orders/{orderId}": {
            "get": {
                "tags": ["Orders"],
                "summary": "Get order",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [{"$ref": "#/components/parameters/OrderId"}],
                "responses": {
                    "200": {"$ref": "#/components/responses/OrderResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                    "404": {"$ref": "#/components/responses/NotFoundError"},
                },
            },
            "put": {
                "tags": ["Orders"],
                "summary": "Update order",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [{"$ref": "#/components/parameters/OrderId"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UpdateOrderRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"$ref": "#/components/responses/OrderResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            },
        },
        "/api/v1/invoices": {
            "get": {
                "tags": ["Invoices"],
                "summary": "List invoices",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [
                    {"$ref": "#/components/parameters/CustomerIdQuery"},
                    {
                        "name": "status",
                        "in": "query",
                        "schema": {"type": "string", "example": "open"},
                    },
                ],
                "responses": {
                    "200": {"$ref": "#/components/responses/InvoiceListResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            }
        },
        "/api/v1/payments": {
            "post": {
                "tags": ["Payments"],
                "summary": "Create payment",
                "security": [{"CustomHeaderAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreatePaymentRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"$ref": "#/components/responses/PaymentResponse"},
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            }
        },
        "/api/v1/sessions/{sessionId}": {
            "delete": {
                "tags": ["Sessions"],
                "summary": "Revoke session",
                "security": [{"CustomHeaderAuth": []}],
                "parameters": [{"$ref": "#/components/parameters/SessionId"}],
                "responses": {
                    "200": {
                        "description": "Session revoked",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "sessionId": {"type": "string"},
                                        "status": {"type": "string", "example": "revoked"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/CustomAuthError"},
                },
            }
        },
        "/api/v1/reports/sales-summary": {
            "get": {
                "tags": ["Reports"],
                "summary": "Get sales summary report",
                "security": [{"JwtBearerAuth": []}],
                "parameters": [
                    {
                        "name": "period",
                        "in": "query",
                        "schema": {"type": "string", "example": "last-30-days"},
                    }
                ],
                "responses": {
                    "200": {"$ref": "#/components/responses/SalesSummaryResponse"},
                    "401": {"$ref": "#/components/responses/JwtAuthError"},
                },
            }
        },
        "/api/v1/security/audit-events": {
            "get": {
                "tags": ["Security"],
                "summary": "List security audit events",
                "security": [{"JwtBearerAuth": []}],
                "parameters": [
                    {
                        "name": "severity",
                        "in": "query",
                        "schema": {"type": "string", "example": "high"},
                    }
                ],
                "responses": {
                    "200": {"$ref": "#/components/responses/AuditEventsResponse"},
                    "401": {"$ref": "#/components/responses/JwtAuthError"},
                },
            }
        },
    },
    "components": {
        "securitySchemes": {
            "CustomHeaderAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Demo-Authenticated",
                "description": "Non-standard custom header authentication.",
            },
            "JwtBearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Standard JWT bearer authentication.",
            },
        },
        "parameters": {
            "CustomerId": {
                "name": "customerId",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "example": "cust-1001"},
            },
            "CustomerIdQuery": {
                "name": "customerId",
                "in": "query",
                "schema": {"type": "string", "example": "cust-1001"},
            },
            "OrderId": {
                "name": "orderId",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "example": "ord-7001"},
            },
            "SessionId": {
                "name": "sessionId",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "example": "sess-abc123"},
            },
        },
        "responses": {
            "CustomerListResponse": {
                "description": "Customer list",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "customers": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Customer"},
                                },
                                "count": {"type": "integer"},
                            },
                        }
                    }
                },
            },
            "CustomerResponse": {
                "description": "Customer details",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "customer": {"$ref": "#/components/schemas/Customer"}
                            },
                        }
                    }
                },
            },
            "OrderResponse": {
                "description": "Order details",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"order": {"$ref": "#/components/schemas/Order"}},
                        }
                    }
                },
            },
            "InvoiceListResponse": {
                "description": "Invoice list",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "invoices": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Invoice"},
                                },
                                "count": {"type": "integer"},
                            },
                        }
                    }
                },
            },
            "PaymentResponse": {
                "description": "Payment created",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "payment": {"$ref": "#/components/schemas/Payment"}
                            },
                        }
                    }
                },
            },
            "SalesSummaryResponse": {
                "description": "Sales summary report",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/SalesSummary"}
                    }
                },
            },
            "AuditEventsResponse": {
                "description": "Audit events",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "events": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/AuditEvent"},
                                },
                                "count": {"type": "integer"},
                            },
                        }
                    }
                },
            },
            "CustomAuthError": {
                "description": "Custom header authentication failed",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                },
            },
            "JwtAuthError": {
                "description": "JWT bearer authentication failed",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                },
            },
            "NotFoundError": {
                "description": "Resource was not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                },
            },
        },
        "schemas": {
            "Health": {
                "type": "object",
                "properties": {"status": {"type": "string", "example": "ok"}},
            },
            "Customer": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "cust-1001"},
                    "name": {"type": "string", "example": "Acme Manufacturing"},
                    "status": {"type": "string", "example": "active"},
                    "region": {"type": "string", "example": "emea"},
                },
            },
            "Order": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "ord-7001"},
                    "customerId": {"type": "string", "example": "cust-1001"},
                    "status": {"type": "string", "example": "shipped"},
                    "total": {"type": "number", "format": "float", "example": 245.9},
                },
            },
            "Invoice": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "inv-3001"},
                    "customerId": {"type": "string", "example": "cust-1001"},
                    "status": {"type": "string", "example": "open"},
                    "amount": {"type": "number", "format": "float", "example": 245.9},
                },
            },
            "Payment": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "pay-9001"},
                    "invoiceId": {"type": "string", "example": "inv-3001"},
                    "amount": {"type": "number", "format": "float", "example": 245.9},
                    "status": {"type": "string", "example": "authorized"},
                },
            },
            "CreateOrderRequest": {
                "type": "object",
                "required": ["customerId", "items"],
                "properties": {
                    "customerId": {"type": "string", "example": "cust-1001"},
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/OrderItem"},
                    },
                },
            },
            "UpdateOrderRequest": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "processing"},
                    "shippingAddress": {
                        "type": "object",
                        "properties": {
                            "line1": {"type": "string", "example": "100 Market Street"},
                            "city": {"type": "string", "example": "London"},
                            "country": {"type": "string", "example": "GB"},
                        },
                    },
                },
            },
            "OrderItem": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "example": "router-100"},
                    "quantity": {"type": "integer", "example": 2},
                },
            },
            "CreatePaymentRequest": {
                "type": "object",
                "required": ["invoiceId", "amount"],
                "properties": {
                    "invoiceId": {"type": "string", "example": "inv-3001"},
                    "amount": {"type": "number", "format": "float", "example": 245.9},
                    "currency": {"type": "string", "example": "USD"},
                },
            },
            "SalesSummary": {
                "type": "object",
                "properties": {
                    "report": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "example": "sales-summary"},
                            "period": {"type": "string", "example": "last-30-days"},
                            "currency": {"type": "string", "example": "USD"},
                            "grossRevenue": {
                                "type": "number",
                                "format": "float",
                                "example": 1634.4,
                            },
                            "paidInvoices": {"type": "integer", "example": 1},
                            "openInvoices": {"type": "integer", "example": 2},
                        },
                    }
                },
            },
            "AuditEvent": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "evt-5001"},
                    "severity": {"type": "string", "example": "high"},
                    "action": {"type": "string", "example": "payment.authorized"},
                    "actor": {"type": "string", "example": "user-demo-1"},
                },
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "expectedHeader": {"type": "string"},
                },
            },
        },
    },
}
