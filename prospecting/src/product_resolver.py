"""
Product Resolver - Maps legacy product tokens to internal product IDs

Provides backward compatibility for existing configs that use:
- qx, mx, px, ax, rx (legacy tokens)
- quality, manufacturing, process, asset, regulatory (display names)

All internal code should use:
- quality_qms, manufacturing_mes, process_validation, asset_excellence, regulatory_submissions

Usage:
    from product_resolver import ProductResolver

    resolver = ProductResolver(rules_config)
    internal_id = resolver.resolve("qx")  # Returns "quality_qms"
    display_name = resolver.get_display_name("quality_qms")  # Returns "Quality Excellence (Qx)"
"""

from typing import Dict, List, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)


# Hardcoded fallback mapping (used if YAML not loaded)
DEFAULT_ALIAS_MAP = {
    "qx": "quality_qms",
    "mx": "manufacturing_mes",
    "px": "process_validation",
    "ax": "asset_excellence",
    "rx": "regulatory_submissions",
    "quality": "quality_qms",
    "manufacturing": "manufacturing_mes",
    "process": "process_validation",
    "asset": "asset_excellence",
    "assets": "asset_excellence",
    "regulatory": "regulatory_submissions",
}

# Valid internal product IDs
VALID_PRODUCT_IDS = {
    "quality_qms",
    "manufacturing_mes",
    "process_validation",
    "asset_excellence",
    "regulatory_submissions",
}


class ProductResolver:
    """
    Resolves legacy product tokens to internal product IDs.

    Maintains backward compatibility while enforcing consistent
    internal product identification.
    """

    def __init__(self, rules_config: Optional[Dict[str, Any]] = None):
        """
        Initialize resolver with rules configuration.

        Args:
            rules_config: Loaded rules configuration dict, or None for defaults
        """
        self.rules_config = rules_config or {}
        self._alias_map = self._build_alias_map()
        self._products = self._load_products()

    def _build_alias_map(self) -> Dict[str, str]:
        """Build alias map from config or use defaults."""
        # Start with hardcoded defaults
        alias_map = DEFAULT_ALIAS_MAP.copy()

        # Override with config if available
        config_map = self.rules_config.get('product_alias_map', {})
        if config_map:
            alias_map.update(config_map)

        # Also add aliases from product definitions
        products = self.rules_config.get('products', {})
        for product_id, product_config in products.items():
            # The key itself should map to product_id
            alias_map[product_id] = product_config.get('product_id', product_id)

            # Add explicit aliases
            for alias in product_config.get('aliases', []):
                alias_map[alias.lower()] = product_config.get('product_id', product_id)

        return alias_map

    def _load_products(self) -> Dict[str, Dict[str, Any]]:
        """Load product definitions from config."""
        products = {}
        config_products = self.rules_config.get('products', {})

        for key, config in config_products.items():
            product_id = config.get('product_id', key)
            products[product_id] = config

        return products

    def resolve(self, token: str) -> str:
        """
        Resolve a product token to internal product ID.

        Args:
            token: Legacy token (qx, mx, etc.) or internal ID

        Returns:
            Internal product ID (quality_qms, manufacturing_mes, etc.)

        Raises:
            ValueError: If token cannot be resolved
        """
        if not token:
            raise ValueError("Empty product token")

        token_lower = token.lower().strip()

        # Already an internal ID?
        if token_lower in VALID_PRODUCT_IDS:
            return token_lower

        # Check alias map
        if token_lower in self._alias_map:
            return self._alias_map[token_lower]

        # Unknown token
        raise ValueError(
            f"Unknown product token '{token}'. Valid tokens: "
            f"{list(self._alias_map.keys())} or {list(VALID_PRODUCT_IDS)}"
        )

    def resolve_list(self, tokens: List[str]) -> List[str]:
        """
        Resolve a list of product tokens to internal IDs.

        Args:
            tokens: List of legacy tokens or internal IDs

        Returns:
            List of internal product IDs (deduplicated, order preserved)
        """
        if not tokens:
            return []

        resolved = []
        seen = set()

        for token in tokens:
            try:
                internal_id = self.resolve(token)
                if internal_id not in seen:
                    resolved.append(internal_id)
                    seen.add(internal_id)
            except ValueError as e:
                logger.warning(f"Skipping invalid token: {e}")

        return resolved

    def is_valid_product(self, token: str) -> bool:
        """Check if token can be resolved to a valid product ID."""
        try:
            self.resolve(token)
            return True
        except ValueError:
            return False

    def get_display_name(self, product_id: str) -> str:
        """
        Get display name for a product.

        Args:
            product_id: Internal product ID

        Returns:
            Display name (e.g., "Quality Excellence (Qx)")
        """
        # Resolve first in case it's a legacy token
        try:
            internal_id = self.resolve(product_id)
        except ValueError:
            return product_id

        product = self._products.get(internal_id, {})
        return product.get('display_name', internal_id)

    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """
        Get full product configuration.

        Args:
            product_id: Product ID (legacy or internal)

        Returns:
            Product configuration dict
        """
        try:
            internal_id = self.resolve(product_id)
        except ValueError:
            return {}

        return self._products.get(internal_id, {})

    def get_forbidden_phrases(self, product_id: str) -> List[str]:
        """
        Get forbidden phrases for a product.

        These are multi-word phrases that uniquely identify the product
        and should trigger forbidden product validation.

        Args:
            product_id: Product ID (legacy or internal)

        Returns:
            List of forbidden phrases
        """
        info = self.get_product_info(product_id)
        return info.get('forbidden_phrases', [])

    def get_unique_identifiers(self, product_id: str) -> List[str]:
        """
        Get unique identifiers for a product.

        These are high-confidence terms that uniquely identify the product.

        Args:
            product_id: Product ID (legacy or internal)

        Returns:
            List of unique identifiers
        """
        info = self.get_product_info(product_id)
        return info.get('unique_identifiers', [])

    def get_all_product_ids(self) -> List[str]:
        """Get all valid internal product IDs."""
        return list(VALID_PRODUCT_IDS)

    def get_legacy_tokens(self) -> Dict[str, str]:
        """Get mapping of legacy tokens to internal IDs."""
        return self._alias_map.copy()


def resolve_product(token: str, rules_config: Optional[Dict] = None) -> str:
    """
    Convenience function to resolve a single product token.

    Args:
        token: Legacy token or internal ID
        rules_config: Optional rules configuration

    Returns:
        Internal product ID
    """
    resolver = ProductResolver(rules_config)
    return resolver.resolve(token)


def resolve_products(tokens: List[str], rules_config: Optional[Dict] = None) -> List[str]:
    """
    Convenience function to resolve a list of product tokens.

    Args:
        tokens: List of legacy tokens or internal IDs
        rules_config: Optional rules configuration

    Returns:
        List of internal product IDs
    """
    resolver = ProductResolver(rules_config)
    return resolver.resolve_list(tokens)
