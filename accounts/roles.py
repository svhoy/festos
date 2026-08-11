from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    SPIESS = "spiess"
    OBERLEUTNANT = "oberleutnant"
    LEUTNANT = "leutnant"
    SCHUETZE = "schuetze"


ROLE_LABELS = {
    Role.ADMIN: "Admin",
    Role.SPIESS: "Spieß",
    Role.OBERLEUTNANT: "Oberleutnant",
    Role.LEUTNANT: "Leutnant",
    Role.SCHUETZE: "Schütze",
}
