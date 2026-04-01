import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from .coordinator import TempoSensorCoordinator
from .entity import TempoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tempo Fit sensors."""
    coordinator = config_entry.runtime_data
    async_add_entities(
        TempoSensorEntity(coordinator, exercise)
        for exercise in coordinator.data["me"]
    )
    async_add_entities(
        [
            # All-time stats
            TempoSensorAllTimeWorkoutCount(coordinator),
            TempoSensorAllTimeWeightLifted(coordinator),
            TempoSensorAllTimeCaloriedBurned(coordinator),
            TempoSensorAllTimeActiveMinutes(coordinator),
            # Weekly stats
            TempoSensorWeeklyWorkoutCount(coordinator),
            TempoSensorWeeklyWeightLifted(coordinator),
            TempoSensorWeeklyCaloriesBurned(coordinator),
            TempoSensorWeeklyActiveMinutes(coordinator),
            # Streak
            TempoSensorStreak(coordinator),
            # Account
            TempoSensorSubscriptionType(coordinator),
        ]
    )


class TempoSensorEntity(TempoEntity, SensorEntity):
    """Representation of a Roborock sensor."""

    def __init__(
        self,
        coordinator: TempoSensorCoordinator,
        exercise: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(
            f"{exercise}_{coordinator.id}",
            coordinator,
        )
        self._name = f"{exercise} Weight"
        self._exercise = exercise

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current weight."""
        if self.coordinator.data:
            return self.coordinator.data["me"].get(self._exercise)
        return None


class TempoSensorAllTimeWorkoutCount(TempoEntity, SensorEntity):
    """Representation of a Roborock sensor."""

    def __init__(
        self,
        coordinator: TempoSensorCoordinator,
    ) -> None:
        """Initialize the entity."""
        self._name = f"All Workout Count"
        super().__init__(
            f"{self._name}_{coordinator.id}",
            coordinator,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current weight."""
        if self.coordinator.data:
            return self.coordinator.data["all_time"].numWorkouts
        return None


class TempoSensorAllTimeWeightLifted(TempoEntity, SensorEntity):
    """Representation of a Roborock sensor."""

    def __init__(
        self,
        coordinator: TempoSensorCoordinator,
    ) -> None:
        """Initialize the entity."""
        self._name = f"All Weighted Lifted"
        super().__init__(
            f"{self._name}_{coordinator.id}",
            coordinator,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current weight."""
        if self.coordinator.data:
            return self.coordinator.data["all_time"].weightLifted
        return None


class TempoSensorAllTimeCaloriedBurned(TempoEntity, SensorEntity):
    """Representation of a Roborock sensor."""

    def __init__(
        self,
        coordinator: TempoSensorCoordinator,
    ) -> None:
        """Initialize the entity."""
        self._name = f"All calories burned"

        super().__init__(
            f"{self._name}_{coordinator.id}",
            coordinator,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current weight."""
        if self.coordinator.data:
            return self.coordinator.data["all_time"].caloriesBurned
        return None


class TempoSensorAllTimeActiveMinutes(TempoEntity, SensorEntity):
    """All-time active minutes."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "All Active Minutes"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["all_time"].activeMinutes
        return None


# --- Weekly sensors ---

class TempoSensorWeeklyWorkoutCount(TempoEntity, SensorEntity):
    """Weekly workout count."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "Weekly Workout Count"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["weekly"].numWorkouts
        return None


class TempoSensorWeeklyWeightLifted(TempoEntity, SensorEntity):
    """Weekly weight lifted (lbs)."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "Weekly Weight Lifted"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["weekly"].weightLifted
        return None


class TempoSensorWeeklyCaloriesBurned(TempoEntity, SensorEntity):
    """Weekly calories burned."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "Weekly Calories Burned"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["weekly"].caloriesBurned
        return None


class TempoSensorWeeklyActiveMinutes(TempoEntity, SensorEntity):
    """Weekly active minutes."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "Weekly Active Minutes"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["weekly"].activeMinutes
        return None


# --- Streak ---

class TempoSensorStreak(TempoEntity, SensorEntity):
    """Current workout streak (consecutive weeks with activity)."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "Workout Streak"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["streak"]
        return None


# --- Account ---

class TempoSensorSubscriptionType(TempoEntity, SensorEntity):
    """Current subscription type (e.g. studio, digital)."""

    def __init__(self, coordinator: TempoSensorCoordinator) -> None:
        self._name = "Subscription Type"
        super().__init__(f"{self._name}_{coordinator.id}", coordinator)

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data["profile"].subscription_type
        return None
