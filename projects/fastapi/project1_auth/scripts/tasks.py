import logging
from datetime import datetime, timezone

from repository import RefreshTokenRepository

logger = logging.getLogger(__name__)


def cleanup_expired_refresh_tokens(token_repository: RefreshTokenRepository):
    try:
        deleted_count = token_repository.delete_expired()
        logger.info(f"Cleaned up {deleted_count} expired refresh tokens at {datetime.now(timezone.utc)}")
    except Exception as e:
        logger.error(f"Failed to cleanup expired tokens: {e}")
