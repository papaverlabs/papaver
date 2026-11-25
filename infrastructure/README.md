# Infrastruktura

Wdrożenie zakłada Kubernetes z Knative ([architektura](../docs/architecture/architektura.md)). Na razie pusto; pierwsze pliki powstaną razem z wdrożeniem labelera.

Planowany układ:

```
infrastructure/
├── helm/           chart instalujący komplet (serwisy Knative, triggery, zadania cykliczne, Keycloak, RabbitMQ);
│                   PostgreSQL i S3 są dostarczane z zewnątrz
└── k3d/            lokalny klaster testowy: k3d z Knative, PostgreSQL i MinIO jako zamienniki
```

Terraform dołożymy, gdy pojawi się środowisko utrzymywane w chmurze. Konwencja nazw plików Terraform: `{typ}-{komponent}.tf`.
