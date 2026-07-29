ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "church_owner": frozenset(
        {"church:read", "church:configure", "users:invite", "users:block", "roles:assign"}
    ),
    "church_admin": frozenset(
        {"church:read", "church:configure", "users:invite", "users:block", "roles:assign"}
    ),
    "pastor": frozenset(
        {"church:read", "users:invite", "users:block", "members:read", "members:approve"}
    ),
    "secretary": frozenset({"church:read", "users:invite", "members:read", "members:approve"}),
    "treasurer": frozenset({"church:read", "finance:read", "finance:create"}),
    "leader": frozenset({"church:read"}),
    "member": frozenset({"church:read"}),
}
