import logging
from .server import mcp
from .utils import (
    get_statute_detail_internal,
    get_statute_article_internal,
    get_precedent_detail_internal,
    get_admin_rule_detail_internal,
    get_legal_term_detail_internal,
    get_statutory_interpretation_detail_internal
)

logger = logging.getLogger("korean-law-mcp")

@mcp.resource("law://statute/{id}")
def read_statute_resource(id: str) -> str:
    """Read full text of a statute (Law)"""
    logger.info(f"Reading statute resource: {id}")
    return get_statute_detail_internal(id)

@mcp.resource("law://statute/{id}/art/{art_no}")
def read_statute_article_resource(id: str, art_no: str) -> str:
    """Read a specific article from a statute"""
    logger.info(f"Reading statute article: {id} Art {art_no}")
    return get_statute_article_internal(id, art_no)

@mcp.resource("law://prec/{id}")
def read_precedent_resource(id: str) -> str:
    """Read content of a precedent (Case Law)"""
    logger.info(f"Reading precedent resource: {id}")
    return get_precedent_detail_internal(id)

@mcp.resource("law://admrul/{id}")
def read_admrul_resource(id: str) -> str:
    """Read content of an administrative rule"""
    logger.info(f"Reading admin rule resource: {id}")
    return get_admin_rule_detail_internal(id)

@mcp.resource("law://term/{id}")
def read_legal_term_resource(id: str) -> str:
    """Read definition of a legal term"""
    logger.info(f"Reading legal term resource: {id}")
    return get_legal_term_detail_internal(id)

@mcp.resource("law://interp/{id}")
def read_interp_resource(id: str) -> str:
    """Read content of a statutory interpretation"""
    logger.info(f"Reading statutory interpretation resource: {id}")
    return get_statutory_interpretation_detail_internal(id)
