"""Item system for loading and managing items from YAML."""

from pathlib import Path

from ruamel.yaml import YAML

from .models import ItemDefinition


class ItemManager:
    """Manages items loaded from YAML configuration."""

    def __init__(self, items_file: Path | None = None):
        if items_file is None:
            # Default to the data/items.yaml in the package
            items_file = Path(__file__).parent.parent / "data" / "items.yaml"

        self.items_file = Path(items_file)
        self.items: dict[str, dict[str, ItemDefinition]] = {}
        self._load_items()

    def _load_items(self) -> None:
        """Load items from YAML file."""
        try:
            yaml = YAML(typ="safe")

            if not self.items_file.exists():
                print(f"Warning: Items file not found at {self.items_file}")
                self._create_default_items()
                return

            with open(self.items_file, encoding="utf-8") as f:
                data = yaml.load(f)

            if not data:
                print("Warning: Empty items file, using defaults")
                self._create_default_items()
                return

            # Parse items by category
            for category, items_data in data.items():
                self.items[category] = {}
                for item_id, item_data in items_data.items():
                    try:
                        self.items[category][item_id] = ItemDefinition(**item_data)
                    except Exception as e:
                        print(f"Error loading item {category}.{item_id}: {e}")

            print(
                f"Loaded {sum(len(cat) for cat in self.items.values())} items from {self.items_file}"
            )

        except Exception as e:
            print(f"Error loading items file: {e}")
            self._create_default_items()

    def _create_default_items(self) -> None:
        """Create default items if YAML file is missing or invalid."""
        self.items = {
            "food": {
                "kibble": ItemDefinition(
                    name="Kibble",
                    description="Basic pet food",
                    effects={"hunger": 15, "affection": 2},
                    cooldown_s=300,
                ),
                "premium_food": ItemDefinition(
                    name="Premium Food",
                    description="High quality pet food",
                    effects={"hunger": 25, "happiness": 5, "affection": 5},
                    cooldown_s=600,
                ),
            },
            "cleaning": {
                "soap": ItemDefinition(
                    name="Soap",
                    description="Basic cleaning soap",
                    effects={"hygiene": 20, "affection": 1},
                    cooldown_s=600,
                ),
                "shampoo": ItemDefinition(
                    name="Shampoo",
                    description="Premium pet shampoo",
                    effects={"hygiene": 35, "happiness": 3, "affection": 3},
                    cooldown_s=900,
                ),
            },
            "toys": {
                "ball": ItemDefinition(
                    name="Ball",
                    description="A simple bouncy ball",
                    effects={"happiness": 15, "energy": -5, "affection": 3},
                    cooldown_s=300,
                ),
                "puzzle": ItemDefinition(
                    name="Puzzle Toy",
                    description="Mental stimulation toy",
                    effects={"happiness": 20, "mood": 10, "energy": -3, "affection": 5},
                    cooldown_s=900,
                ),
            },
        }

    def get_item(self, category: str, item_id: str) -> ItemDefinition | None:
        """Get a specific item by category and ID."""
        return self.items.get(category, {}).get(item_id)

    def get_category_items(self, category: str) -> dict[str, ItemDefinition]:
        """Get all items in a category."""
        return self.items.get(category, {})

    def get_all_items(self) -> dict[str, dict[str, ItemDefinition]]:
        """Get all items organized by category."""
        return self.items

    def list_items_by_category(self, category: str) -> list[str]:
        """Get a list of item names in a category."""
        return list(self.items.get(category, {}).keys())

    def search_items(self, search_term: str) -> dict[str, dict[str, ItemDefinition]]:
        """Search for items by name or description."""
        results = {}
        search_lower = search_term.lower()

        for category, items in self.items.items():
            category_results = {}
            for item_id, item in items.items():
                if (
                    search_lower in item.name.lower()
                    or search_lower in item.description.lower()
                    or search_lower in item_id.lower()
                ):
                    category_results[item_id] = item

            if category_results:
                results[category] = category_results

        return results

    def get_item_info(self, category: str, item_id: str) -> str | None:
        """Get formatted information about an item."""
        item = self.get_item(category, item_id)
        if not item:
            return None

        info_lines = [
            f"**{item.name}**",
            f"Description: {item.description}",
            f"Cooldown: {item.cooldown_s}s",
        ]

        if item.effects:
            effects_list = []
            for stat, value in item.effects.items():
                sign = "+" if value > 0 else ""
                effects_list.append(f"{stat} {sign}{value}")
            info_lines.append(f"Effects: {', '.join(effects_list)}")

        return "\n".join(info_lines)

    def validate_items(self) -> list[str]:
        """Validate all items and return list of issues found."""
        issues = []

        for category, items in self.items.items():
            for item_id, item in items.items():
                try:
                    # Validate required fields
                    if not item.name.strip():
                        issues.append(f"{category}.{item_id}: Empty name")

                    if not item.description.strip():
                        issues.append(f"{category}.{item_id}: Empty description")

                    if item.cooldown_s < 0:
                        issues.append(f"{category}.{item_id}: Negative cooldown")

                    # Validate effect values
                    for stat, value in item.effects.items():
                        if not isinstance(value, (int, float)):
                            issues.append(f"{category}.{item_id}: Invalid effect value for {stat}")

                except Exception as e:
                    issues.append(f"{category}.{item_id}: Validation error: {e}")

        return issues

    def reload_items(self) -> bool:
        """Reload items from the YAML file."""
        try:
            self._load_items()
            return True
        except Exception as e:
            print(f"Failed to reload items: {e}")
            return False

    def save_items_to_file(self, file_path: Path | None = None) -> bool:
        """Save current items to a YAML file."""
        if file_path is None:
            file_path = self.items_file

        try:
            yaml = YAML()
            yaml.default_flow_style = False

            # Convert items to serializable format
            data = {}
            for category, items in self.items.items():
                data[category] = {}
                for item_id, item in items.items():
                    data[category][item_id] = item.model_dump()

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f)

            print(f"Items saved to {file_path}")
            return True

        except Exception as e:
            print(f"Failed to save items: {e}")
            return False

    def add_item(self, category: str, item_id: str, item: ItemDefinition) -> bool:
        """Add a new item to the collection."""
        try:
            if category not in self.items:
                self.items[category] = {}

            self.items[category][item_id] = item
            return True

        except Exception as e:
            print(f"Failed to add item: {e}")
            return False

    def remove_item(self, category: str, item_id: str) -> bool:
        """Remove an item from the collection."""
        try:
            if category in self.items and item_id in self.items[category]:
                del self.items[category][item_id]
                # Remove empty categories
                if not self.items[category]:
                    del self.items[category]
                return True
            return False

        except Exception as e:
            print(f"Failed to remove item: {e}")
            return False
