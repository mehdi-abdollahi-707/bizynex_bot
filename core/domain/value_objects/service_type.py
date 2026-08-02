"""The six services Bizynex sells, with their canonical Persian labels.

This is the single source of truth for service identity: the Django model
field (`apps.requests.models.SERVICE_TYPE_CHOICES`) builds its `choices=`
list from this enum instead of duplicating the Persian labels, so adding a
7th service later only means adding one member here.
"""

from __future__ import annotations

from enum import StrEnum


class ServiceType(StrEnum):
    WORDPRESS_WEBSITE = "wordpress_website"
    CUSTOM_WEBSITE = "custom_website"
    TELEGRAM_BOT = "telegram_bot"
    N8N_AUTOMATION = "n8n_automation"
    POSTER_DESIGN = "poster_design"
    THUMBNAIL_COVER_DESIGN = "thumbnail_cover_design"

    @property
    def label_fa(self) -> str:
        return _LABELS_FA[self]


_LABELS_FA: dict[ServiceType, str] = {
    ServiceType.WORDPRESS_WEBSITE: "طراحی سایت وردپرسی",
    ServiceType.CUSTOM_WEBSITE: "طراحی سایت اختصاصی",
    ServiceType.TELEGRAM_BOT: "ساخت ربات تلگرام",
    ServiceType.N8N_AUTOMATION: "اتوماسیون با n8n",
    ServiceType.POSTER_DESIGN: "طراحی پوستر",
    ServiceType.THUMBNAIL_COVER_DESIGN: "طراحی تامنیل یوتیوب و کاور اینستاگرام",
}
